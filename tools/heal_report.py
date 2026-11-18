"""Render a small local HTML report from JSONL audit history."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=Path, default=Path('docs/heal-audit.jsonl'))
    parser.add_argument('--out', type=Path, default=Path('docs/heal-report.html'))
    args = parser.parse_args()
    entries = [json.loads(s) for s in args.log.read_text(encoding='utf-8').splitlines() if s.strip()] if args.log.exists() else []
    rows = ''.join('<tr>' + ''.join('<td>' + html.escape(str(e.get(k, ''))) + '</td>' for k in ('timestamp', 'script', 'result', 'notes')) + '</tr>' for e in entries)
    result = '<!doctype html><meta charset="utf-8"><title>Healing audit</title><h1>Locator healing audit</h1><table border="1"><tr><th>Time</th><th>Script</th><th>Result</th><th>Notes</th></tr>' + rows + '</table>'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(result, encoding='utf-8')
    print(args.out)


if __name__ == '__main__':
    main()
