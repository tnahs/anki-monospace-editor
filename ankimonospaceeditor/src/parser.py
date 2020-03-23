import re
from typing import Any, Optional

import aqt

from .helpers import css_color_names


class QQColor:

    regex_word = re.compile(r"\w+")

    regex_hsl = re.compile(
        r"""
        hsl\(
        (\d{1,3}),[ ]?
        (\d{1,3})%,[ ]?
        (\d{1,3})%
        \)
    """,
        flags=re.VERBOSE,
    )

    regex_hsla = re.compile(
        r"""
        hsla\(
        (\d{1,3}),[ ]?
        (\d{1,3})%,[ ]?
        (\d{1,3})%,[ ]?
        (\d?\.\d{1,2})
        \)
    """,
        flags=re.VERBOSE,
    )

    # rgb(255, 255, 255)
    regex_rgb = re.compile(
        r"""
        rgb\(
        (\d{1,3}),[ ]?
        (\d{1,3}),[ ]?
        (\d{1,3})
        \)
    """,
        flags=re.VERBOSE,
    )

    # rgba(255, 255, 255, 1.0)
    regex_rgba = re.compile(
        r"""
        rgba\(
        (\d{1,3}),[ ]?
        (\d{1,3}),[ ]?
        (\d{1,3}),[ ]?
        (\d?\.\d{1,2})
        \)
    """,
        flags=re.VERBOSE,
    )

    def __init__(self, color: Optional[str], default: str) -> None:

        self._color = color
        self._default = default

    def parse(self) -> aqt.qt.QColor:

        if not self._color:

            obj = self._dispatch_parser(self._default)

        else:

            obj = self._dispatch_parser(self._color)

            if obj is None:
                aqt.utils.showInfo(
                    f"AnkiMonospaceEditor: Error parsing color `{self._color}` "
                    f"in `config.json`."
                )
                obj = self._dispatch_parser(self._default)

        return obj

    def _dispatch_parser(self, string) -> Optional[aqt.qt.QColor]:

        if self.regex_word.fullmatch(string):
            return self._color_from_css_name(string)

        elif string.startswith("#"):
            return self._color_from_hex(string)

        elif string.startswith("hsla"):
            return self._color_from_hsla(string)

        elif string.startswith("hsl"):
            return self._color_from_hsl(string)

        elif string.startswith("rgb"):
            return self._color_from_rgb(string)

        elif string.startswith("rgba"):
            return self._color_from_rgba(string)

        return None

    def _color_from_hsl(self, string: str) -> aqt.qt.QColor:

        match = self.regex_hsl.fullmatch(string)

        if not match:
            return None

        hue = int(match.group(1)) / 360
        saturation = int(match.group(2)) / 100
        lightness = int(match.group(3)) / 100
        alpha = 1.0

        return aqt.qt.QColor.fromHslF(hue, saturation, lightness, alpha)

    def _color_from_hsla(self, string: str) -> aqt.qt.QColor:

        match = self.regex_hsla.fullmatch(string)

        if not match:
            return None

        hue = int(match.group(1)) / 360
        saturation = int(match.group(2)) / 100
        lightness = int(match.group(3)) / 100
        alpha = float(match.group(4))

        return aqt.qt.QColor.fromHslF(hue, saturation, lightness, alpha)

    def _color_from_rgb(self, string: str) -> aqt.qt.QColor:

        match = self.regex_rgb.fullmatch(string)

        if not match:
            return None

        red = int(match.group(1)) / 255
        green = int(match.group(2)) / 255
        blue = int(match.group(3)) / 255
        alpha = 1.0

        return aqt.qt.QColor.fromRgbF(red, green, blue, alpha)

    def _color_from_rgba(self, string: str) -> aqt.qt.QColor:

        match = self.regex_rgba.fullmatch(string)

        if not match:
            return None

        red = int(match.group(1)) / 255
        green = int(match.group(2)) / 255
        blue = int(match.group(3)) / 255
        alpha = float(match.group(4))

        return aqt.qt.QColor.fromRgbF(red, green, blue, alpha)

    def _color_from_hex(self, string: str) -> aqt.qt.QColor:

        if len(string) != 7:
            return None

        string = string.lower()

        return aqt.qt.QColor(string)

    def _color_from_css_name(self, string: str) -> aqt.qt.QColor:

        string = string.lower()

        try:
            hex_color = css_color_names[string]
        except KeyError:
            return None

        return aqt.qt.QColor(hex_color)
