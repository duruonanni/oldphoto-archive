# Oldphoto Archive

Generate a static family photo website from a JSON catalog and local images. Browsers need no AI service, database or login. The example contains only generated geometric pictures and fictional labels.

## Quick start

Requires Python 3.10+. The generator uses only the standard library.

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/python -m oldphoto_archive --catalog examples/catalog.json --images examples/photos --output out/example
.venv/bin/python -m http.server 8010 --bind 127.0.0.1 --directory out/example
```

Open `http://127.0.0.1:8010`. The output directory must not already exist; use a fresh path for another build. A no-install alternative is `PYTHONPATH=src python3 -m oldphoto_archive ...` with the same arguments.

## Catalog

See `examples/catalog.json`. `site` configures title, subtitle, introduction, footer, noindex, people order and optional category cover file names. Each photo has a relative `file`, category (`color`, `bw`, `id`), plain-text description and a list of people. Set `publish: false` to omit both the record and its image from the new output. Subdirectories are supported; source images must remain inside the images directory.

Store your real catalog and photographs under ignored `data/` or outside the repository. A public website and an open-source program are different publications: MIT covers the program and synthetic examples, not your personal photographs or descriptions.

## Features and limitations

Available: category pages, 12-item pagination, AND person filtering, lightbox and keyboard navigation, safe text rendering, image copying and SHA-256 output manifest. Output contains no runtime Python code or database connection. Empty categories are supported.

Not included: photo scanning, recognition, Immich authentication/database writeback, automatic content synchronization, user accounts or an automatic production deployer. Export any upstream source into the documented catalog format first. Only known raster-image extensions are accepted; the generator is not an image sanitizer and does not strip EXIF. Use trusted, appropriately prepared images. The output is public unless your hosting layer adds authentication.

## Tests

```bash
.venv/bin/python -m pytest -q
# Optional browser test (uses file://, no server required):
playwright install chromium
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py
```

## Layout

`src/oldphoto_archive/`: generator and templates; `examples/`: synthetic catalog/images; `tests/`: behavior and boundary tests; `deploy/`: nginx template and repository-first release workflow; `docs/reviews/`: sanitized acceptance evidence. `data/` is private and `out/` is generated; neither belongs in Git.

## License

MIT. Adapted from a personal archive generator; no personal catalog, family photos, credentials or original Git history are distributed.
