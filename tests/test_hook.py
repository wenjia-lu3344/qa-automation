import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('hook', Path(__file__).resolve().parents[1] / '.claude/hooks/check_playwright_failure.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def test_hook_detects_failure():
    assert hook.check({'tool_name': 'Bash', 'tool_input': {'command': 'python tools/heal_runner.py examples/failing_locator.py'}, 'tool_response': {'stdout': '[HEAL] FAILURE CAPTURED'}})


def test_hook_ignores_other_command():
    assert hook.check({'tool_name': 'Bash', 'tool_input': {'command': 'echo test'}, 'tool_response': {'stdout': 'TimeoutError'}}) is None
