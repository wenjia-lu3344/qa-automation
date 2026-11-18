# Live verification

ARIA snapshots are observations at one moment, not proof that a suggested selector targets the correct control. If a CDP-connected browser is available and user-approved, inspect its live DOM, confirm candidate count is exactly one, its label/function matches test intent, and it is actionable. Avoid opening CDP on public interfaces; use localhost and a dedicated disposable profile. If live inspection is unavailable, clearly label the proposal unverified and request human review.
