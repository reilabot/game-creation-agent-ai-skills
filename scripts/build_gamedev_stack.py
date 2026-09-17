#!/usr/bin/env python3
"""Build the repository-local Game Dev Super Stack without touching game code."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"

SKILL_GROUPS = {
    "orchestration": {
        "game-studio-director": ("Orchestrate a game project from goal to release by selecting specialists, dependency waves, playable increments, and evidence gates. Use for broad game creation or multi-system changes.", "project brief, dependency graph, increment plan, release evidence"),
        "gamedev-project-analyzer": ("Inspect an existing or proposed game project and determine engine, language, dimensions, platforms, multiplayer mode, tools, risks, and missing evidence. Use before routing substantial game work.", "evidence-based project profile and uncertainty list"),
        "gamedev-router": ("Route a game-development goal to the smallest sufficient set of engine, genre, system, art, release, and QA skills. Use after project analysis or when a request crosses game disciplines.", "ordered skills, roles, model classes, tools, dependencies, and gates"),
        "gamedev-language-selector": ("Select or confirm a programming language for a game project from engine constraints, target platforms, performance needs, iteration speed, ecosystem, and team capability. Use for new projects, undecided engines, or language/engine tradeoffs.", "a primary language, compatible alternatives, decisive constraints, confidence, and validation plan"),
        "gamedev-quality-gate": ("Gate playable increments and releases using functional, visual, performance, accessibility, persistence, networking, and platform evidence. Use before accepting a game increment or build.", "pass/fail report with reproducible evidence and fix loop"),
        "game-design": ("Turn a game concept into testable pillars, player fantasy, core loop, constraints, and a scoped vertical slice. Use during concept, preproduction, or feature prioritization.", "concise design brief and falsifiable prototype questions"),
    },
    "genres": {
        "genre-mmo": ("Design MMO shards, authority, persistence, interest management, social systems, and operations. Use for massively multiplayer worlds.", "population model, service boundaries, persistence and load-test plan"),
        "genre-rts": ("Design real-time strategy economy, unit control, fog, pathfinding, combat simulation, and deterministic replay. Use for RTS games.", "simulation rules, command model, AI and scale budgets"),
        "genre-4x": ("Design explore-expand-exploit-exterminate loops, diplomacy, economy, research, AI turns, and late-game pacing. Use for 4X games.", "turn model, systemic dependencies, balance simulation"),
        "genre-city-builder": ("Design zoning, placement, services, traffic, resources, citizen feedback, and city simulation. Use for city builders.", "simulation graph, build loop, readability and scale checks"),
        "genre-colony-sim": ("Design agent needs, jobs, scheduling, resources, incidents, and emergent colony stories. Use for colony simulations.", "agent model, job arbitration, incident and performance tests"),
        "genre-tycoon": ("Design business operations, customer flow, pricing, upgrades, staffing, and financial progression. Use for tycoon games.", "economy loop, demand model, dashboards and balance tests"),
        "genre-soulslike": ("Design deliberate stamina combat, telegraphs, checkpoints, recovery loops, bosses, and build progression. Use for soulslike games.", "combat contract, encounter rules, fairness playtests"),
        "genre-metroidvania": ("Design ability-gated exploration, interconnected maps, backtracking rewards, traversal, and progression. Use for metroidvania games.", "ability graph, map gates, sequence-break tests"),
        "genre-fighting": ("Design fighting-game frame data, state machines, cancels, hitboxes, training tools, input handling, and rollback needs. Use for fighting games.", "combat timing model, input and netcode test matrix"),
        "genre-racing": ("Design vehicle handling, tracks, racing rules, AI lines, assists, timing, and camera feedback. Use for racing games.", "handling targets, track metrics, assist and latency tests"),
        "genre-sports": ("Design sport rules, player/team simulation, controls, officiating, AI tactics, seasons, and presentation. Use for sports games.", "rules model, control scheme, AI and replay validation"),
        "genre-rhythm": ("Design beat maps, timing windows, calibration, latency compensation, scoring, and audio synchronization. Use for rhythm games.", "timing contract, calibration flow, sync evidence"),
        "genre-extraction-shooter": ("Design raid loops, extraction, authoritative inventory, risk/reward, matchmaking, anti-cheat, and loss recovery. Use for extraction shooters.", "raid state model, economy sinks, security and recovery tests"),
        "genre-moba": ("Design lanes, objectives, heroes, abilities, items, vision, matchmaking, and authoritative team combat. Use for MOBAs.", "match flow, content schema, balance telemetry"),
        "genre-auto-battler": ("Design shops, pools, synergies, formations, deterministic combat, rounds, and economy. Use for auto battlers.", "round state machine, pool odds, simulation tests"),
        "genre-party-game": ("Design quick onboarding, short rounds, local/online join, fairness, accessibility, and spectator-readable chaos. Use for party games.", "round contract, join/recovery flows, mixed-device tests"),
        "genre-idle-incremental": ("Design offline progress, generators, prestige, curves, caps, time integrity, and automation. Use for idle or incremental games.", "economy formulas, offline simulation and exploit tests"),
        "genre-gacha-live-service": ("Design transparent gacha probabilities, pity, currencies, content cadence, entitlements, and live-service economy. Use for gacha systems; require legal and publishing review.", "economy model, disclosure, simulation, rollback and approval gates"),
    },
    "systems": {
        "game-quest-system": ("Design data-driven quests, objectives, branching, rewards, failure, persistence, and migration. Use for quest systems.", "quest schema, state transitions, save and regression tests"),
        "game-crafting-building": ("Design recipes, stations, placement, snapping, validation, construction, ownership, and persistence. Use for crafting or building.", "data contracts, placement authority, save and multiplayer tests"),
        "game-skill-tree": ("Design unlock graphs, prerequisites, respec, modifiers, UI presentation, persistence, and migration. Use for skill trees.", "acyclic graph, effect contract, save/version tests"),
        "game-boss-encounter": ("Design readable boss phases, telegraphs, arenas, transitions, recovery, rewards, and accessibility. Use for boss encounters.", "phase graph, timing sheet, fairness and performance captures"),
        "game-authoritative-server": ("Design server-authoritative game state, validation, ownership, replication, interest management, and abuse resistance. Use for competitive or persistent online games.", "authority matrix, protocol boundaries, load and security tests"),
        "game-rollback-netcode": ("Design deterministic rollback, input prediction, snapshots, resimulation, delay policy, and desync detection. Use for latency-sensitive peer matches.", "rollback budget, deterministic harness, latency and desync tests"),
        "game-network-prediction": ("Design client prediction, reconciliation, interpolation, lag compensation, and correction presentation. Use for real-time online movement or combat.", "timeline model, authority rules, impairment tests"),
        "game-anti-cheat": ("Threat-model game clients, servers, economy, telemetry, sanctions, false positives, and secure updates. Use for online competitive or valuable economies.", "threat model, server checks, privacy-aware response plan"),
        "game-save-migration": ("Version, migrate, back up, validate, and recover game saves without player data loss. Use when schemas or persistent content change.", "versioned migration, golden saves, rollback and corruption tests"),
        "game-desync-investigation": ("Capture and localize multiplayer desynchronization using deterministic logs, hashes, replay, binary search, and network impairment. Use for state divergence.", "minimal reproduction, first divergent tick and verified fix"),
        "game-economy-balance-simulation": ("Model and simulate sources, sinks, progression curves, player cohorts, exploits, and sensitivity. Use before changing a game economy.", "explicit assumptions, seeded simulation, charts and balance risks"),
        "game-localization": ("Design localization-ready strings, fonts, layout expansion, pluralization, bidi, voice, and linguistic QA. Use for multilingual games.", "string pipeline, locale matrix, pseudo-localization and LQA"),
        "game-visual-regression": ("Create deterministic visual states and compare screenshots across builds, devices, resolutions, and quality levels. Use for visual regression testing.", "baselines, tolerances, diffs and human review gate"),
        "game-qa-playtest": ("Plan functional QA, exploratory playtests, telemetry, bug reproduction, compatibility, and release triage. Use for playable increments.", "risk-based matrix, sessions, evidence and triaged defects"),
        "game-build-ci-cd": ("Build reproducible game CI/CD with pinned toolchains, caching, tests, signing boundaries, artifacts, and promotion gates. Use for automated builds and delivery.", "pipeline definition, immutable artifacts and rollback procedure"),
        "game-publishing-liveops": ("Plan store submission, compliance, staged rollout, telemetry, incidents, updates, and end-of-life. Use for publishing or live operations.", "release checklist, approvals, monitoring and rollback"),
        "game-art-2d": ("Plan and produce coherent 2D sprites, tiles, UI art, palettes, animation, import settings, and atlases. Use for 2D art pipelines.", "art bible, asset specs, import and visual QA"),
        "game-art-3d-blender": ("Plan 3D Blender assets with scale, topology, UVs, materials, rigs, LODs, collision, export, and provenance. Use for 3D asset pipelines.", "asset contract, export preset, engine import and visual QA"),
        "game-animation": ("Design responsive state-driven animation, rigs, retargeting, root motion, blending, events, and performance. Use for character or object animation.", "state graph, timing contract, transition and runtime tests"),
        "game-audio": ("Design music, ambience, dialogue, SFX, mixing, buses, spatial audio, accessibility, and runtime budgets. Use for game audio systems.", "audio event map, loudness/mix targets, device and runtime tests"),
    },
    "ui": {
        "game-ui-information-architecture": ("Structure HUD, menus, screens, hierarchy, and information priority. Use when defining game UI navigation or display architecture.", "screen map, information priorities, navigation paths"),
        "game-hud-design": ("Design readable combat, exploration, and status HUDs across devices and aspect ratios. Use for HUD work.", "HUD states, readability tests, safe-zone layouts"),
        "game-menu-navigation": ("Design keyboard, mouse, gamepad, and touch navigation with focus recovery. Use for menus and settings.", "navigation graph, focus rules, mixed-input tests"),
        "game-inventory-ui": ("Design inventory, equipment, loot, drag/drop, comparison, and loss-safe interactions. Use for inventory UI.", "interaction states, error recovery, controller/touch tests"),
        "game-dialogue-quest-ui": ("Design dialogue, choices, quest tracking, subtitles, and history. Use for narrative UI.", "content states, subtitle rules, accessibility tests"),
        "game-shop-crafting-ui": ("Design shops, currencies, recipes, confirmation, cancellation, and insufficient-resource states. Use for shop or crafting UI.", "transaction flow, preview, confirmation and rollback tests"),
        "game-onboarding-tutorial": ("Design progressive onboarding, contextual hints, practice, skip/replay, and learning validation. Use for tutorials.", "learning objectives, trigger rules, comprehension playtests"),
        "game-responsive-ui": ("Adapt UI to resolution, aspect ratio, safe area, DPI, density, input method, and localization. Use for responsive game UI.", "layout constraints and device/resolution matrix"),
        "game-ui-motion": ("Design transitions, focus motion, micro-interactions, feedback animation, interruption, and reduced motion. Use for UI animation.", "motion tokens, state transitions, reduced-motion tests"),
        "game-accessibility": ("Integrate color, subtitle, text, remapping, difficulty, audio, motor, cognitive, and motion accessibility. Use during design and quality gates.", "accessibility matrix, defaults, persistence and user tests"),
        "game-ux-research": ("Run usability studies using task success, behavior logs, comprehension, and drop-off evidence. Use to validate game UX.", "study plan, observations, findings and prioritized changes"),
    },
    "effects": {
        "game-vfx-direction": ("Define a coherent VFX language for color, shape, timing, hierarchy, and gameplay readability. Use when directing game effects.", "VFX bible, semantic palette, readability rules"),
        "game-particle-effects": ("Implement particles, trails, decals, emitters, pooling, and deterministic triggers. Use for particle effects.", "effect prefab contract, budgets, pooling and capture tests"),
        "game-shader-effects": ("Implement surface, dissolve, outline, damage, and environment shaders with fallbacks. Use for gameplay shader effects.", "parameter contract, variants, performance and readability tests"),
        "game-post-processing": ("Use bloom, grading, depth, exposure, and motion effects without hiding game state. Use for post-processing.", "volume profiles, accessibility toggles, GPU captures"),
        "game-combat-effects": ("Design hit, critical, guard, parry, heal, and status effects tied to authoritative events. Use for combat VFX.", "event mapping, priority, timing and clutter tests"),
        "game-environment-effects": ("Design weather, fog, wind, water, fire, and destruction effects. Use for environmental presentation.", "state contract, transitions, budgets and gameplay visibility tests"),
        "game-screen-effects": ("Design vignette, flash, damage direction, and low-health screen effects with accessibility controls. Use for screen-space feedback.", "priority stack, intensity caps, comfort tests"),
        "game-camera-effects": ("Design shake, impulse, zoom, FOV, framing, and transitions driven by gameplay events. Use for camera effects.", "impulse contract, envelopes, comfort and collision tests"),
        "game-cinematics": ("Design cutscenes, timelines, camera blocking, gameplay handoff, skip, and checkpoint behavior. Use for cinematics.", "sequence plan, state handoff, skip and localization tests"),
        "game-ui-effects": ("Design UI particles, selection, reward, notification, and rarity effects that preserve legibility. Use for UI effects.", "effect hierarchy, motion alternatives, performance tests"),
        "game-audio-visual-sync": ("Synchronize animation, VFX, SFX, music, camera, and haptics through shared semantic events. Use for cross-modal feedback.", "feedback event schema, timing offsets and capture validation"),
        "game-vfx-optimization": ("Measure and reduce VFX overdraw, particles, variants, memory, and spikes using platform budgets. Use when effects threaten performance.", "budget table, captures, LOD/pooling plan and before/after data"),
    },
    "feel": {
        "game-input-design": ("Design action maps, rebinding, device switching, conflicts, prompts, and persistence. Use for input architecture.", "input map, conflict rules, device and accessibility tests"),
        "game-player-controller": ("Implement tunable movement, acceleration, turning, slopes, air control, collision, and state transitions. Use for player controllers.", "movement model, parameter asset, edge-case tests"),
        "game-input-buffering": ("Implement input buffers, queues, priorities, cancel windows, expiry, and debugging. Use for timing-sensitive controls.", "buffer contract, timing parameters, frame-step tests"),
        "game-platformer-feel": ("Tune coyote time, jump buffering, variable jump, apex, falling, landing, and feedback. Use for platformer controls.", "tuning data, trajectory plots, blind playtests"),
        "game-combat-feel": ("Tune startup, active, recovery, combos, cancels, parries, hit reactions, and readable timing. Use for action combat feel.", "frame/timing data, event hooks, fairness playtests"),
        "game-aiming-assistance": ("Design aim assist, target selection, dead zones, sensitivity, gyro, and fairness controls. Use for aiming.", "assist policy, tunable curves, device and skill-level tests"),
        "game-lock-on-targeting": ("Implement lock-on, target scoring, cycling, occlusion, camera coordination, and release rules. Use for target lock systems.", "selection model, camera contract, crowded-scene tests"),
        "game-camera-feel": ("Tune follow, look-ahead, damping, collision, recentering, framing, and FOV. Use for gameplay camera feel.", "camera states, tunable profiles, comfort and occlusion tests"),
        "game-hit-feedback": ("Layer hit stop, shake, flash, knockback, impact frames, sound, and haptics from shared events. Use for impact feedback.", "feedback recipe, priority/caps, slow-motion capture tests"),
        "game-recoil-feedback": ("Tune weapon, camera, reticle, spread, recovery, sound, VFX, and haptics recoil. Use for weapon feedback.", "recoil curves, recovery rules, input/device tests"),
        "game-haptics": ("Design vibration, rumble, adaptive trigger, and mobile haptics with priorities and user controls. Use for tactile feedback.", "semantic haptic events, device fallbacks, comfort tests"),
        "game-animation-responsiveness": ("Reduce perceived animation latency through blend tuning, root-motion policy, anticipation, cancel rules, and event timing. Use for responsive animation.", "latency budget, transition profiles, frame-step evidence"),
        "game-control-latency": ("Measure and budget input-to-photon latency, frame pacing, buffering, display, and network delay. Use for latency diagnosis.", "measurement method, latency budget, before/after captures"),
        "game-feel-playtesting": ("Run blinded comparison tests for controls and feedback with reproducible builds, tasks, metrics, and tuning logs. Use for feel validation.", "test protocol, observations, chosen parameters and rationale"),
    },
}

def skill_text(name: str, description: str, deliverable: str) -> str:
    if name == "gamedev-language-selector":
        return f"""---
