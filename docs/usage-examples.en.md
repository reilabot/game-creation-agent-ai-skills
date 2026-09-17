# Usage Examples

Analyze and route a goal:

```powershell
python scripts/gamedev_router.py "Steam向け4人協力型オープンワールド・サバイバル。建築、クラフト、戦闘、敵AI、永続セーブ、専用サーバー" --engine unreal
```

Then ask the agent to use `game-studio-director` and implement only the first playable increment. The response should identify engine evidence, selected skills, dependency order, model capability classes, observation tools, and quality gates.

Other dry-run goals:

- `Godot 2D pixel art roguelite with procedural rooms and persistent unlocks`
- `Unity mobile idle RPG with touch UI, offline progress, and accessible settings`
- `low-end WebGL action game with responsive HUD, input latency budget, and reduced VFX`
