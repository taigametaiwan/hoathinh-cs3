#!/usr/bin/env python3
"""Refresh CloudStream plugin metadata from CS3 files in the repository root."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins.json"
CONFIG = ROOT / "catalog-config.json"
REPOSITORY = "taigametaiwan/hoathinh-cs3"
BRANCH = "main"


def package_info(path):
    try:
        with zipfile.ZipFile(path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            if "classes.dex" not in archive.namelist():
                raise ValueError("missing classes.dex")
    except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.name}: invalid CS3 package: {exc}") from exc
    if not isinstance(manifest.get("name"), str) or not manifest["name"].strip():
        raise ValueError(f"{path.name}: missing name")
    if type(manifest.get("version")) is not int or manifest["version"] < 0:
        raise ValueError(f"{path.name}: invalid version")
    if not isinstance(manifest.get("pluginClassName"), str) or not manifest["pluginClassName"].strip():
        raise ValueError(f"{path.name}: missing pluginClassName")
    return manifest


def refresh(entry, path, manifest):
    entry = entry.copy()
    entry["url"] = f"https://raw.githubusercontent.com/{REPOSITORY}/{BRANCH}/{quote(path.name)}"
    entry["repositoryUrl"] = f"https://github.com/{REPOSITORY}"
    entry["version"] = manifest["version"]
    entry["fileSize"] = path.stat().st_size
    entry["fileHash"] = "sha256-" + hashlib.sha256(path.read_bytes()).hexdigest()
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if plugins.json needs updating")
    args = parser.parse_args()
    existing = json.loads(PLUGINS.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    excluded = set(config["exclude"])
    files = {p.stem.casefold(): p for p in ROOT.glob("*.cs3")}
    result = []
    used = set()
    for entry in existing:
        key = entry["internalName"].casefold()
        if key in used:
            raise ValueError(f"Duplicate internalName: {entry['internalName']}")
        if key not in files:
            raise ValueError(f"Listed addon is missing: {entry['internalName']}.cs3")
        if files[key].name in excluded:
            raise ValueError(f"Listed addon is excluded: {files[key].name}")
        used.add(key)
        result.append(refresh(entry, files[key], package_info(files[key])))
    for key, path in sorted(files.items()):
        if key in used or path.name in excluded:
            continue
        manifest = package_info(path)
        entry = {
            "url": "",
            "status": 1,
            "version": 0,
            "apiVersion": 1,
            "name": manifest["name"],
            "internalName": path.stem,
            "authors": ["Community"],
            "description": f"Cloudstream extension: {manifest['name']}.",
            "repositoryUrl": "",
            "tvTypes": ["Anime"],
            "language": "vi",
            "iconUrl": manifest.get("iconUrl") or None,
            "fileSize": 0,
            "fileHash": "",
        }
        result.append(refresh(entry, path, manifest))
    updated = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    current = PLUGINS.read_text(encoding="utf-8")
    if args.check:
        if current != updated:
            print("plugins.json needs updating", file=sys.stderr)
            return 1
    else:
        PLUGINS.write_text(updated, encoding="utf-8")
    print(f"Validated {len(result)} listed plugins and {len(excluded)} excluded CS3 file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