name: {name}
description: {description}
---

# Game Development Language Selector

Choose a language only after separating hard constraints from preferences. If an existing engine or codebase fixes the language, confirm that constraint instead of proposing a rewrite.

## Decision inputs

- Existing engine, source language, build pipeline, plugins, and shipped code
- Target platforms and store or console restrictions
- Game scale, simulation density, latency, memory, loading, and determinism needs
- Team experience, hiring, iteration speed, debugging, tooling, middleware, and maintenance horizon
- Networking authority, modding/scripting needs, native integration, and deployment model

## Workflow

1. Detect existing project evidence first. Treat an established engine-language pairing as locked unless the user explicitly requests migration analysis.
2. Convert requirements into hard constraints, weighted preferences, and unknowns. Do not equate raw language speed with shipped-game performance without profiling evidence.
3. Eliminate incompatible options, then compare the remaining candidates on platform support, engine maturity, libraries, iteration, runtime behavior, operations, and team risk.
4. Return one primary recommendation when evidence is decisive. Otherwise return a ranked shortlist and name the smallest prototype or benchmark that resolves the uncertainty.
5. Route to the matching engine Skill. Keep gameplay scripting, native extensions, shaders, build scripts, and backend services as separate language decisions when appropriate.

## Output contract

Report `primary`, `alternatives`, `locked_by_engine`, `confidence`, `reasons`, `tradeoffs`, and `validation`. Never invent an engine-language combination that the target engine does not support.

