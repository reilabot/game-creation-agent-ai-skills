# Validation Report

Validation date: 2026-09-17 (Asia/Tokyo)

| Check | Result | Evidence |
|---|---|---|
| Skill syntax/frontmatter/naming | PASS | Official `quick_validate.py`: 109/109 passed with UTF-8 mode |
| Local structure, duplicate names/descriptions | PASS | `python scripts/validate_stack.py`: 109 skills, 0 errors |
| Relative links and required files | PASS | Local validator; file-like relative links resolve |
| Route references and circular orchestration | PASS | All configured skill references exist; orchestration is one-way to the quality gate |
| Router fixtures | PASS | 17/17, including eight engine/genre cases, five UI/VFX/feel cases, and four language-selection cases |
| Over-routing guard | PASS | Every fixture selected at most 18 skills |
| Clean reproduction | PASS | Pinned archive SHA-256 `ab6762d63dc829d2d69f5a562fa5b7ca4942db9ef738c801b5167431f585df45`; clean install produced 109 skills including the language selector |
| License and attribution | PASS | `docs/source-lock.md` and `THIRD_PARTY_NOTICES.md` present; 28 external skills locked to one Apache-2.0 commit |
| Secret/dangerous literal scan | PASS | No credential-like fixed literal found in Skill files; mutation boundaries documented |
| Codex/Antigravity layout | PASS with note | Canonical `.agents/skills`; Antigravity fallback described in installation docs |
| Representative GOAL dry runs | PASS | Unreal co-op survival selects C++; browser selects TypeScript; an under-specified strategy goal returns a shortlist instead of guessing |

Commands executed:

```powershell
$env:PYTHONUTF8='1'
python scripts/validate_stack.py
python <path-to-skill-creator>/scripts/quick_validate.py <each-skill-directory>
python scripts/install_stack.py --verify-only
python scripts/gamedev_router.py <goal> [--engine <engine>]
```

Observed limitations: console SDK/store procedures remain planned because they require platform-confidential tooling; mobile store automation, advanced pygame/LÖVE UI adapters, and custom-engine platform adapters are partial. No live engine/editor project was present, so this validation proves the Skill stack and router rather than an engine build or authenticated editor integration.
