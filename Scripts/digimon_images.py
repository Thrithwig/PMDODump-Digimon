#!/usr/bin/env python3
"""Fetch the explicitly mapped Wikimon originals and losslessly encode pixels as PNG.

Requires Pillow. No cropping, resizing, background removal, or generated artwork.
Run from the repository root: python Scripts/digimon_images.py
"""

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


def main():
    root = Path(__file__).resolve().parents[1] / "DataAsset" / "Digimon"
    mapping = json.loads((root / "image_sources.json").read_text(encoding="utf-8"))
    provenance_path = root / "image_provenance.json"
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {"images": []}
    records = {entry["species"]: entry for entry in provenance["images"]}
    for entry in mapping["images"]:
        path = root / entry["path"]
        previous = records.get(entry["species"])
        if previous and previous["source_url"] == entry["source_url"] and path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() == previous["png_sha256"]:
                continue
        request = Request(entry["source_url"], headers={"User-Agent": "PMDODump-Digimon development asset import"})
        with urlopen(request, timeout=30) as response:
            data = response.read()
        with Image.open(io.BytesIO(data)) as original:
            original.load()
            path.parent.mkdir(parents=True, exist_ok=True)
            original.save(path, format="PNG")
            records[entry["species"]] = {
                **entry, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "original_format": original.format, "width": original.width, "height": original.height,
                "source_sha256": hashlib.sha256(data).hexdigest(),
                "png_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "processing": "PNG encoding only; source pixels and background retained",
                "rights_status": mapping["rights_status"],
            }
        provenance["images"] = [records[key] for key in sorted(records)]
        provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        print(entry["species"], flush=True)


if __name__ == "__main__":
    main()
