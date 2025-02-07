from pathlib import Path
from typing import Any
import typer
from cuddly_dicts import kdl_source_to_dict

from zed_hct_theme_maker.models import Color, Highlight, PlayerColor, Theme, Variant

from coloraide import Color as Base
from coloraide.spaces.hct import HCT
from textwrap import indent

from json import dumps
import re

class HCTColor(Base): ...

HCTColor.register(HCT())

cli = typer.Typer()

def recurse_resolve_colors(color: Color, env: dict[str, Color], what: str, resolve_chain: list[str]) -> Color:
    if what in resolve_chain:
        raise Exception(f"{what} references {', which references '.join(resolve_chain)}")
    
    if color.apply is None:
        return color
    
    h, c, t, a = None, None, None, None
    
    for apply in color.apply.split(" "):
        if env.get(apply) is None:
            raise Exception(f"{what} references {color.apply}, which does not exist")
        
        resolved = recurse_resolve_colors(
            env[apply],
            env,
            apply,
            [what, *resolve_chain]
        )
        
        h = h if resolved.h is None else resolved.h
        c = c if resolved.c is None else resolved.c
        t = t if resolved.t is None else resolved.t
        a = a if resolved.a is None else resolved.a
    
    h = h if color.h is None else color.h
    c = c if color.c is None else color.c
    t = t if color.t is None else color.t
    a = t if color.a is None else color.a
    
    return Color(
        h=h,
        c=c,
        t=t,
        a=a
    )

def color_to_hex(color: Color | None, env: dict[str, Color], name: str) -> str | None:
    if color is None:
        return None
    
    resolved = recurse_resolve_colors(
        color,
        env,
        name,
        list()
    )
    
    return HCTColor('hct', (resolved.h, resolved.c, resolved.t), alpha=resolved.a or 1) \
        .convert('srgb') \
        .to_string(hex=True)

def compile_highlight(highlight: Highlight | Color, env: dict[str, Color], name: str) -> dict[str, Any]:
    if isinstance(highlight, Color):
        return {
            "background_color": None,
            "color": color_to_hex(highlight, env, name),
            "font_style": None,
            "font_weight": None
        }
    else:
        return {
            "background_color": color_to_hex(highlight.background_color, env, name),
            "color": color_to_hex(highlight.color, env, name),
            "font_style": highlight.font_style,
            "font_weight": highlight.font_weight
        }

def compile_variant(theme: Theme, variant: Variant, name: str):
    accents = variant.accent
    if isinstance(accents, Color):
        accents = [accents]
    
    players = variant.player
    if isinstance(players, PlayerColor):
        players = [players]
    
    layers = variant.layer
    if isinstance(layers, str):
        layers = [layers]

    env = theme.token.copy()
    out = dict()
    syntax = dict()
    for layer in variant.layer:
        env.update(theme.layer[layer].token)
        out.update(theme.layer[layer].style)
        syntax.update(theme.layer[layer].syntax)
        
        accent = theme.layer[layer].accent
        if isinstance(accent, Color):
            accent = [accent]
        accents.extend(accent)
        
        player = theme.layer[layer].player
        if isinstance(player, PlayerColor):
            player = [player]
        players.extend(player)
    
    out.update(variant.style)
    syntax.update(variant.syntax)
    
    resolved_out = dict()
    
    for key, color in out.items():
        resolved_out[key] = color_to_hex(
            color,
            env,
            key
        )
    
    resolved_out["accents"] = [
        color_to_hex(
            color,
            env,
            "accent"
        )
        for color in accents
    ]
    
    resolved_out["players"] = [
        {
            "background": color_to_hex(
                player.background,
                env,
                "player background"
            ),
            "cursor": color_to_hex(
                player.cursor,
                env,
                "color background"
            ),
            "selection": color_to_hex(
                player.selection,
                env,
                "selection background"
            ),
        } for player in players
    ]
    
    resolved_out["syntax"] = {
        key: compile_highlight(
            highlight,
            env,
            key
        ) for key, highlight in syntax.items()
    }
    
    return {
        "name": name,
        "appearance": variant.appearance,
        "style": resolved_out
    }

@cli.command()
def compile(
    file: Path
):
    with open(file) as fd:
        kdl = kdl_source_to_dict(fd.read())
        theme = Theme(**kdl)
    
    themes = [compile_variant(
        theme,
        variant,
        name
    ) for name, variant in theme.variant.items()]
    
    final_theme = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": theme.name,
        "author": theme.author,
        "themes": themes
    }
    
    print(dumps(final_theme, indent=2))

@cli.command()
def experimental_patch_settings(
    file: Path,
    settings_path: Path,
    variant: str,
):
    with open(file) as fd:
        kdl = kdl_source_to_dict(fd.read())
        theme = Theme(**kdl)
    
    variant = compile_variant(
        theme,
        theme.variant[variant],
        variant
    )
    
    overrides = variant["style"]
    override_json = dumps(overrides, indent=2)
    override_json = indent(override_json, '  ').lstrip()
    
    with open(settings_path, "r+") as fd:
        data = fd.read()
        fd.seek(0)
        r = re.compile(
            r'"experimental\.theme_overrides":\s+({(\s+"\w+":\s+{(\s+"[\w.]+":\s+{[^}]*},?)*[^}]*}|\s+"\w+":\s+\[[^\]]+\]|[^}])*})',
            re.MULTILINE | re.VERBOSE
        )
        match = r.search(data)
        
        assert match, "couldn't find experimental.theme_overrides key"
        
        span = match.span(1)
        assert span
        
        fd.write(
            f'{data[:span[0]]}{override_json}{data[span[1]:]}'
        )
        fd.truncate()
        
if __name__ == "__main__":
    cli()