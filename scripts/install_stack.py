#!/usr/bin/env python3
"""Reproduce external skills at a fixed revision, then build local skills."""
from __future__ import annotations

import argparse
import hashlib
import io
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REVISION = "b105e1cf617adf0b68ed98790a716bbb60993179"
ARCHIVE_SHA256 = "ab6762d63dc829d2d69f5a562fa5b7ca4942db9ef738c801b5167431f585df45"
PATHS = [
    "skills/unity/unity-csharp-scripting", "skills/unreal/unreal-cpp-gameplay",
    "skills/godot/godot-gdscript", "skills/godot/godot-nodes-scenes",
    "skills/other-engines/roblox-luau", "skills/other-engines/roblox-networking",
    "skills/other-engines/bevy-ecs", "skills/web-engines/phaser-core",
    "skills/web-engines/pixijs-rendering", "skills/web-engines/threejs-scene-setup",
    "skills/other-engines/pygame-core", "skills/other-engines/love2d-core",
    "skills/disciplines/save-systems", "skills/disciplines/performance-optimization",
    "skills/disciplines/game-ai", "skills/disciplines/procedural-gen",
    "skills/disciplines/audio-design", "skills/disciplines/shader-programming",
    "skills/disciplines/level-design", "skills/disciplines/game-ui-ux",
    "skills/disciplines/input-systems", "skills/disciplines/game-feel",
    "skills/genres/survival-crafting", "skills/genres/rpg", "skills/genres/roguelike",
    "skills/genres/platformer", "skills/workflows/steam-publish", "skills/workflows/itch-publish",
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, default=Path.cwd())
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root = args.dest.resolve()
    url = f"https://github.com/gamedev-skills/awesome-gamedev-agent-skills/archive/{REVISION}.zip"
    data = urllib.request.urlopen(url, timeout=60).read()
    digest = hashlib.sha256(data).hexdigest()
    print(f"archive_sha256={digest}")
    if ARCHIVE_SHA256 != "TO_BE_RECORDED_BY_UPDATE_WORKFLOW" and digest != ARCHIVE_SHA256:
        raise SystemExit("archive checksum mismatch")
    if args.verify_only:
        return 0
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        zipfile.ZipFile(io.BytesIO(data)).extractall(temp_path)
        source = next(temp_path.iterdir())
        destination = root / ".agents" / "skills"
        for relative in PATHS:
            src = source / relative
            dst = destination / src.name
            if dst.exists():
                raise SystemExit(f"refusing to overwrite {dst}")
            shutil.copytree(src, dst)
    subprocess.run([sys.executable, str(root / "scripts/build_gamedev_stack.py")], check=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
