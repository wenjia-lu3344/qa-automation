"""Conservative locator repair proposal tool. No automatic edits by default.

Suggest a replacement for an exact get_by_role(button, name=...) expression
using the captured ARIA snapshot. The proposal remains subject to review.
"""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import re

ROLE_CALL = re.compile(r'get_by_role\(\s*[\'\"]button[\'\"]\s*,\s*name\s*=\s*([\'\"])(.*?)\1\s*\)')
BUTTON_LINE = re.compile(r'^\s*- button ["\']([^"\']+)["\']', re.MULTILINE)


def propose(source: str, snapshot: str, line_number: int) -> dict:
    lines = source.splitlines()
    if not 1 <= line_number <= len(lines):
        return {'status': 'unsupported', 'reason': 'line number is outside the file'}
    line = lines[line_number - 1]
    found = ROLE_CALL.search(line)
    if not found:
        return {'status': 'unsupported', 'reason': 'only single-line button role locators are supported'}
    old = found.group(2)
    candidates = BUTTON_LINE.findall(snapshot)
    # Automated proposals are intentionally limited to pages with exactly one button.
    # Multiple buttons (including duplicate names) require semantic review.
    if len(candidates) != 1:
        return {'status': 'ambiguous', 'original': old, 'candidates': candidates, 'reason': 'more than one button or no buttons in snapshot'}
    choices = difflib.get_close_matches(old, candidates, n=2, cutoff=0.35)
    if len(choices) != 1:
        return {'status': 'ambiguous', 'original': old, 'candidates': choices, 'reason': 'no unique plausible replacement'}
    new = choices[0]
    if old == new:
        return {'status': 'unsupported', 'reason': 'original locator already matches the snapshot'}
    updated_line = line[:found.start(2)] + new + line[found.end(2):]
    return {'status': 'proposal', 'original': old, 'suggested': new,
            'line': line_number, 'old_code': line, 'new_code': updated_line,
            'warning': 'Verify uniqueness and semantics in a live browser before applying.'}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('bundle', type=Path)
    args = p.parse_args()
    metadata = json.loads(args.bundle.read_text(encoding='utf-8'))
    script = Path(metadata.get('failing_file') or '')
    snap = args.bundle.parent / 'aria_snapshot.yaml'
    if not script.is_file() or not snap.is_file():
        print(json.dumps({'status': 'unsupported', 'reason': 'missing source or ARIA snapshot'}))
        return 2
    result = propose(script.read_text(encoding='utf-8'), snap.read_text(encoding='utf-8'), metadata['failing_line'])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'proposal' else 2


if __name__ == '__main__':
    raise SystemExit(main())
