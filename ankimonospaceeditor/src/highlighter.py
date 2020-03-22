import re

import aqt


class WhitespaceHighlighter(aqt.qt.QSyntaxHighlighter):
    def __init__(self, is_dark_mode: bool, parent: aqt.qt.QTextDocument):
        super().__init__(parent)

        # Whitespace is always rendered as semi-transparent text over the
        # background of the current text editor. A contrasting color is chosen
        # based on the current theme Anki is running.
        color = "white" if is_dark_mode else "black"

        # Create color, format and regex for `transparent` characters.
        transparent_color = aqt.qt.QColor(0, 0, 0, 0)
        transparent_format = aqt.qt.QTextCharFormat()
        transparent_format.setForeground(transparent_color)
        transparent_expression = r"[ ]"
        transparent_re_expression = re.compile(transparent_expression)

        # Create color, format and regex for `highlight` characters.
        highlight_color = aqt.qt.QColor(color)
        highlight_color.setAlpha(32)
        highlight_format = aqt.qt.QTextCharFormat()
        highlight_format.setForeground(highlight_color)
        highlight_expression = r"(\t|[ ]{2,})"
        highlight_re_expression = re.compile(highlight_expression)

        # Single `space` characters are *not* highlight. Therefore it's
        # important that `highlightBlock` highlights the text in a strict
        # order. First, all `space` characters are set to the `transparent`
        # format. Then all `tabs` and greater than two consecutive `space`
        # characters are set to the `highlighed` format.
        self._expressions = {
            transparent_re_expression: transparent_format,
            highlight_re_expression: highlight_format,
        }

    def highlightBlock(self, text: str):

        # See `WhitespaceHighlighter.__init__()`.
        for expression, format_ in self._expressions.items():
            for match in expression.finditer(text):

                match_start = match.start()
                match_end = match.end()
                match_count = match_end - match_start

                self.setFormat(match_start, match_count, format_)
