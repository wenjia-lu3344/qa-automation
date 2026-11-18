# Locator selection and scope

Use explicit, accessible semantics in this order where appropriate:
1. Stable, verified test id (`get_by_test_id`) when configured and supported.
2. Verified role + accessible name (`get_by_role`).
3. Verified label or visible text.
4. CSS only as a last resort.

Never use positional `.first()` or XPath to conceal ambiguity. Preserve intent and confirm uniqueness on the current page. Fix one failing locator at a time, keep the diff minimal, and report similar occurrences without editing them.
