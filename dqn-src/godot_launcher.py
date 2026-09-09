import os


def resolve_godot_exe() -> str:
    """
    Command or full path used to launch Godot.

    Defaults to "godot" on PATH (works cross-platform if Godot is installed
    that way). Override with the GODOT_EXE environment variable if Godot
    isn't on PATH, e.g. on Windows if you installed via Scoop:
        set GODOT_EXE=%USERPROFILE%\\scoop\\apps\\godot\\current\\godot.console.exe
    """
    return os.environ.get("GODOT_EXE", "godot")