## Boundaries

Do not migrate an existing project, add a runtime, or change build tooling merely because another language scores higher. Such changes require an explicit migration request and evidence covering plugins, assets, saves, CI, platform certification, and rollback.
"""
    return f"""---
name: {name}
description: {description}
---

# {name}

## Scope

Own this responsibility while preserving the detected engine's conventions. Do not replace adjacent specialists; compose through explicit data and semantic event contracts.

## Workflow

1. Read the project profile, player-facing goal, constraints, target hardware, and existing tests before changing files.
2. State measurable behavior, ownership, tunable parameters, failure cases, and the smallest playable increment.
3. Implement through engine-native APIs after detecting versions and available tools. Keep simulation truth separate from presentation.
4. Connect neighboring systems with data schemas or semantic events; avoid direct cross-system dependencies where a stable contract works.
5. Produce {deliverable}.

## Quality gate

Test the representative player journey and edge cases on the target input and platform. Capture available logs, screenshots/video, profiler data, saves, or network traces. A file existing is not proof of correct behavior.

## Boundaries

Require explicit approval immediately before destructive data operations, purchases, credential use, store publication, production deployment, or irreversible external changes. Never embed secrets. Route final acceptance through `gamedev-quality-gate`.
"""

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def main() -> None:
    for group in SKILL_GROUPS.values():
        for name, (desc, deliverable) in group.items():
            target = SKILLS / name / "SKILL.md"
            if target.exists():
                continue
            write(target, skill_text(name, desc, deliverable))

    model_routing = {
        "version": 1,
        "classes": {
            "frontier-high": {"use_for": ["requirements", "architecture", "integration", "hard-debugging"], "reasoning": "high"},
            "coding-high": {"use_for": ["implementation", "refactor", "test-fixes"], "reasoning": "high"},
            "vision-capable": {"use_for": ["screenshots", "ui", "art", "visual-qa"], "reasoning": "medium"},
            "fast-low-cost": {"use_for": ["inventory", "formatting", "mechanical-checks"], "reasoning": "low"},
        },
        "rule": "Map to an available model only at execution time; never fail because a product name is absent.",
    }
    engine_detection = {
        "version": 1,
        "engines": {
            "unity": {"files": ["ProjectSettings/ProjectVersion.txt", "Assets/**"], "skills": ["unity-csharp-scripting"]},
            "unreal": {"files": ["*.uproject", "Source/*.Build.cs"], "skills": ["unreal-cpp-gameplay"]},
            "godot": {"files": ["project.godot"], "skills": ["godot-gdscript", "godot-nodes-scenes"]},
            "roblox": {"files": ["default.project.json", "*.rbxl*"], "skills": ["roblox-luau", "roblox-networking"]},
            "bevy": {"content": ["bevy"], "files": ["Cargo.toml"], "skills": ["bevy-ecs"]},
            "phaser": {"content": ["phaser"], "files": ["package.json"], "skills": ["phaser-core"]},
            "pixijs": {"content": ["pixi.js", "pixijs"], "files": ["package.json"], "skills": ["pixijs-rendering"]},
            "threejs": {"content": ["three"], "files": ["package.json"], "skills": ["threejs-scene-setup"]},
            "pygame": {"content": ["pygame"], "files": ["requirements.txt", "pyproject.toml"], "skills": ["pygame-core"]},
            "love2d": {"files": ["conf.lua", "main.lua"], "skills": ["love2d-core"]},
        },
    }
    language_selection = {
        "version": 1,
        "engine_languages": {
            "unity": {"primary": "C#", "alternatives": [], "reason": "Unity gameplay and editor scripting use C# as the supported default."},
            "unreal": {"primary": "C++", "alternatives": ["Blueprints"], "reason": "Unreal native gameplay uses C++; Blueprints complement it for visual scripting."},
            "godot": {"primary": "GDScript", "alternatives": ["C#"], "reason": "GDScript provides the tightest Godot workflow; C# is viable when .NET constraints are acceptable."},
            "roblox": {"primary": "Luau", "alternatives": [], "reason": "Roblox runtime scripting uses Luau."},
            "bevy": {"primary": "Rust", "alternatives": [], "reason": "Bevy is a Rust engine and ECS framework."},
            "phaser": {"primary": "TypeScript", "alternatives": ["JavaScript"], "reason": "TypeScript adds static tooling while preserving the Phaser web ecosystem."},
            "pixijs": {"primary": "TypeScript", "alternatives": ["JavaScript"], "reason": "TypeScript is the maintainable default for PixiJS web projects."},
            "threejs": {"primary": "TypeScript", "alternatives": ["JavaScript"], "reason": "TypeScript improves contracts in non-trivial Three.js applications."},
            "pygame": {"primary": "Python", "alternatives": [], "reason": "pygame targets Python."},
            "love2d": {"primary": "Lua", "alternatives": [], "reason": "LÖVE gameplay is authored in Lua."},
        },
        "signals": [
            {"language": "TypeScript", "keywords": ["browser", "webgl", "web game", "ブラウザ"], "reason": "The browser target favors the TypeScript/JavaScript ecosystem."},
            {"language": "C++", "keywords": ["aaa", "native", "console", "maximum performance", "最高性能"], "reason": "Native and high-end constraints favor C++ when the engine ecosystem supports it."},
            {"language": "Rust", "keywords": ["rust", "bevy", "ecs", "memory safety"], "reason": "Rust fits Bevy/ECS or explicit memory-safety requirements."},
            {"language": "GDScript", "keywords": ["rapid prototype", "small team", "beginner", "godot", "小規模", "プロトタイプ"], "reason": "Fast iteration and a small team favor GDScript with Godot."},
            {"language": "C#", "keywords": ["unity", "mobile", "cross-platform", "モバイル", "クロスプラットフォーム"], "reason": "Unity/C# offers broad platform support and productive iteration."},
            {"language": "Python", "keywords": ["pygame", "python", "education", "教材"], "reason": "Python fits pygame and education-oriented development."},
            {"language": "Lua", "keywords": ["love2d", "löve", "lua"], "reason": "Lua is the native LÖVE scripting choice."}
        ],
        "fallback": {"primary": None, "alternatives": ["C#", "GDScript", "TypeScript", "C++"], "reason": "Engine and platform constraints are insufficient; select the engine or run a vertical-slice spike first."}
    }
    rules = [
        (["platformer", "プラットフォーマー", "coyote", "jump buffer"], ["platformer", "game-platformer-feel", "game-input-buffering", "game-player-controller", "game-hit-feedback", "game-camera-effects", "game-audio-visual-sync"]),
        (["melee", "近接", "soulslike"], ["game-combat-feel", "game-lock-on-targeting", "game-hit-feedback", "game-camera-effects", "game-haptics", "game-animation-responsiveness", "game-boss-encounter"]),
        (["mobile", "モバイル", "touch"], ["game-responsive-ui", "game-menu-navigation", "game-input-design", "game-haptics", "game-vfx-optimization", "game-accessibility"]),
        (["controller", "gamepad", "コントローラー"], ["game-menu-navigation", "game-input-design", "game-accessibility"]),
        (["webgl", "low-end", "低性能"], ["game-responsive-ui", "game-vfx-optimization", "game-control-latency", "performance-optimization", "game-accessibility"]),
        (["roguelite", "roguelike", "ローグ"], ["roguelike", "procedural-gen", "save-systems"]),
        (["idle", "放置"], ["genre-idle-incremental", "game-economy-balance-simulation", "save-systems"]),
        (["survival", "サバイバル", "crafting", "クラフト", "building", "建築"], ["survival-crafting", "game-crafting-building", "save-systems"]),
        (["card game", "カードゲーム"], ["game-design", "save-systems"]),
        (["tycoon", "タイクーン"], ["genre-tycoon", "game-economy-balance-simulation", "save-systems"]),
        (["strategy", "ストラテジー", "turn-based", "ターン制"], ["game-design", "game-economy-balance-simulation", "game-ai"]),
        (["multiplayer", "online", "協力", "専用サーバー"], ["game-authoritative-server", "game-network-prediction", "game-desync-investigation", "game-anti-cheat"]),
        (["ui", "hud", "menu", "字幕", "safe area"], ["game-ui-information-architecture", "game-responsive-ui", "game-accessibility"]),
    ]
    skill_routing = {"version": 1, "always": ["gamedev-project-analyzer", "gamedev-language-selector", "gamedev-router"], "rules": [{"keywords": k, "skills": s} for k, s in rules], "finish": ["game-qa-playtest", "gamedev-quality-gate"]}
    quality = {"version": 1, "gates": {"functional": "critical journeys and failure recovery pass", "persistence": "versioned save/load and migration evidence", "network": "authority and impairment tests when online", "visual": "readability across target states and resolutions", "accessibility": "input, subtitle, color, text, motion settings persist", "performance": "representative frame-time and memory budgets", "release": "immutable artifact, provenance, rollback and approvals"}}
    for name, data in (("model-routing.yaml", model_routing), ("engine-detection.yaml", engine_detection), ("language-selection.yaml", language_selection), ("skill-routing.yaml", skill_routing), ("quality-gates.yaml", quality)):
        write(ROOT / ".agents" / "config" / name, json.dumps(data, ensure_ascii=False, indent=2))

    fixtures = [
        {"name":"godot-pixel-roguelite","goal":"Godot 2D pixel art roguelite","engine":"godot","expect":["godot-gdscript","roguelike","procedural-gen","gamedev-quality-gate"]},
        {"name":"unity-mobile-idle","goal":"Unity mobile idle RPG touch UI","engine":"unity","expect":["unity-csharp-scripting","genre-idle-incremental","game-responsive-ui","game-accessibility"]},
        {"name":"unreal-coop-survival","goal":"Unreal four player online survival crafting building dedicated server","engine":"unreal","expect":["unreal-cpp-gameplay","survival-crafting","game-authoritative-server","game-crafting-building"]},
        {"name":"phaser-card","goal":"Phaser browser card game","engine":"phaser","expect":["phaser-core","game-design"]},
        {"name":"roblox-tycoon","goal":"Roblox multiplayer tycoon","engine":"roblox","expect":["roblox-luau","roblox-networking","genre-tycoon"]},
        {"name":"bevy-action","goal":"Bevy desktop ECS action game","engine":"bevy","expect":["bevy-ecs"]},
        {"name":"threejs-exploration","goal":"Three.js 3D browser exploration game","engine":"threejs","expect":["threejs-scene-setup"]},
        {"name":"undecided-strategy","goal":"engine undecided turn-based strategy","engine":None,"expect":["game-design","game-economy-balance-simulation","game-ai"]},
        {"name":"feel-platformer","goal":"2D platformer coyote time jump buffer landing VFX SFX camera impulse","engine":None,"expect":["game-platformer-feel","game-input-buffering","game-hit-feedback","game-camera-effects","game-audio-visual-sync"]},
        {"name":"feel-melee","goal":"3D melee combat lock-on combo cancel hit stop camera shake haptics boss telegraph","engine":None,"expect":["game-lock-on-targeting","game-combat-feel","game-hit-feedback","game-haptics","game-boss-encounter"]},
        {"name":"feel-mobile","goal":"mobile action touch UI safe area gesture haptics low-cost VFX","engine":None,"expect":["game-responsive-ui","game-input-design","game-haptics","game-vfx-optimization"]},
        {"name":"feel-controller-menu","goal":"controller-first menu focus navigation rebind subtitles text size colorblind","engine":None,"expect":["game-menu-navigation","game-input-design","game-accessibility"]},
        {"name":"feel-low-webgl","goal":"low-end WebGL responsive UI shader particle budget input latency visual readability","engine":None,"expect":["game-responsive-ui","game-vfx-optimization","game-control-latency","performance-optimization"]},
        {"name":"language-browser","goal":"browser multiplayer game with a maintainable typed codebase","engine":None,"expect":["gamedev-language-selector"],"expect_language":"TypeScript"},
        {"name":"language-aaa-native","goal":"AAA native console action game requiring maximum performance","engine":None,"expect":["gamedev-language-selector"],"expect_language":"C++"},
        {"name":"language-small-prototype","goal":"small team rapid prototype for a 2D game","engine":None,"expect":["gamedev-language-selector"],"expect_language":"GDScript"},
        {"name":"language-engine-lock","goal":"four player survival game","engine":"unreal","expect":["gamedev-language-selector","unreal-cpp-gameplay"],"expect_language":"C++","expect_locked":True},
    ]
    write(ROOT / "tests" / "router-fixtures.json", json.dumps(fixtures, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
