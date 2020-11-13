import re

import aqt

from . import parser


class HighlighterBase(aqt.qt.QSyntaxHighlighter):

    _color_parser = parser.QQColor()

    def __init__(self, is_dark_mode: bool, colors: dict, parent: aqt.qt.QTextDocument):
        super().__init__(parent)

        self._expressions = []

        self._default_color = "white" if is_dark_mode else "black"

        #

        color_light = colors.get("font-light", None)
        color_dark = colors.get("font-dark", None)
        self._color = color_dark if is_dark_mode else color_light

        accent_color_light = colors.get("font-light-accent", None)
        accent_color_dark = colors.get("font-dark-accent", None)
        self._accent_color = accent_color_dark if is_dark_mode else accent_color_light

        #

        # Create color, format and regex for `whitespace` characters.
        whitespace_color = self._color_parser.parse(
            color=self._color, default_color=self._default_color
        )
        whitespace_color.setAlpha(32)
        whitespace_format = aqt.qt.QTextCharFormat()
        whitespace_format.setForeground(whitespace_color)
        whitespace_regex = re.compile(r"(\t|[ ]{2,})")

        # Create color, format and regex for `transparent` characters.
        transparent_color = aqt.qt.QColor(0, 0, 0, 0)
        transparent_format = aqt.qt.QTextCharFormat()
        transparent_format.setForeground(transparent_color)
        transparent_regex = re.compile(r"(?<! ) (?! )")

        """ Single `space` characters are *not* highlighted. Therefore it's
        important that `highlightBlock` formats the text in a strict order.
        First, all `mustache` syntax are set to the `mustache` format. Then all
        `tabs` and greater than two consecutive `whitespace` characters are set
        to the `whitespace` format. Finally, all `space` characters are set to
        the `transparent` format. """
        self.register_expression(regex=whitespace_regex, fmt=whitespace_format)
        self.register_expression(regex=transparent_regex, fmt=transparent_format)

    def register_expression(
        self, regex: re.Pattern, fmt: aqt.qt.QTextCharFormat, index: int = 0
    ) -> None:
        # fmt:off
        self._expressions.insert(
            index,
            {
                "regex": regex,
                "fmt": fmt,
            }
        )
        # fmt:on

    def highlightBlock(self, text: str):

        # See `HighlighterBase.__init__()`.
        for item in self._expressions:

            regex = item.get("regex", None)
            fmt = item.get("fmt", None)

            if regex is None or fmt is None:
                continue

            for match in regex.finditer(text):

                match_start = match.start()
                match_end = match.end()
                match_count = match_end - match_start

                self.setFormat(match_start, match_count, fmt)


class HighlighterHTML(HighlighterBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create color, format and regex for `mustache` syntax: `{{Field}}`.
        mustache_color = self._color_parser.parse(
            color=self._accent_color, default_color=self._default_color
        )
        mustache_format = aqt.qt.QTextCharFormat()
        mustache_format.setForeground(mustache_color)
        mustache_regex = re.compile(r"\{{2}[^{}]*?\}{2}")

        self.register_expression(regex=mustache_regex, fmt=mustache_format)


class HighlighterCSS(HighlighterBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
