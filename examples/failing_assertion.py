"""Intentionally failing non-locator case; should NOT be auto-repaired."""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from tools.heal_runner import capture_in_context


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH") or None)
        try:
            page = await browser.new_page()
            await page.set_content('<h1>Ready</h1>')
            try:
                assert 1 == 2, 'intentional business assertion failure'
            except Exception as exc:
                await capture_in_context(exc, Path(__file__))
                raise
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
