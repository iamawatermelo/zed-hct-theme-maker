from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field


class Color(BaseModel):
    h: Optional[int] = None
    c: Optional[int] = None
    t: Optional[int] = None
    a: Optional[float] = None
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
    accent: Color | list[Color] = []
    player: PlayerColor | list[PlayerColor] = []
    syntax: dict[str, Color | Highlight] = dict()


class Layer(BaseModel):
    token: dict[str, Color] = dict()
    style: dict[str, Color] = dict()
    accent: Color | list[Color] = []
    player: PlayerColor | list[PlayerColor] = []
    syntax: dict[str, Color | Highlight] = dict()


class Module(BaseModel):
    version: Literal[1]
    include: Annotated[list[str] | str | None, Field(alias="@include")] = None
    token: dict[str, Color] = dict()
    layer: dict[str, Layer] = dict()


class Theme(BaseModel):
    version: Literal[1]
    name: str
    author: str
    include: Annotated[list[str] | str | None, Field(alias="@include")] = None
    variant: dict[str, Variant] = dict()
    token: dict[str, Color] = dict()
    layer: dict[str, Layer] = dict()