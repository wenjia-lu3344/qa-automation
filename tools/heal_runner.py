"""Run an async Python Playwright script and collect failure artifacts.

Usage: python tools/heal_runner.py examples/failing_locator.py [--hold 0]
Note: scripts should create a global `page`, or call register_page(page).
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
import runpy
import sys
import traceback
from types import TracebackType
from typing import Any

ACTIVE_PAGE: Any = None


def register_page(page: Any) -> None:
    """Preferred, explicit page registration for reliable failure capture."""
    global ACTIVE_PAGE
    ACTIVE_PAGE = page


def _page_from_traceback(tb: TracebackType | None) -> Any:
    from playwright.async_api import Page
    while tb:
        for namespace in (tb.tb_frame.f_locals, tb.tb_frame.f_globals):
            for obj in namespace.values():
                if isinstance(obj, Page):
                    return obj
        tb = tb.tb_next
    return ACTIVE_PAGE


def _failure_line(tb: TracebackType | None, script: Path) -> tuple[str | None, int | None]:
    hits = traceback.extract_tb(tb)
    for frame in reversed(hits):
        if Path(frame.filename).resolve() == script:
            return str(script), frame.lineno
    for frame in reversed(hits):
        if 'site-packages' not in frame.filename and 'asyncio' not in frame.filename:
            return frame.filename, frame.lineno
    return None, None


async def _capture(exc: BaseException, tb: TracebackType | None, script: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    page = _page_from_traceback(tb)
    file, line = _failure_line(tb, script)
    metadata: dict[str, Any] = {
        'script': str(script), 'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'error_type': type(exc).__name__, 'error_message': str(exc),
        'failing_file': file, 'failing_line': line, 'page_url': None,
        'artifacts': {}, 'capture_errors': [],
    }
    (output / 'traceback.txt').write_text(''.join(traceback.format_exception(type(exc), exc, tb)), encoding='utf-8')
    metadata['artifacts']['traceback'] = 'traceback.txt'
    if page is not None:
        try:
            metadata['page_url'] = page.url
        except Exception as err:
            metadata['capture_errors'].append(f'url: {err}')
        try:
            if hasattr(page.locator('body'), 'aria_snapshot'):
                snap = await page.locator('body').aria_snapshot(timeout=3000)
                (output / 'aria_snapshot.yaml').write_text(snap, encoding='utf-8')
                metadata['artifacts']['aria_snapshot'] = 'aria_snapshot.yaml'
            else:
                html = await page.content()
                (output / 'dom.html').write_text(html, encoding='utf-8')
                metadata['artifacts']['dom'] = 'dom.html'
        except Exception as err:
            metadata['capture_errors'].append(f'snapshot: {err}')
            try:
                (output / 'dom.html').write_text(await page.content(), encoding='utf-8')
                metadata['artifacts']['dom'] = 'dom.html'
            except Exception as fallback_err:
                metadata['capture_errors'].append(f'dom: {fallback_err}')
        try:
            await page.screenshot(path=str(output / 'screenshot.png'), timeout=3000)
            metadata['artifacts']['screenshot'] = 'screenshot.png'
        except Exception as err:
            metadata['capture_errors'].append(f'screenshot: {err}')
    (output / 'bundle.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'[HEAL] FAILURE CAPTURED: {output / "bundle.json"}', flush=True)
    print(f'[HEAL] failing_at: {file}:{line}', flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path)
    parser.add_argument('--hold', type=int, default=0, help='Seconds to keep context open after failure (optional)')
    args = parser.parse_args(argv)
    if args.hold < 0:
        parser.error('--hold must be >= 0')
    script = args.script.resolve()
    if not script.is_file() or script.suffix != '.py':
        parser.error('script must be an existing .py file')
    output = script.parent / '_healing' / script.stem
    os.chdir(script.parent)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script)]
    os.environ.pop('QA_HEAL_CAPTURED', None)
    try:
        runpy.run_path(str(script), run_name='__main__')
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException as exc:
        # asyncio.run in a script may close the page before this handler runs.
        # Prefer exception capture while the browser is still open: see examples.
        if os.environ.get('QA_HEAL_CAPTURED') != '1':
            asyncio.run(_capture(exc, exc.__traceback__, script, output))
        traceback.print_exception(exc)
        return 1
    return 0


async def capture_in_context(exc: BaseException, script: str | Path) -> None:
    """Call inside the browser's async context *before* the page closes."""
    path = Path(script).resolve()
    await _capture(exc, exc.__traceback__, path, path.parent / '_healing' / path.stem)
    os.environ['QA_HEAL_CAPTURED'] = '1'


if __name__ == '__main__':
    raise SystemExit(main())
