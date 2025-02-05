from pathlib import Path
import typer
from cuddly_dicts import kdl_source_to_dict

from zed_hct_theme_maker.models import Color, Theme, Variant

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
    
    if color._resolved:
        return color
    
    color._resolved = True
    
    if color.apply is None:
        return color
    
    apply_from = env.get(color.apply)
    
    if apply_from is None:
        raise Exception(f"{what} references {color.apply}, which does not exist")
    
    apply_from = recurse_resolve_colors(
        apply_from,
        env,
        color.apply,
        [what, *resolve_chain]
    )
    
    color.h = apply_from.h if color.h is None else color.h
    color.c = apply_from.c if color.c is None else color.c
    color.t = apply_from.t if color.t is None else color.t
    
    return color

def compile_variant(theme: Theme, variant: Variant, name: str):
    if isinstance(variant.layer, str):
        env = {
            **theme.token,
            **theme.layer[variant.layer].token
        }
    else:
        env = theme.token.copy()
        
        for theme in variant.layer:
            env.update(theme.layer[variant.layer])
    
    out = dict()
    
    for key, color in variant.style.items():
        out[key] = recurse_resolve_colors(
            color,
            env,
            key,
            list()
        )
    
    out_colors = {
        key: HCTColor('hct', (color.h, color.c, color.t)).convert('srgb').to_string(hex=True)
        for key, color in out.items()
    }
    
    return {
        "name": name,
        "appearance": variant.appearance,
        "style": out_colors
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
    override_json = indent(override_json, '  ')
    
    with open(settings_path, "r+") as fd:
        data = fd.read()
        fd.seek(0)
        r = re.compile(
            r'"experimental\.theme_overrides":\s+({[^}]*})',
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