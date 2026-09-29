"""Transparent contact sheets, GIFs, and a local playback page for action review."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from .core import load_config


def make_previews(repo_root: Path, output_root: Path,
                  config_path: Path | None = None,
                  actions_path: Path | None = None) -> list[str]:
    species = load_config(config_path or repo_root / "config/phase4/agumon.json")
    config = json.loads((actions_path or repo_root / "config/phase4/agumon-actions.json").read_text())
    if config.get("species") != species["species"]:
        raise ValueError("Actions manifest species does not match render config")
    frame_size = species["frame_size"]
    package = output_root / "package" / str(species["pmdo_index"])
    destination = output_root / "previews"
    destination.mkdir(parents=True, exist_ok=True)
    available = []
    for spec in config["actions"]:
        name = spec["name"]
        path = package / f"{name}-Anim.png"
        if not path.exists():
            continue
        with Image.open(path) as source:
            atlas = source.convert("RGBA")
        count = len(spec["durations"])
        if atlas.size != (count*frame_size,8*frame_size):
            continue
        atlas.resize((atlas.width*4, atlas.height*4), Image.Resampling.NEAREST).save(destination / f"{name}-contact.png")
        with Image.open(package / f"{name}-Offsets.png") as offsets_file, Image.open(package / f"{name}-Shadow.png") as shadow_file:
            overlay = Image.alpha_composite(atlas, offsets_file.convert("RGBA"))
            overlay = Image.alpha_composite(overlay, shadow_file.convert("RGBA"))
            overlay.resize((overlay.width*4, overlay.height*4), Image.Resampling.NEAREST).save(
                destination / f"{name}-markers.png")
        colors = sorted({rgb[:3] for rgb in atlas.getdata() if rgb[3]})
        palette = [0,0,0] + [v for rgb in colors for v in rgb]
        palette.extend([0] * (768-len(palette)))
        lookup = {rgb:i+1 for i,rgb in enumerate(colors)}
        frames = []
        for col in range(count):
            rgba = Image.new("RGBA", (8*frame_size,frame_size))
            for row in range(8):
                rgba.paste(atlas.crop((col*frame_size,row*frame_size,(col+1)*frame_size,(row+1)*frame_size)), (row*frame_size,0))
            indexed = Image.new("P", rgba.size, 0)
            indexed.putpalette(palette)
            indexed.putdata([lookup[p[:3]] if p[3] else 0 for p in rgba.getdata()])
            frames.append(indexed)
        frames[0].save(destination / f"{name}.gif", save_all=True, append_images=frames[1:],
                       duration=[round(v*1000/60) for v in spec["durations"]],
                       disposal=2, transparency=0, loop=0, optimize=False)
        available.append(name)
    buttons = "\n".join(f'<button data-action="{name}">{name}</button>' for name in available)
    data = json.dumps({s["name"]:s["durations"] for s in config["actions"] if s["name"] in available})
    html = """<!doctype html><meta charset="utf-8"><title>SPECIES action previews</title>
<style>body{font:16px sans-serif;background:#ddd}button{margin:4px}canvas{image-rendering:pixelated;
background:linear-gradient(45deg,#ccc 25%,transparent 25%) 0 0/16px 16px,
linear-gradient(45deg,transparent 75%,#ccc 75%) 0 0/16px 16px,#fff}
</style><h1>SPECIES action candidate</h1><p>All eight directions, from Down through DownLeft.</p>
<div id="buttons">BUTTONS</div><h2 id="name"></h2><canvas width="CANVAS_WIDTH" height="FRAME_SIZE" style="width:DISPLAY_WIDTHpx;height:DISPLAY_HEIGHTpx"></canvas>
<script>const timings=DATA;const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
let action='',img,started=performance.now();function select(name){action=name;img=new Image();
img.src='../package/PMDO_ID/'+name+'-Anim.png';started=performance.now();document.querySelector('#name').textContent=name}
document.querySelectorAll('button').forEach(b=>b.onclick=()=>select(b.dataset.action));
function draw(now){if(img?.complete&&img.naturalWidth){let durations=timings[action],cycle=durations.reduce((a,b)=>a+b,0);
let t=((now-started)/1000*60)%cycle,index=0;while(t>=durations[index]){t-=durations[index++];}
ctx.clearRect(0,0,CANVAS_WIDTH,FRAME_SIZE);for(let row=0;row<8;row++)ctx.drawImage(img,index*FRAME_SIZE,row*FRAME_SIZE,FRAME_SIZE,FRAME_SIZE,row*FRAME_SIZE,0,FRAME_SIZE,FRAME_SIZE)}
requestAnimationFrame(draw)}requestAnimationFrame(draw);select(FIRST)</script>"""
    html = (html.replace("BUTTONS", buttons).replace("DATA", data)
            .replace("FIRST", json.dumps(available[0] if available else ""))
            .replace("SPECIES", species["display_name"])
            .replace("PMDO_ID", str(species["pmdo_index"]))
            .replace("CANVAS_WIDTH", str(8*frame_size))
            .replace("DISPLAY_WIDTH", str(8*frame_size*4))
            .replace("DISPLAY_HEIGHT", str(frame_size*4))
            .replace("FRAME_SIZE", str(frame_size)))
    (destination / "index.html").write_text(html, encoding="utf-8")
    return available
