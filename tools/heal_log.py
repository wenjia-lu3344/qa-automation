"""Append-only local repair audit log; never store secrets in notes."""
import argparse
import datetime as dt
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--script', required=True)
    parser.add_argument('--result', choices=['fixed', 'unresolved', 'not-locator'], required=True)
    parser.add_argument('--notes', default='')
    parser.add_argument('--path', type=Path, default=Path('docs/heal-audit.jsonl'))
    args = parser.parse_args()
    args.path.parent.mkdir(parents=True, exist_ok=True)
    record = {'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(), 'script': args.script,
              'result': args.result, 'notes': args.notes}
    with args.path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print('Audit record appended:', args.path)


if __name__ == '__main__':
    main()
