import re

import aqt

from . import parser


class SyntaxHighlighter(aqt.qt.QSyntaxHighlighter):
    def __init__(self, is_dark_mode: bool, colors: dict, parent: aqt.qt.QTextDocument):
        super().__init__(parent)

        default_color = "white" if is_dark_mode else "black"

        #

        color_light = colors.get("font-light", None)
        color_dark = colors.get("font-dark", None)
        color = color_dark if is_dark_mode else color_light

        accent_color_light = colors.get("font-light-accent", None)
        accent_color_dark = colors.get("font-dark-accent", None)
        accent_color = accent_color_dark if is_dark_mode else accent_color_light

        #

        # Create color, format and regex for `mustache` syntax: `{{Field}}`.
        mustache_color = parser.QQColor(
            color=accent_color, default=default_color
        ).parse()
        mustache_format = aqt.qt.QTextCharFormat()
        mustache_format.setForeground(mustache_color)
        mustache_expression = r"{{2}[^{}]*?}{2}"
        mustache_re_expression = re.compile(mustache_expression)

        # Create color, format and regex for `whitespace` characters.
        whitespace_color = parser.QQColor(color=color, default=default_color).parse()
        whitespace_color.setAlpha(32)
        whitespace_format = aqt.qt.QTextCharFormat()
        whitespace_format.setForeground(whitespace_color)
        whitespace_expression = r"(\t|[ ]{2,})"
        whitespace_re_expression = re.compile(whitespace_expression)

        # Create color, format and regex for `transparent` characters.
        transparent_color = aqt.qt.QColor(0, 0, 0, 0)
        transparent_format = aqt.qt.QTextCharFormat()
        transparent_format.setForeground(transparent_color)
        transparent_expression = r"(?<! ) (?! )"
        transparent_re_expression = re.compile(transparent_expression)

        """ Single `space` characters are *not* highlighted. Therefore it's
        important that `highlightBlock` formats the text in a strict order.
        First, all `mustache` syntax are set to the `mustache` format. Then all
        `tabs` and greater than two consecutive `whitespace` characters are set
        to the `whitespace` format. Finally, all `space` characters are set to
        the `transparent` format. """
        self._expressions = {
            mustache_re_expression: mustache_format,
            whitespace_re_expression: whitespace_format,
            transparent_re_expression: transparent_format,
        }

    def highlightBlock(self, text: str):

        # See `SyntaxHighlighter.__init__()`.
        for expression, format_ in self._expressions.items():
            for match in expression.finditer(text):

                match_start = match.start()
                match_end = match.end()
                match_count = match_end - match_start

                self.setFormat(match_start, match_count, format_)
