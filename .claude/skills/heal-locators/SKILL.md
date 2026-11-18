---
name: heal-locators
description: Diagnose Playwright Python locator failures from failure artifacts, propose small locator-only edits, and verify the outcome. Never guess when evidence is insufficient.
---

# Locator healing workflow

## Rules
- Use `tools/heal_runner.py` for script execution and inspect `_healing/<script-stem>/bundle.json`.
- Do not confuse locator failures with assertion failures, disabled elements, test-data issues, navigation or infrastructure failures.
- Do not alter assertions, URLs, data, timing, access controls, or test intent to make a test pass.
- Do not push, open a PR, or modify branches without explicit user approval.
- Preserve evidence; never commit screenshots, traces, session data or `_healing/`.
- Show the precise proposed diff before applying; require user approval for edits.
- Optional live CDP inspection is only permitted when explicitly enabled and authenticated sessions are safe to inspect.

## Phase 0: Execute
Run `python tools/heal_runner.py examples/failing_locator.py`. If it passes, stop.

## Phase 1: Diagnose
Read the bundle, traceback, source line, aria_snapshot.yaml / dom.html and screenshot. Report whether this is definitively a locator problem. If not, stop and report.

## Phase 2: Live verification (optional)
Only if the browser is still available: compare candidates in live DOM and confirm exact uniqueness and intended target. Do not assume that a snapshot alone proves a match. See `references/live-verification.md`.

## Phase 3: Propose and repair
Run `python tools/repair_locator.py path/to/bundle.json`. Inspect the candidate; if ambiguous, stop. Make a minimal locator-only edit after explicit approval. Prefer stable test-id or role+accessible-name when verified. See `references/locator-selection.md`.

## Phase 4: Cross-file scan
Search other examples for identical broken patterns and REPORT other matches. Never change them automatically.

## Phase 5: Verify
Re-run the same failing test and inspect the output. A successful command is a necessary but not sufficient condition; verify that the intended control was tested. Limit retry attempts.

## Phase 6: Log and report
Append a log with `python tools/heal_log.py --script ... --result fixed --notes ...`. Build HTML with `python tools/heal_report.py`.

## Phase 7: Version control
Only after approval, create a feature branch and proposed commit/PR. Never force push or push directly to main.

## Phase 8: Improvement
Document suggested changes to this skill. Do not self-edit guardrails or automation instructions without explicit authorization. See `references/self-improvement.md`.
