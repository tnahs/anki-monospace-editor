import json
import pathlib
from typing import Optional

import aqt
import aqt.clayout

from . import errors, highlighter


class AnkiMonospaceEditor:

    name = "AnkiMonospaceEditor"

    main_root = pathlib.Path(__file__).parent.parent
    user_root = main_root / "user_files"
    config_path = main_root / "config.json"

    _card_layout: Optional[aqt.clayout.CardLayout] = None
    _edit_area: Optional[aqt.qt.QTextEdit] = None

    _highlighter_html: Optional[highlighter.HighlighterHTML] = None
    _highlighter_css: Optional[highlighter.HighlighterCSS] = None

    def __init__(self) -> None:

        self._load_config()

    def _load_config(self) -> None:

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise errors.ConfigError("Missing `config.json`.")
        except json.JSONDecodeError:
            raise errors.ConfigError("Cannot read `config.json`.")

        self._config = config

    @property
    def _font_family(self) -> str:
        return self._config.get("font-family", "Courier")

    @property
    def _font_size(self) -> int:
        return self._config.get("font-size", "12pt")

    @property
    def _colors(self) -> dict:
        return self._config.get("colors", {})

    @property
    def _font_color(self) -> Optional[str]:
        return (
            self._colors.get("font-dark", None)
            if self._is_dark_mode
            else self._colors.get("font-light", None)
        )

    @property
    def _is_dark_mode(self) -> bool:
        return (
            aqt.theme.theme_manager.night_mode
            or aqt.theme.theme_manager.macos_dark_mode()
        )

    @property
    def _show_whitespace(self) -> str:
        return self._config.get("show-whitespace", True)

    @property
    def _stylesheet(self) -> str:

        if self._font_color is None:
            return f"""
                font-family: {self._font_family};
                font-size: {self._font_size};
            """

        return f"""
            font-family: {self._font_family};
            font-size: {self._font_size};
            color: {self._font_color};
        """

    def _callback__set_highlighter_html(self) -> None:
        self._edit_area.highlighter = self._highlighter_html

    def _callback__set_highlighter_css(self) -> None:
        self._edit_area.highlighter = self._highlighter_css

    def setup(self) -> None:
        def hook__customize_layout(clayout: aqt.clayout.CardLayout) -> None:

            # Bind layout to
            if self._card_layout is None or self._edit_area is None:
                self._card_layout = clayout
                self._edit_area = clayout.tform.edit_area

            # Create syntax highlighters.
            if self._highlighter_html is None or self._highlighter_css is None:

                self._highlighter_html = highlighter.HighlighterHTML(
                    is_dark_mode=self._is_dark_mode,
                    colors=self._colors,
                    parent=self._edit_area.document(),
                )

                self._highlighter_css = highlighter.HighlighterCSS(
                    is_dark_mode=self._is_dark_mode,
                    colors=self._colors,
                    parent=self._edit_area.document(),
                )

            # Set text editor styling.
            self._edit_area.setStyleSheet(self._stylesheet)

            tab_width = self._edit_area.fontMetrics().width(" " * 4)
            self._edit_area.setTabStopDistance(tab_width)

            if self._show_whitespace:

                text_option = self._edit_area.document().defaultTextOption()
                text_option.setFlags(
                    text_option.flags() | aqt.qt.QTextOption.ShowTabsAndSpaces
                )
                self._edit_area.document().setDefaultTextOption(text_option)

            # Set initial syntax highlighter.

            if self._card_layout.tform.front_button.isChecked():
                self._callback__set_highlighter_html()
            elif self._card_layout.tform.back_button.isChecked():
                self._callback__set_highlighter_html()
            elif self._card_layout.tform.style_button.isChecked():
                self._callback__set_highlighter_css()
            else:
                pass

            # Connect radio-buttons to set syntax highlighters on click.

            aqt.qt.qconnect(
                self._card_layout.tform.front_button.clicked,
                self._callback__set_highlighter_html,
            )
            aqt.qt.qconnect(
                self._card_layout.tform.back_button.clicked,
                self._callback__set_highlighter_html,
            )
            aqt.qt.qconnect(
                self._card_layout.tform.style_button.clicked,
                self._callback__set_highlighter_css,
            )

        aqt.gui_hooks.card_layout_will_show.append(hook__customize_layout)
