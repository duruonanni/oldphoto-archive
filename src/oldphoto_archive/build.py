"""Build a self-contained static archive from a local, explicit catalog."""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from .template import page

CATEGORIES = {"color": "彩色", "bw": "黑白", "id": "证件照"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def read_catalog(path):
    document = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict):
        raise ValueError("catalog must be an object")
    config, records = document.get("site", {}), document["photos"]
    if not isinstance(config, dict) or not isinstance(records, list):
        raise ValueError("site must be an object and photos must be a list")
    for key in ["title", "subtitle", "intro", "footer"]:
        if key in config and not isinstance(config[key], str):
            raise ValueError(f"site.{key} must be a string")
    order, covers = config.get("people_order", []), config.get("covers", {})
    if not isinstance(order, list) or any(not isinstance(name, str) for name in order):
        raise ValueError("site.people_order must be a list of strings")
    if not isinstance(covers, dict) or any(k not in CATEGORIES or not isinstance(v, str) for k, v in covers.items()):
        raise ValueError("site.covers must map category names to file names")
    if "noindex" in config and not isinstance(config["noindex"], bool):
        raise ValueError("site.noindex must be a boolean")
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("photo records must be objects")
        name = record["file"]
        if not isinstance(name, str) or not name:
            raise ValueError("photo file must be a nonempty string")
        rel = PurePosixPath(name)
        if rel.is_absolute() or any(p in {"", ".", ".."} for p in name.split("/")) or "\\" in name:
            raise ValueError("photo path must stay within the image directory")
        if rel.suffix.lower() not in IMAGE_SUFFIXES or name in seen:
            raise ValueError("unsupported or duplicate photo file")
        seen.add(name)
        if not isinstance(record["category"], str) or record["category"] not in CATEGORIES:
            raise ValueError("category must be color, bw or id")
        if "publish" in record and not isinstance(record["publish"], bool):
            raise ValueError("publish must be a boolean")
        if not isinstance(record.get("description", ""), str):
            raise ValueError("description must be a string")
        people = record.get("people", [])
        if not isinstance(people, list) or any(not isinstance(p, str) or not p or "、" in p or p == "__none__" for p in people):
            raise ValueError("people must contain nonempty names without the delimiter 、")
    return config, records


def build(catalog, images, output):
    config, records = read_catalog(catalog)
    image_root, output = Path(images).resolve(), Path(output).resolve()
    if output == image_root or image_root in output.parents or output in image_root.parents:
        raise ValueError("image directory and output must be separate")
    if output == Path(catalog).resolve() or output in Path(catalog).resolve().parents:
        raise ValueError("output cannot contain the source catalog")
    if output.exists():
        raise ValueError("output already exists; use a fresh staging directory")
    groups = {k: [] for k in CATEGORIES}
    copies = []
    for record in records:
        if record.get("publish", True) is False:
            continue
        source = (image_root / record["file"]).resolve(strict=True)
        if not source.is_relative_to(image_root) or not source.is_file():
            raise ValueError("image escapes source directory or is not a file")
        groups[record["category"]].append({
            "rel": "photos/" + quote(record["file"], safe="/"), "fn": record["file"],
            "desc": record.get("description", ""),
            "people": "、".join(record.get("people", [])),
        })
        copies.append((source, output / "photos" / record["file"]))
    counts = tuple(len(groups[k]) for k in CATEGORIES)
    title = config.get("title", "家庭老照片档案")
    output.mkdir(parents=True)
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    cards = []
    for category, label in CATEGORIES.items():
        items = groups[category]
        covers = config.get("covers", {})
        cover = covers.get(category)
        if cover:
            items.sort(key=lambda x: x["fn"] != cover)
        image = f'<img loading="lazy" src="{html.escape(items[0]["rel"], quote=True)}" alt="{label}">' if items else ""
        cards.append(f'<a href="{category}.html">{image}<div class="t"><h2>{label} · {len(items)} 张</h2></div></a>')
        people = {p for item in items for p in item["people"].split("、") if p}
        # Empty categories still need an info node so the JS can render safely.
        body = '<div class="grid" id="grid"></div><div class="pager" id="pager"></div>'
        if not people:
            body = '<div class="info" id="info"></div>' + body
        text = page(f"{title} · {label}", body, category, items, people, counts, config)
        (output / f"{category}.html").write_text(text, encoding="utf-8")
    intro = html.escape(config.get("intro", ""))
    body = f'<div class="wrap portal"><div class="stats">{intro}</div><div class="sel">{"".join(cards)}</div></div>'
    (output / "index.html").write_text(page(title, body, counts=counts, config=config), encoding="utf-8")
    files = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob("*")) if p.is_file()}
    (output / "manifest.json").write_text(json.dumps({"counts": dict(zip(CATEGORIES, counts)), "files": files}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"counts": dict(zip(CATEGORIES, counts)), "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.catalog, args.images, args.output), ensure_ascii=False))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(1, f"Build failed: {exc}\n")
