"""Apply an explicitly approved, single-line locator change safely."""
import argparse
import json
from pathlib import Path


def apply(path: Path, proposal: dict) -> None:
    if proposal.get('status') != 'proposal':
        raise ValueError('not an actionable proposal')
    if path.suffix != '.py':
        raise ValueError('target must be a Python script')
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines(keepends=True)
    n = proposal['line'] - 1
    if n < 0 or n >= len(lines) or lines[n].rstrip('\r\n') != proposal['old_code']:
        raise ValueError('source has changed; refusing unsafe replacement')
    ending = '\r\n' if lines[n].endswith('\r\n') else ('\n' if lines[n].endswith('\n') else '')
    lines[n] = proposal['new_code'] + ending
    path.write_text(''.join(lines), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('script', type=Path)
    parser.add_argument('proposal', type=Path)
    parser.add_argument('--approve', action='store_true', help='explicitly apply the proposed change')
    args = parser.parse_args()
    proposal = json.loads(args.proposal.read_text(encoding='utf-8'))
    print(json.dumps(proposal, ensure_ascii=False, indent=2))
    if not args.approve:
        print('DRY RUN: no files changed. Use --approve after reviewing the proposal.')
        return 0
    apply(args.script, proposal)
    print('Approved locator edit applied. Re-run the test to verify.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
