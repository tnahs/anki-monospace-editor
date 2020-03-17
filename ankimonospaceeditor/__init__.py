import sys

from .src import AnkiMonospaceEditor, errors

try:
    addon = AnkiMonospaceEditor()
except errors.ConfigError as error:
    # Prevents AnkiMonospaceEditor from hooking to Anki if there are any config
    # errors. See `AnkiMonospaceEditor._validate_config()`
    sys.stderr.write(f"{AnkiMonospaceEditor.name}: {error}")
else:
    addon.setup()
