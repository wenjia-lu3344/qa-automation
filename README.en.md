# Python Playwright Locator Healing

This project demonstrates failure capture, conservative locator diagnosis, optional Claude Code orchestration, and human-approved repair. It is designed for local demo HTML, not a live banking site.

## Install

Python 3.10+ recommended. Run:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Examples

```bash
python tools/heal_runner.py examples/passing.py             # expected exit 0
python tools/heal_runner.py examples/failing_locator.py     # expected exit 1
python tools/heal_runner.py examples/failing_assertion.py   # expected exit 1, do NOT repair locator
```

The failing example explicitly captures artifacts before closing the browser. Inspect `examples/_healing/failing_locator/bundle.json`, `aria_snapshot.yaml`, `screenshot.png`, and `traceback.txt`. `python tools/repair_locator.py examples/_healing/failing_locator/bundle.json` prints a **proposal only**. Recheck correctness and uniqueness in a live page. To apply manually, save the JSON output to `proposal.json` and run `python tools/apply_repair.py examples/failing_locator.py proposal.json --approve`. Then rerun tests and verify their intended assertions. Avoid applying the demo repair if you want to keep the intentionally failing sample.

## Claude Code

`.claude/settings.json` installs a `PostToolUse` hook that detects failure output and supplies a prompt to follow `.claude/skills/heal-locators/SKILL.md`. Hook support and invocation vary by Claude Code version. The hook is advisory and never modifies source code. The skill describes 9 phases (0–8): run, diagnose, optional live verify, repair, scan, retest, log/report, branch/PR, improve.

## Constraints and security

- The baseline runner cannot guarantee snapshot capture after a script has closed its browser; use `capture_in_context` as in the failing examples.
- No unconditional monkey patches of Playwright internals and no default CDP debug port.
- Proposal tool covers simple, single-line `get_by_role('button', name='...')` calls only; not a general locator synthesis engine.
- No auto edit, auto push, or auto PR. Store all traces locally, verify before sharing, never store secrets.
- A passing test is not proof of semantic correctness. Review code and actual page interactions.

## Tests

`pytest -q` tests the pure-Python proposal, stale-edit guard, and hook. Browser integration requires Chromium installed and a runnable environment.

## Integrated guarded repair (dry-run by default)

```bash
python tools/heal_pipeline.py examples/failing_locator.py
# Review semantic correctness and exact target identity first.
python tools/heal_pipeline.py examples/failing_locator.py --apply
python -m pytest -q
```

`--apply` explicitly authorizes a narrowly supported single-line button locator edit after a unique candidate is inferred. The pipeline reruns the test and restores original bytes if verification fails. Make a copy of the intentionally failing sample before trying an edit if you want to preserve the example. This is **not** a general autonomous repair system; live semantics must still be reviewed. See [design changes](docs/IMPROVEMENTS.md).
