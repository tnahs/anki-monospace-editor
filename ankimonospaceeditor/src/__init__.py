import json
import pathlib
from typing import List

import aqt

from . import errors


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
    def _is_darkmode(self) -> bool:
        return (
            aqt.theme.theme_manager.night_mode
            or aqt.theme.theme_manager.macos_dark_mode()
        )

    @property
    def _stylesheet(self) -> str:

        font_color = (
            self._font_color_dark if self._is_darkmode else self._font_color_light
        )

        if font_color is None:
            return f"""
                font-family: {self._font_family};
                font-size: {self._font_size};
            """

        return f"""
            font-family: {self._font_family};
            font-size: {self._font_size};
            color: {font_color};
        """

    def setup(self) -> None:
        def hook__customize_layout(clayout) -> None:
            # (aqt.clayout.CardLayout)

            layouts: List[aqt.at.QTextEdit] = [
                clayout.tform.front,
                clayout.tform.back,
                clayout.tform.css,
            ]

            for layout in layouts:
                layout.setStyleSheet(self._stylesheet)

        aqt.gui_hooks.card_layout_will_show.append(hook__customize_layout)
