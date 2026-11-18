"""Opt-in bounded repair workflow: reproduce -> propose -> approve -> edit -> rerun -> rollback.

Only a narrow, reviewable locator change is allowed. Default is dry-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

try:
    from tools.repair_locator import propose
    from tools.apply_repair import apply
except ModuleNotFoundError:
    from repair_locator import propose
    from apply_repair import apply


def run_script(script: Path, root: Path) -> int:
    return subprocess.run([sys.executable, str(root / 'tools/heal_runner.py'), str(script)], cwd=root, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path, help='Existing Python Playwright test script')
    parser.add_argument('--apply', action='store_true', help='Explicitly approve one guarded locator repair')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    script = args.script.resolve()
    if not script.is_file() or script.suffix != '.py':
        parser.error('script must be an existing .py file')
    if not script.is_relative_to(root):
        parser.error('only files within this project may be edited')
    initial = run_script(script, root)
    if initial == 0:
        print('[HEAL] Already passing; no changes.')
        return 0
    bundle_path = script.parent / '_healing' / script.stem / 'bundle.json'
    if not bundle_path.exists():
        print('[HEAL] No failure bundle; refusing repair.')
        return 2
    bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
    error = str(bundle.get('error_message', ''))
    if bundle.get('error_type') not in ('TimeoutError', 'Error') or not any(x in error.lower() for x in ('locator', 'waiting for get_by_role', 'strict mode violation')):
        print('[HEAL] Failure is not a verified locator failure; refusing repair.')
        return 2
    if Path(bundle.get('failing_file', '')).resolve() != script:
        print('[HEAL] Failing location is not the target script; refusing repair.')
        return 2
    snapshot_path = bundle_path.parent / 'aria_snapshot.yaml'
    if not snapshot_path.exists():
        print('[HEAL] Missing ARIA snapshot; refusing repair.')
        return 2
    proposal = propose(script.read_text(encoding='utf-8'), snapshot_path.read_text(encoding='utf-8'), bundle.get('failing_line', -1))
    print(json.dumps(proposal, ensure_ascii=False, indent=2))
    if proposal.get('status') != 'proposal':
        print('[HEAL] No safe unique candidate; leaving files unchanged.')
        return 2
    (bundle_path.parent / 'proposal.json').write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding='utf-8')
    if not args.apply:
        print('[HEAL] DRY RUN. Review the proposal and rerun with --apply to try it.')
        return 0
    original = script.read_bytes()
    try:
        apply(script, proposal)
        print('[HEAL] Repair applied; rerunning test for validation.')
        status = run_script(script, root)
        if status:
            script.write_bytes(original)
            print('[HEAL] Validation failed; restored original script.')
            return 3
        print('[HEAL] VERIFIED: script passed after approved locator change. Review git diff before committing.')
        return 0
    except BaseException:
        script.write_bytes(original)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
