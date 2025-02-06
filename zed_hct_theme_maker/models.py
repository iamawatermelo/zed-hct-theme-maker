from typing import Literal, Optional
from pydantic import BaseModel


class Color(BaseModel):
    _resolved: bool = False
    h: Optional[int] = None
    c: Optional[int] = None
    t: Optional[int] = None
    a: float = 1
    apply: Optional[str] = None


class PlayerColor(BaseModel):
    background: Optional[Color] = None
    cursor: Optional[Color] = None
    selection: Optional[Color] = None


class Highlight(BaseModel):
    background_color: Optional[Color] = None
    color: Optional[Color] = None
    font_style: Optional[str] = None
    font_weight: Optional[int] = None


class Variant(BaseModel):
    appearance: str 
    layer: str | list[str]
    style: dict[str, Color] = dict()
    accent: list[Color] = []
    player: list[PlayerColor] = []
    syntax: dict[str, Color | Highlight] = dict()


class Layer(BaseModel):
    token: dict[str, Color] = dict()
    style: dict[str, Color] = dict()
    accent: Color | list[Color] = []
    player: PlayerColor | list[PlayerColor] = []
    syntax: dict[str, Color | Highlight] = dict()


class Theme(BaseModel):
    version: Literal[1]
    name: str
    author: str
    variant: dict[str, Variant]
    token: dict[str, Color]
    layer: dict[str, Layer]