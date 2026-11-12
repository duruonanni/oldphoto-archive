"""Optional actual browser check; opens local files, not a production service."""
import json
import os
from pathlib import Path

import pytest

from oldphoto_archive.build import build

pytestmark = pytest.mark.skipif(os.environ.get("RUN_BROWSER_TESTS") != "1", reason="browser opt-in")


def test_filters_pagination_lightbox_and_injection(tmp_path):
    from playwright.sync_api import sync_playwright

    root = Path(__file__).resolve().parents[1]
    # Reuse image bytes with different file names to exercise pagination.
    images = tmp_path / "images"
    images.mkdir()
    records = []
    for i in range(14):
        name = f"{i}.png"
        (images / name).write_bytes((root / "examples/photos/example-1.png").read_bytes())
        records.append({"file": name, "category": "color", "description": '<img src=x onerror="window.INJECTED=1">', "people": ["A", "B"] if i == 0 else ["A"]})
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"photos": records}))
    out = tmp_path / "out"
    build(catalog, images, out)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto((out / "color.html").as_uri())
        assert page.locator(".card").count() == 12
        assert page.locator(".desc img").count() == 0
        assert page.evaluate("window.INJECTED || null") is None
        page.locator(".pager button").last.click()
        assert page.locator(".card").count() == 2
        page.locator('[data-v="A"] input').check()
        page.locator('[data-v="B"] input').check()
        assert page.locator(".card").count() == 1
        page.locator(".card").click()
        assert page.locator("#lightbox").is_visible()
        page.keyboard.press("Escape")
        assert not page.locator("#lightbox").is_visible()
        assert not errors
        browser.close()
