"""Intentionally ambiguous role locator: two matching buttons, not a safe auto-repair."""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from tools.heal_runner import capture_in_context


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH') or None)
        try:
            page = await browser.new_page()
            await page.set_content('<button>Save</button><button>Save</button>')
            try:
                await page.get_by_role('button', name='Save').click(timeout=1500)
            except Exception as exc:
                await capture_in_context(exc, Path(__file__))
                raise
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
