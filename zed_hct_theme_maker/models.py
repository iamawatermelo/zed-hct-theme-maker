from typing import Literal, Optional
from pydantic import BaseModel


class Color(BaseModel):
    _resolved: bool = False
    h: Optional[int] = None
    c: Optional[int] = None
    t: Optional[int] = None
    apply: Optional[str] = None


class Variant(BaseModel):
    appearance: str
    layer: str | list[str]
    style: dict[str, Color]


class Layer(BaseModel):
    token: dict[str, Color]


class Theme(BaseModel):
    version: Literal[1]
    name: str
    author: str
    variant: dict[str, Variant]
    token: dict[str, Color]
    layer: dict[str, Layer]