# Repository guidance

Python async Playwright examples live under `examples/`. Execute with `python tools/heal_runner.py examples/<script>.py`. On failure inspect `_healing/<stem>/bundle.json` and use `.claude/skills/heal-locators/SKILL.md`. Never silently rewrite business assertions or push changes. Before changing code, explain the failure, show a minimal proposed locator diff, and obtain approval. This is a demo repository; do not submit credentials, session state or confidential traces.
