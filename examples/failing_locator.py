"""Intentionally failing locator; capture artifacts *before* context closes."""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from tools.heal_runner import capture_in_context

HTML = '<h1>ログイン</h1><button data-locator-id="submit-btn">送信する</button>'


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH") or None)
        try:
            page = await browser.new_page()
            await page.set_content(HTML)
            try:
                await page.get_by_role('button', name='登録する').click(timeout=1800)
            except Exception as exc:
                await capture_in_context(exc, Path(__file__))
                raise
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
