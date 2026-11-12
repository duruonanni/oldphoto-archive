import json
import re
import subprocess
from urllib.parse import unquote
from pathlib import Path

import pytest

from oldphoto_archive.build import build

ROOT = Path(__file__).resolve().parents[1]


def fixture_catalog(tmp_path, records, site=None):
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps({"site": site or {}, "photos": records}), encoding="utf-8")
    return p


def record(file="example-1.png", **changes):
    return dict(file=file, category="color", description="plain text", people=["A"], **changes)


def test_example_build_links_and_integrity(tmp_path):
    out = tmp_path / "site"
    result = build(ROOT / "examples/catalog.json", ROOT / "examples/photos", out)
    assert result["counts"] == {"color": 1, "bw": 1, "id": 1}
    manifest = json.loads((out / "manifest.json").read_text())
    assert len(manifest["files"]) == 7
    for name in manifest["files"]:
        assert (out / name).is_file()
    for h in out.glob("*.html"):
        markup = re.sub(r"<script>.*?</script>", "", h.read_text(), flags=re.S)
        for src in re.findall(r'src="([^"]+)"', markup):
            if src:
                assert (out / unquote(src)).is_file()


def test_private_record_is_not_copied(tmp_path):
    cat = fixture_catalog(tmp_path, [record(publish=False)])
    out = tmp_path / "site"
    assert build(cat, ROOT / "examples/photos", out)["counts"]["color"] == 0
    assert not (out / "photos/example-1.png").exists()
    assert "example-1.png" not in (out / "color.html").read_text()


@pytest.mark.parametrize("filename", ["../secret.png", "/etc/secret.png", "foo/../../secret.png", "x\\secret.png", "a.svg", "a/./b.png"])
def test_invalid_photo_path_rejected(tmp_path, filename):
    cat = fixture_catalog(tmp_path, [record(filename)])
    with pytest.raises(ValueError):
        build(cat, ROOT / "examples/photos", tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_symlink_escape_rejected(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    (tmp_path / "private.png").write_bytes(b"private")
    (images / "photo.png").symlink_to(tmp_path / "private.png")
    cat = fixture_catalog(tmp_path, [record("photo.png")])
    with pytest.raises(ValueError):
        build(cat, images, tmp_path / "out")


def test_input_and_existing_output_are_not_overwritten(tmp_path):
    cat = ROOT / "examples/catalog.json"
    images = ROOT / "examples/photos"
    for out in [images, images / "sub", ROOT / "examples"]:
        with pytest.raises(ValueError):
            build(cat, images, out)
    out = tmp_path / "existing"
    out.mkdir()
    sentinel = out / "keep"
    sentinel.write_text("original")
    with pytest.raises(ValueError):
        build(cat, images, out)
    assert sentinel.read_text() == "original"


def test_script_termination_and_html_are_escaped(tmp_path):
    payload = '</script><script>window.INJECTED=1</script><img src=x onerror="alert(1)">'
    cat = fixture_catalog(tmp_path, [{"file": "example-1.png", "category": "color", "description": payload, "people": [payload]}])
    out = tmp_path / "out"
    build(cat, ROOT / "examples/photos", out)
    content = (out / "color.html").read_text()
    scripts = re.findall(r"<script>(.*?)</script>", content, re.S)
    assert len(scripts) == 1
    assert payload not in scripts[0]
    assert json.loads(re.search(r"var ITEMS=(.*?);\s*\n", scripts[0]).group(1))[0][2] == payload
    js = tmp_path / "inline.js"
    js.write_text(scripts[0])
    subprocess.run(["node", "--check", str(js)], check=True, capture_output=True)


def test_empty_and_unlabelled_categories_have_render_target(tmp_path):
    cat = fixture_catalog(tmp_path, [{"file": "example-1.png", "category": "color", "people": []}])
    out = tmp_path / "out"
    build(cat, ROOT / "examples/photos", out)
    assert 'id="info"' in (out / "color.html").read_text()
    assert 'id="grid"' in (out / "bw.html").read_text()


def test_manifest_hashes_match(tmp_path):
    import hashlib

    out = tmp_path / "out"
    build(ROOT / "examples/catalog.json", ROOT / "examples/photos", out)
    for name, digest in json.loads((out / "manifest.json").read_text())["files"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest


def test_special_filename_url_maps_to_exported_image(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    name = "photo #1?100% 彩色.png"
    (images / name).write_bytes((ROOT / "examples/photos/example-1.png").read_bytes())
    cat = fixture_catalog(tmp_path, [record(name)])
    out = tmp_path / "out"
    build(cat, images, out)
    content = (out / "color.html").read_text()
    item = json.loads(re.search(r"var ITEMS=(.*?);\s*\n", content).group(1))[0]
    assert "#" not in item[0] and "?" not in item[0]
    assert unquote(item[0]) == "photos/" + name
    assert (out / unquote(item[0])).is_file()


@pytest.mark.parametrize("site", [{"covers": []}, {"people_order": {}}, {"title": []}, {"noindex": "false"}])
def test_invalid_site_config_rejected_before_output(tmp_path, site):
    cat = fixture_catalog(tmp_path, [record()], site)
    with pytest.raises(ValueError):
        build(cat, ROOT / "examples/photos", tmp_path / "out")
    assert not (tmp_path / "out").exists()
