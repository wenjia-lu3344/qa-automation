# Playwright Locator Healing / Playwright 定位器自愈

A conservative Python Playwright failure-capture and AI-assisted locator-repair toolkit. **Not a fully autonomous self-healing agent:** the included proposal tool never changes source files without explicit approval.

- [中文说明](README.zh-CN.md)
- [日本語説明](README.ja.md)
- [English documentation](README.en.md)

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python tools/heal_runner.py examples/passing.py
python tools/heal_runner.py examples/failing_locator.py
python tools/repair_locator.py examples/_healing/failing_locator/bundle.json
pytest -q
```

`failing_locator.py` is supposed to fail, capture screenshots/ARIA/traceback, and exit nonzero. Read and verify the repair suggestion; the system must not blindly modify your test.

## Privacy
Never commit `_healing/`, screenshots, authenticated sessions, secrets, or test production credentials. A GitHub branch / PR should be created only after review.

## Bounded repair pipeline (dry-run by default)

```bash
python tools/heal_pipeline.py examples/failing_locator.py
# Review the proposal and test against the intended button before changing code.
# Recommended: duplicate the failing sample first to keep it failing in this repository.
python tools/heal_pipeline.py examples/failing_locator.py --apply
python -m pytest -q
```

`--apply` modifies only an explicitly supported, unambiguous, single-line button locator. It reruns the script and **rolls back if validation fails**. Never use `--apply` blindly on a real system. See [implementation improvements](docs/IMPROVEMENTS.md).

Screenshot-inspired entry point: `python tools/heal_runner.py demo.py` (expected failure). Other samples include `examples/failing_strict_mode.py` (ambiguous locator, never blind-repair).

## Upload to your own GitHub repository

```bash
git init
git branch -M main
git add .
git commit -m "feat: add Playwright locator healing toolkit"
git remote add origin https://github.com/wenjia-lu3344/qa-automation.git
git push -u origin main
```

Run the commands **inside the extracted `qa-automation` folder**. If `origin` or `main` already exist, inspect first; do not blindly overwrite history.
