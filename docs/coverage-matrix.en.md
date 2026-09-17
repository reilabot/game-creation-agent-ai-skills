# Coverage Matrix

Status is `full`, `partial`, `planned`, or `not-applicable` and names the evidence skill.

## Engine x basic capability

| Engine | Core | Gameplay/data | UI/input | Build/release |
|---|---|---|---|---|
| Unity | full `unity-csharp-scripting` | full cross-engine systems | full `game-responsive-ui`, `game-input-design` | partial `game-build-ci-cd` |
| Unreal | full `unreal-cpp-gameplay` | full cross-engine systems | full UI/input specialists | partial `game-build-ci-cd` |
| Godot | full `godot-gdscript`, `godot-nodes-scenes` | full cross-engine systems | full UI/input specialists | partial `game-build-ci-cd` |
| Roblox | full `roblox-luau`, `roblox-networking` | full cross-engine systems | full UI/input specialists | partial platform publishing |
| Bevy | full `bevy-ecs` | full cross-engine systems | partial engine UI specifics | partial `game-build-ci-cd` |
| Phaser | full `phaser-core` | full cross-engine systems | full UI/input specialists | full `itch-publish` |
| PixiJS | full `pixijs-rendering` | partial framework/game loop | full UI/input specialists | full `itch-publish` |
| Three.js | full `threejs-scene-setup` | full cross-engine systems | full UI/input specialists | full `itch-publish` |
| pygame | full `pygame-core` | full cross-engine systems | partial advanced UI | partial desktop packaging |
| LÖVE | full `love2d-core` | full cross-engine systems | partial advanced UI | partial desktop packaging |
| Custom engine | partial project-native APIs | full contracts/systems | full intent, planned adapters | partial platform-specific |

## Genre x required systems

| Genre families | Status and skills |
|---|---|
| RPG, roguelike, survival, platformer | full `rpg`, `roguelike`, `survival-crafting`, `platformer` |
| MMO, RTS, 4X, city/colony/tycoon | full `genre-mmo`, `genre-rts`, `genre-4x`, `genre-city-builder`, `genre-colony-sim`, `genre-tycoon` |
| Soulslike, metroidvania, fighting | full respective `genre-*`, combat/feel/netcode skills |
| Racing, sports, rhythm | full respective `genre-*`, latency/camera/audio skills |
| Extraction, MOBA, auto battler, party | full respective `genre-*`, authority/economy/QA skills |
| Idle, gacha/live service | full `genre-idle-incremental`, `genre-gacha-live-service`, economy/publishing gates |

## Production stage x owner

| Stage | Status and skills |
|---|---|
| Concept/design | full `game-design`, `game-studio-director` |
| Engineering/gameplay/world/AI | full engine skills, `game-ai`, `level-design`, system skills |
| 2D/3D/animation/VFX/audio | full `game-art-*`, `game-animation`, `game-vfx-*`, `game-audio` |
| UI/UX/accessibility/feel | full all `game-ui-*`, `game-accessibility`, `game-*-feel`, input/camera/haptics |
| Performance/QA | full `performance-optimization`, `game-qa-playtest`, `gamedev-quality-gate` |
| Build/publish/liveops | full generic pipeline; partial platform SDK specifics |

## Platform x delivery

| Platform | Status and skills |
|---|---|
| Steam desktop | full generic `steam-publish`, `game-build-ci-cd` |
| itch.io/web | full `itch-publish`, web-engine skills |
| Mobile | full design/test intent; partial store-specific automation |
| Console | planned SDK-specific confidential tooling; generic gates apply |
| Roblox | partial platform-specific release; full runtime skills |

## Player topology x network/save/QA

| Topology | Status and skills |
|---|---|
| Single player | full `save-systems`, `game-save-migration`, QA |
| Local multiplayer | full input/accessibility/QA; partial engine device adapters |
| Online co-op | full authority/prediction/desync/save contracts |
| Competitive rollback | full `game-rollback-netcode`, anti-cheat, impairment tests |

The exact UI/VFX/feel responsibilities requested in the instruction are individually traceable by their same-named Skill directories. Accessibility and performance are selected in design routes and quality gates, not appended only at release.

## Language selection

`gamedev-language-selector` is always routed. Existing engines lock their supported primary language; new projects are compared using platform, engine ecosystem, performance, iteration speed, and team constraints. The Router returns the primary choice, alternatives, confidence, reasons, tradeoffs, and a validation spike. When evidence is insufficient it returns a shortlist rather than inventing certainty.
