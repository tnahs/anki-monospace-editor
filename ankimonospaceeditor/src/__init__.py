import json
import pathlib
from typing import List

import aqt
import aqt.clayout

from . import errors, highlighter


class AnkiMonospaceEditor:

    name = "AnkiMonospaceEditor"

    main_root = pathlib.Path(__file__).parent.parent
    user_root = main_root / "user_files"
    config_path = main_root / "config.json"

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
    def _font_color_light(self) -> str:
        return self._config.get("font-color-light", None)

    @property
    def _font_color_dark(self) -> str:
        return self._config.get("font-color-dark", None)

    @property
    def _font_color(self) -> str:
        return self._font_color_dark if self._is_dark_mode else self._font_color_light

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

    def setup(self) -> None:
        def hook__customize_layout(clayout: aqt.clayout.CardLayout) -> None:

            widgets: List[aqt.qt.QTextEdit] = [
                clayout.tform.front,
                clayout.tform.back,
                clayout.tform.css,
            ]

            for widget in widgets:

                widget.setStyleSheet(self._stylesheet)

                if self._show_whitespace:

                    text_option = widget.document().defaultTextOption()
                    text_option.setFlags(
                        text_option.flags() | aqt.qt.QTextOption.ShowTabsAndSpaces
                    )
                    widget.document().setDefaultTextOption(text_option)

                    widget.whitespace_highlighter = highlighter.WhitespaceHighlighter(
                        is_dark_mode=self._is_dark_mode, parent=widget.document()
                    )

        aqt.gui_hooks.card_layout_will_show.append(hook__customize_layout)
