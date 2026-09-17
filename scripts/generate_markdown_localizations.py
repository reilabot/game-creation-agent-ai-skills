#!/usr/bin/env python3
"""Create explicit English and Japanese companions for every Markdown source file."""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PAIR_NAMES = {"INSTALL_EN.md", "INSTALL_JA.md"}
TOKEN_RE = re.compile(r"`[^`\n]+`|https?://[^\s)>]+|\[[^\]]+\]\([^)]*\)")

def translate(text: str) -> str:
    if not re.search(r"[A-Za-z]", text):
        return text
    protected: list[str] = []
    def hold(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"ZXQHOLD{len(protected)-1}QXZ"
    payload = TOKEN_RE.sub(hold, text).replace("\n", " ZXQNEWLINEQXZ ")
    query = urllib.parse.urlencode({"client":"dict-chrome-ex","sl":"en","tl":"ja","q":payload})
    request = urllib.request.Request("https://clients5.google.com/translate_a/t?" + query, headers={"User-Agent":"GameDevSuperStack/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
            result = data[0] if data and isinstance(data[0], str) else "".join(part[0] for part in data[0] if part[0])
            for index, value in enumerate(protected):
                result = result.replace(f"ZXQHOLD{index}QXZ", value)
                result = result.replace(f"ZXQHOLD{index} QXZ", value)
            result = result.replace(" ZXQNEWLINEQXZ ", "\n")
            result = result.replace("ZXQNEWLINEQXZ", "\n")
            return result
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("translation failed")

def translate_markdown(source: str) -> str:
    frontmatter = ""
    body = source
    if source.startswith("---\n"):
        end = source.find("\n---\n", 4)
        if end != -1:
            frontmatter = source[:end + 5]
            body = source[end + 5:]
    blocks = re.split(r"(```[\s\S]*?```)", body)
    translated: list[str] = []
    for index, block in enumerate(blocks):
        if index % 2 == 1:
            translated.append(block)
            continue
        paragraphs = re.split(r"(\n\s*\n)", block)
        chunk = ""
        for paragraph in paragraphs:
            if len(chunk) + len(paragraph) <= 3500:
                chunk += paragraph
                continue
            translated.append(translate(chunk) if chunk.strip() else chunk)
            chunk = paragraph
        translated.append(translate(chunk) if chunk.strip() else chunk)
    note = "> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。\n\n" if frontmatter else ""
    return frontmatter + note + "".join(translated)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    sources = sorted(path for path in root.rglob("*.md") if ".git" not in path.parts and not path.name.endswith((".en.md", ".ja.md")) and path.name not in PAIR_NAMES)
    for source in sources:
        content = source.read_text(encoding="utf-8")
        english = source.with_name(source.stem + ".en.md")
        japanese = source.with_name(source.stem + ".ja.md")
        if not args.force and english.exists() and japanese.exists():
            continue
        english.write_bytes(source.read_bytes())
        japanese.write_text(translate_markdown(content), encoding="utf-8")
        print(source.relative_to(root))
    print(f"localized_markdown_sources={len(sources)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
