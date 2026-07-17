from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
    page = browser.new_page()
    stealth_sync(page)
    print("Navigating...")
    page.goto("https://tma.foxigrow.com")
    print("Waiting...")
    time.sleep(10)
    page.screenshot(path="test.png")
    print("Done")
