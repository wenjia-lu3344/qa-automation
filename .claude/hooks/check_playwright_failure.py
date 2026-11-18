"""Claude Code PostToolUse hook. Emits context; never changes exit status or files."""
import json
import sys

MARKERS = ('[HEAL] FAILURE CAPTURED', 'TimeoutError', 'strict mode violation')


def check(payload: dict) -> dict | None:
    if payload.get('tool_name') != 'Bash':
        return None
    command = str((payload.get('tool_input') or {}).get('command', ''))
    if 'heal_runner.py' not in command and not command.strip().endswith('.py') and not command.strip().startswith('python'):
        return None
    response = payload.get('tool_response') or {}
    text = '\n'.join(str(response.get(k, '')) for k in ('stdout', 'stderr', 'output', 'error', 'message', 'result', 'text'))
    if not any(marker in text for marker in MARKERS):
        return None
    return {'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext':
            'Playwright failure detected. Read the artifacts under _healing/<script-stem>/ and consult the heal-locators skill. Diagnose before changing any code; never auto-push.'}}


def main() -> int:
    try:
        result = check(json.load(sys.stdin))
        if result:
            print(json.dumps(result, ensure_ascii=False))
    except (Exception, KeyboardInterrupt):
        pass  # hooks must not block the user's normal workflow
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
