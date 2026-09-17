#!/usr/bin/env python3
"""Deterministic, conservative router for the repository-local skill stack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name: str):
    return json.loads((ROOT / ".agents" / "config" / name).read_text(encoding="utf-8"))

def select_language(goal: str, engine: str | None) -> dict:
    config = load("language-selection.yaml")
    if engine and engine in config["engine_languages"]:
        choice = config["engine_languages"][engine]
        return {"primary": choice["primary"], "alternatives": choice["alternatives"], "locked_by_engine": True, "confidence": "high", "reasons": [choice["reason"]], "tradeoffs": ["Changing the primary language may require changing or extending the engine."], "validation": "Confirm engine version, platform modules, plugins, and build pipeline."}
    text = goal.casefold()
    scores: dict[str, int] = {}
    reasons: dict[str, list[str]] = {}
    for signal in config["signals"]:
        hits = sum(keyword.casefold() in text for keyword in signal["keywords"])
        if hits:
            language = signal["language"]
            scores[language] = scores.get(language, 0) + hits
            reasons.setdefault(language, []).append(signal["reason"])
    if not scores:
        fallback = config["fallback"]
        return {"primary": fallback["primary"], "alternatives": fallback["alternatives"], "locked_by_engine": False, "confidence": "low", "reasons": [fallback["reason"]], "tradeoffs": ["No language is defensible until engine, platform, team, and performance constraints are known."], "validation": "Build the same smallest playable vertical slice in the leading candidates."}
    ranked = sorted(scores, key=lambda item: (-scores[item], item))
    primary = ranked[0]
    confidence = "high" if scores[primary] >= 2 or len(ranked) == 1 else "medium"
    return {"primary": primary, "alternatives": ranked[1:3], "locked_by_engine": False, "confidence": confidence, "reasons": reasons[primary], "tradeoffs": ["Re-evaluate if engine, target platform, or team capability changes."], "validation": "Verify the recommendation with a representative vertical slice and target-platform build."}

def route(goal: str, engine: str | None = None) -> dict:
    routing = load("skill-routing.yaml")
    engines = load("engine-detection.yaml")["engines"]
    text = goal.casefold()
    selected = list(routing["always"])
    detected = engine.casefold() if engine else None
    language = select_language(goal, detected)
    if detected and detected in engines:
        selected.extend(engines[detected]["skills"])
    for rule in routing["rules"]:
        if any(keyword.casefold() in text for keyword in rule["keywords"]):
            selected.extend(rule["skills"])
    selected.extend(routing["finish"])
    selected = list(dict.fromkeys(selected))
    return {
        "engine": detected,
        "language_selection": language,
        "skills": selected,
        "roles": ["director", "engine-specialist", "system-specialist", "qa"],
        "model_classes": ["frontier-high", "coding-high", "vision-capable"],
        "tools": ["project-native-cli", "tests", "profiler-or-capture-when-available"],
        "dependency_order": ["analyze", "design-contracts", "playable-increment", "observe", "quality-gate", "fix-loop"],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("goal")
    parser.add_argument("--engine")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(route(args.goal, args.engine), ensure_ascii=False, indent=None if args.compact else 2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
