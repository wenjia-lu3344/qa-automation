# Development Roadmap — Playwright Locator Healing

## Overview

This roadmap outlines planned improvements to **Playwright Locator Healing**, a Python-based toolkit for capturing Playwright test failures, diagnosing locator problems, and proposing carefully controlled repairs.

The current implementation is a proof of concept. It supports a narrow set of button-role locators, local failure artifacts, human-reviewed repair proposals, and an opt-in repair-and-rollback pipeline. The goal of the next development cycle is to make the toolkit more reliable, extensible, and useful in real-world QA automation workflows **without changing test intent or silently applying unsafe fixes**.

**Estimated remaining development effort: 38–54 hours.** These are planning estimates, not completed or billed hours. Scope and estimates may be refined as implementation progresses.

| Phase | Focus | Estimated effort | Status |
| --- | --- | ---: | --- |
| 1 | Reliability & Safety | 6–8 hours | Planned |
| 2 | Locator Engine v2 | 10–14 hours | Planned |
| 3 | pytest Integration | 8–12 hours | Planned |
| 4 | Integration Testing & CI | 8–12 hours | Planned |
| 5 | Reporting & Documentation | 6–8 hours | Planned |
| **Total** | | **38–54 hours** | |

## Phase 1 — Reliability & Safety

**Estimated effort: 6–8 hours**  
**Goal:** Make failure handling, diagnosis, and authorized repairs deterministic and safe.

### Planned tasks

- [ ] Assign a unique run ID to every test execution and store artifacts in run-specific directories.
- [ ] Validate artifact freshness and provenance before generating a repair proposal; never use a stale `bundle.json` from an earlier run.
- [ ] Improve failure classification so locator-not-found errors, strict-mode violations, visibility/actionability problems, assertion failures, and infrastructure failures are not treated as interchangeable.
- [ ] Consolidate the approval, edit, rerun, and rollback steps into a clear, auditable workflow; ensure failed verification restores the original file.
- [ ] Add tests for missing/corrupted artifacts, stale source files, unsupported failures, interrupted repairs, and rollback behavior.
- [ ] Document local artifact retention and precautions for screenshots, page contents, session data, and secrets.

### Acceptance criteria

- A failed or incomplete capture cannot trigger a proposal based on an earlier run.
- Unsupported failure types do not result in source-code edits.
- A failed post-repair verification restores the original source content.
- Regression tests cover the primary failure and rollback paths.

## Phase 2 — Locator Engine v2

**Estimated effort: 10–14 hours**  
**Goal:** Support more realistic locator failures while retaining conservative safety checks.

### Planned tasks

- [ ] Extend diagnosis and repair proposals beyond single-line `get_by_role('button', name=...)` to selected `get_by_text`, `get_by_label`, `get_by_placeholder`, and `get_by_test_id` patterns.
- [ ] Explore support for common CSS locator patterns where safe, and explicitly report unsupported expressions.
- [ ] Replace fragile source-code regex replacement with Python AST-based detection or another syntax-aware approach that preserves unrelated code.
- [ ] Collect structured candidate information, including role, accessible name, test ID, visibility, and DOM context where available.
- [ ] Rank multiple candidate locators using transparent rules and explain why each candidate was suggested.
- [ ] Check candidate uniqueness against the live page when available; require human review when intended target semantics cannot be established.
- [ ] Add unit tests for ambiguous matches, duplicate names, multiline expressions, nested calls, and unsupported patterns.

### Acceptance criteria

- Supported locator types produce explainable suggestions in representative sample cases.
- Ambiguous or low-confidence candidates are reported rather than silently applied.
- Proposed changes affect only the intended locator expression.
- Passing a rerun alone is never presented as proof that a candidate is semantically correct.

## Phase 3 — pytest Integration

**Estimated effort: 8–12 hours**  
**Goal:** Integrate failure capture into everyday Python Playwright test suites.

### Planned tasks

- [ ] Prototype a pytest plugin or opt-in `conftest.py` integration using supported pytest hooks.
- [ ] Capture test identifiers, exceptions, and failure metadata without requiring each test to call `capture_in_context()` manually.
- [ ] Integrate with `pytest-playwright` fixtures where possible, and document limitations when the browser/page has already closed.
- [ ] Add configuration options for enabling capture, choosing output paths, and restricting sensitive artifacts.
- [ ] Keep repair suggestions separate from normal test execution; never edit test files just because a pytest run fails.
- [ ] Provide a minimal example project and tests showing successful capture and non-locator failure handling.

### Acceptance criteria

- A sample pytest-playwright suite can generate a useful failure bundle through an opt-in integration.
- Ordinary passing tests run without unexpected source modifications.
- Capture failures do not conceal or alter the original pytest failure result.

## Phase 4 — Integration Testing & CI

**Estimated effort: 8–12 hours**  
**Goal:** Verify the complete repair workflow against reproducible local browser scenarios.

### Planned tasks

- [ ] Create local HTML fixtures for renamed controls, multiple matching controls, missing elements, disabled/hidden elements, and unrelated assertion failures.
- [ ] Add end-to-end integration tests for capture → diagnosis → proposal → approved edit → rerun → rollback.
- [ ] Assert that unsupported or ambiguous cases do not modify test source files.
- [ ] Add regression coverage for stale artifacts, source changes between proposal and application, and failed reruns.
- [ ] Configure GitHub Actions to install dependencies, run unit tests, and run browser integration tests on pushes and pull requests.
- [ ] Document how to reproduce CI failures locally.

### Acceptance criteria

- Unit and browser integration tests run automatically in CI.
- The test suite exercises at least one successful approved repair and several safe-refusal scenarios.
- Any repair that fails verification is rolled back and recorded as unsuccessful.

## Phase 5 — Reporting & Documentation

**Estimated effort: 6–8 hours**  
**Goal:** Make the tool's behavior easier for QA engineers to understand, audit, and adopt.

### Planned tasks

- [ ] Enhance the HTML report with original and proposed locators, failure classification, verification outcome, and a readable diff.
- [ ] Improve audit-log structure with run IDs, timestamps, outcome categories, and links to local artifacts.
- [ ] Show summary metrics such as proposals generated, approved, rejected, verified, and rolled back; avoid misleading “healed” counts.
- [ ] Clarify installation steps, supported locator patterns, limitations, privacy considerations, and safety boundaries in the README.
- [ ] Add a practical walkthrough using local sample pages and troubleshooting guidance.
- [ ] Review and update English, Japanese, and Simplified Chinese documentation where applicable.

### Acceptance criteria

- Users can inspect what failed, what was proposed, what changed, and whether verification succeeded.
- The README provides a reproducible quick-start workflow.
- Documentation distinguishes supported features from planned capabilities.

## Development Principles

1. **Human approval first.** Repairs should remain opt-in and reviewable; no automatic push or pull request creation without explicit authorization.
2. **Do not change test intent.** Never “fix” a failing test by weakening assertions, bypassing access controls, or changing expected business behavior.
3. **Fail safely.** If evidence is incomplete or the intended element cannot be determined confidently, report the uncertainty and leave source files unchanged.
4. **Protect sensitive data.** Keep screenshots, traces, DOM snapshots, credentials, and authenticated session details local by default; never publish real customer data.
5. **Use measurable verification.** Prefer reproducible tests, observable diffs, and honest outcome reporting over claims of fully autonomous healing.

## Tracking Progress

Work will be tracked through repository commits and, where useful, GitHub Issues. Phase statuses and estimates will be updated as tasks are scoped and completed. This roadmap describes **future planned work**, not features already implemented.
