from colorsys import rgb_to_hsv
from typing import Tuple


def color_8bit_to_float(color_8bit: Tuple[int, ...]) -> Tuple[float, ...]:
    return tuple(x / 255 for x in color_8bit)


def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    r, g, b = (round(x * 255) for x in rgb)
    return f'#{r:02x}{g:02x}{b:02x}'


def hex_to_rgb(h: str) -> Tuple[float, ...]:
    return tuple(int(h[i : i + 2], 16) / 255 for i in (1, 3, 5))


def hex_to_h(h: str) -> float:
    rgb = hex_to_rgb(h)
    hsv = rgb_to_hsv(*rgb)
    return hsv[0]
