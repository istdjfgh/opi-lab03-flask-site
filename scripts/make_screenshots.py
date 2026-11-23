"""Знімає скриншоти сторінок для звіту (lab-reports/screenshots).

Запуск: python scripts/make_screenshots.py
Потрібні: pip install playwright (браузер — вбудований Chromium або встановлений Chrome).
"""
import os
import sys
import threading

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import app  # noqa: E402

OUT = os.path.join(ROOT, 'lab-reports', 'screenshots')
PAGES = [('home', '/'), ('catalog', '/catalog'), ('game', '/catalog/pandemic'),
         ('about', '/about'), ('delivery', '/delivery'), ('contacts', '/contacts'), ('404', '/catalog/xyz')]


def launch(playwright):
    try:
        return playwright.chromium.launch()
    except Exception:
        return playwright.chromium.launch(channel='chrome')


def main():
    os.makedirs(OUT, exist_ok=True)
    server = make_server('127.0.0.1', 0, app)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'

    with sync_playwright() as p:
        browser = launch(p)
        desktop = browser.new_page(viewport={'width': 1440, 'height': 900})
        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        for name, path in PAGES:
            desktop.goto(base + path)
            desktop.screenshot(path=os.path.join(OUT, f'{name}-desktop.png'), full_page=True)
            mobile.goto(base + path)
            mobile.screenshot(path=os.path.join(OUT, f'{name}-mobile.png'))
            print('✓', name)

        # Відкрите мобільне меню («бургер»)
        mobile.goto(base + '/')
        mobile.click('label.nav-burger')
        mobile.wait_for_timeout(300)
        mobile.screenshot(path=os.path.join(OUT, 'menu-mobile.png'))
        print('✓ menu-mobile')
        browser.close()
    server.shutdown()


if __name__ == '__main__':
    main()
