#!/usr/bin/env python3
"""Validate skill structure, routing, links, attribution, and unsafe literals."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from gamedev_router import route

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
ERRORS: list[str] = []

def fail(message: str) -> None:
    ERRORS.append(message)

def main() -> int:
    names: dict[str, Path] = {}
    descriptions: dict[str, Path] = {}
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        fail("no skills found")
    for file in skill_files:
        text = file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not match:
            fail(f"missing frontmatter: {file}")
            continue
        name_match = re.search(r"^name:\s*([^\n]+)$", match.group(1), re.M)
        desc_match = re.search(r"^description:\s*([^\n]+)$", match.group(1), re.M)
        if not name_match or not desc_match:
            fail(f"missing name/description: {file}")
            continue
        name = name_match.group(1).strip()
        desc = desc_match.group(1).strip()
        if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
            fail(f"invalid name: {name}")
        if name != file.parent.name:
            fail(f"folder/name mismatch: {file}")
        if name in names:
            fail(f"duplicate name: {name}")
        if desc not in (">", "|") and desc in descriptions:
            fail(f"duplicate description: {name}")
        names[name] = file
        if desc not in (">", "|"):
            descriptions[desc] = file
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            is_file_link = "/" in target or "\\" in target or target.lower().endswith(".md")
            if is_file_link and "://" not in target and not target.startswith("#") and not (file.parent / target.split("#")[0]).exists():
                fail(f"broken link: {file} -> {target}")
        if re.search(r"(?i)(api[_-]?key|token|password)\s*[:=]\s*['\"][A-Za-z0-9+/=_-]{12,}", text):
            fail(f"possible secret literal: {file}")
    config = json.loads((ROOT / ".agents/config/skill-routing.yaml").read_text(encoding="utf-8"))
    routed = set(config["always"] + config["finish"])
    for rule in config["rules"]:
        routed.update(rule["skills"])
    engines = json.loads((ROOT / ".agents/config/engine-detection.yaml").read_text(encoding="utf-8"))
    for data in engines["engines"].values():
        routed.update(data["skills"])
    for name in routed - names.keys():
        fail(f"route references missing skill: {name}")
    fixtures = json.loads((ROOT / "tests/router-fixtures.json").read_text(encoding="utf-8"))
    for fixture in fixtures:
        result = route(fixture["goal"], fixture["engine"])
        missing = sorted(set(fixture["expect"]) - set(result["skills"]))
        if missing:
            fail(f"fixture {fixture['name']} missing {missing}")
        if len(result["skills"]) > 18:
            fail(f"fixture {fixture['name']} over-routed: {len(result['skills'])}")
        if "expect_language" in fixture and result["language_selection"]["primary"] != fixture["expect_language"]:
            fail(f"fixture {fixture['name']} expected language {fixture['expect_language']} but got {result['language_selection']['primary']}")
        if "expect_locked" in fixture and result["language_selection"]["locked_by_engine"] != fixture["expect_locked"]:
            fail(f"fixture {fixture['name']} language lock mismatch")
    required = [
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "ORIGINAL_SKILLS_LICENSE.en.md",
        ROOT / "ORIGINAL_SKILLS_LICENSE.ja.md",
        ROOT / "TERMS_OF_USE.en.md",
        ROOT / "TERMS_OF_USE.ja.md",
        ROOT / "LICENSES/Apache-2.0.txt",
        ROOT / "docs/source-lock.md",
        ROOT / ".agents/README.md",
    ]
    for file in required:
        if not file.exists():
            fail(f"required file missing: {file}")
    license_text = (ROOT / "ORIGINAL_SKILLS_LICENSE.en.md").read_text(encoding="utf-8")
    for required_term in ["Use", "Reference", "Mandatory attribution", "Prohibited conduct", "sell"]:
        if required_term not in license_text:
            fail(f"original skills license missing required term: {required_term}")
    print(f"skills={len(skill_files)} fixtures={len(fixtures)} errors={len(ERRORS)}")
    for error in ERRORS:
        print(f"ERROR: {error}")
    return 1 if ERRORS else 0

if __name__ == "__main__":
    raise SystemExit(main())
