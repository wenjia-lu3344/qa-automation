# Design changes / 设计改进记录 / 設計改善記録

This repository was reconstructed from user-provided screenshots, **not** copied byte-for-byte from complete original source files. Missing reference files are independently documented. Below are deliberate deviations and reasons.

| Screenshot concept | Implemented change | Reason / 目的 |
|---|---|---|
| `heal_runner.py` monkey-patches private Playwright context manager | Public Playwright API + explicit `capture_in_context()` during `except`, before browser shutdown | Avoid fragile internal monkey patches and losing the live page before capture. Tests must opt in to this capture pattern. |
| Force CDP port `9222` on all Chromium instances | CDP disabled by default; optional read-only, explicitly approved inspection in Skill | Avoid exposing an unauthenticated debugging interface or leaking session state. |
| Hook detects any Python failure | Hook only gives extra context; Python pipeline separately checks error class, message, file and exact failing line | Do not auto-fix assertions, infrastructure issues or unrelated business failures. |
| Agent autonomously changes locator across many files | Deterministic proposal for a narrow `get_by_role('button', name=...)` case; only one button in snapshot; one-line edit, stale-source check | A snapshot cannot prove semantics or uniqueness on a changing UI. Cross-file matches are only reported. |
| Autonomous broad repair & push | Default dry-run. `--apply` explicitly authorizes local change, requires successful rerun, reverts on failed validation; git operations are manual | Prevent surprise modifications, minimize blast radius, preserve review. |
| Eight/nine-phase workflow depends on missing referenced helpers | Added locally runnable capture / proposal / apply / report tools and a portable Skill with documented optional phases | Make a working example instead of referencing missing files. |
| Manual failure data handling | `.gitignore` excludes captures and local audit outputs | Screenshots, DOM, traces and URLs may expose secrets. |
| Failure reported only as a passing shell command when swallowed | Keep non-zero exit for failures and check `bundle.json` | Do not misrepresent a failed test as passing. |
| No sample distinction | Added passing, wrong-locator and non-locator assertion samples | Prove positive, negative and refusal-to-heal behavior. |

## Proof and limitations

- `python -m pytest -q`: unit tests for proposal guards, stale edits and hook detection.
- Browser smoke test using local Chromium: `passing.py` passed; wrong locator produced ARIA/screenshot/traceback; opt-in pipeline applied a unique locator change and passed rerun; assertion failure was captured but not proposed as a locator fix.
- This is a **bounded self-healing demonstration**, not a generic autonomously safe website fixer. It does **not** guarantee repair on arbitrary sites, multi-control pages, dynamic forms, or live authenticated sessions.
- Full Claude Code / MCP / GitHub PR execution was **not** validated in this runtime; Claude Code is an optional advisory orchestration integration.
