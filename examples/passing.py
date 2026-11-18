"""Passing local example: no internet, credentials, or external application needed."""
import asyncio
import os
from playwright.async_api import async_playwright

HTML = '<h1>ログイン</h1><button data-locator-id="submit-btn">送信する</button>'


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH") or None)
        try:
            page = await browser.new_page()
            await page.set_content(HTML)
            await page.get_by_role('button', name='送信する').click()
            print('PASS: button clicked')
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
