#!/usr/bin/env python3
"""Render the README / dataset-card banner: the Accelerate Bench title surrounded by the 32 task illustrations.

Usage: python3 scripts/make_banner.py
Writes dist/assets/accelerate-bench-banner.png (2400 px wide). Needs Google Chrome for the headless screenshot.
"""
import json
import random
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'dist' / 'assets'
OUT = ASSETS / 'accelerate-bench-banner.png'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H, CW, CH = 1800, 840, 200, 100
COLORS = ['#2f66b0', '#307f83', '#6b5fb5', '#3f8f5a', '#b0703a', '#8a4fa0', '#c0565b', '#5d7088']


def illustration(path):
    svg = path.read_text()
    svg = re.sub(r'<title>.*?</title>|<desc>.*?</desc>', '', svg, flags=re.S)
    svg = svg.replace('viewBox="0 0 720 400"', 'viewBox="0 80 720 180" preserveAspectRatio="xMidYMid meet"', 1)
    assert 'viewBox="0 80 720 180"' in svg, path
    return svg


def positions():
    rows = [(18, 8, 22), (132, 7, 133)]
    slots = [(x0 + i * 222, y) for y, n, x0 in rows for i in range(n)]
    slots += [(24, 370), (1576, 370)]
    slots += [(x0 + i * 222, y) for y, n, x0 in [(608, 7, 133), (722, 8, 22)] for i in range(n)]
    return slots


def page(tasks):
    rng = random.Random(11)
    fonts = ASSETS / 'fonts'
    cards = []
    for (x, y), t in zip(positions(), tasks):
        x, y, r = x + rng.uniform(-5, 5), y + rng.uniform(-4, 4), rng.uniform(-2.4, 2.4)
        cards.append(f'<div class="card" style="left:{x:.1f}px;top:{y:.1f}px;transform:rotate({r:.2f}deg);--c:{COLORS[t["area_id"]]}">'
                     f'<div class="art">{illustration(ROOT / "dist" / t["diagram"])}</div>'
                     f'<div class="cap"><i></i>{t["name"]}</div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Manrope;font-weight:600;src:url('{(fonts / 'manrope-600.ttf').as_uri()}')}}
@font-face{{font-family:Manrope;font-weight:800;src:url('{(fonts / 'manrope-800.ttf').as_uri()}')}}
@font-face{{font-family:Plex;src:url('{(fonts / 'ibm-plex-mono-400.ttf').as_uri()}')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{position:relative;background:radial-gradient(ellipse 62% 58% at 50% 50%,#ffffff 0%,#f6f8fb 55%,#e8eef5 100%);font-family:Manrope,sans-serif}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(#cfd9e6 1.1px,transparent 1.3px);background-size:24px 24px;opacity:.55}}
.card{{position:absolute;width:{CW}px;height:{CH}px;background:#fff;border:1px solid #d9e2ec;border-radius:9px;overflow:hidden;
  box-shadow:0 8px 18px rgba(23,43,69,.10),0 1px 3px rgba(23,43,69,.08)}}
.card::before{{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:var(--c)}}
.art{{position:absolute;left:7px;right:7px;top:11px;height:52px}}
.art svg{{width:100%;height:100%;display:block}}
.art svg text{{display:none}}
.art svg *{{vector-effect:non-scaling-stroke}}
.art svg [stroke]{{stroke-width:1.3px}}
.cap{{position:absolute;left:10px;right:8px;bottom:8px;display:flex;align-items:center;gap:6px;font-weight:600;font-size:12.5px;color:#22364f;white-space:nowrap}}
.cap i{{width:7px;height:7px;border-radius:50%;background:var(--c);flex:none}}
.title{{position:absolute;left:0;right:0;top:318px;text-align:center}}
.brand{{display:inline-flex;align-items:center;gap:30px}}
.mark{{width:106px;height:106px;border-radius:25px;background:#172b45;display:grid;place-items:center;box-shadow:0 10px 24px rgba(23,43,69,.22)}}
.mark svg{{width:74px;height:74px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}}
h1{{margin:0;font-size:116px;font-weight:800;letter-spacing:-4px;color:#172b45;line-height:1}}
h1 span{{font-weight:600;color:#2c4a73}}
.tag{{margin:22px 0 0;font-size:30px;font-weight:600;color:#53677f;letter-spacing:-.3px}}
.meta{{margin:14px 0 0;font:16px/1 Plex,monospace;letter-spacing:2.4px;text-transform:uppercase;color:#7c8fa6}}
</style></head><body><div class="dots"></div>{''.join(cards)}
<div class="title"><div class="brand"><span class="mark"><svg viewBox="0 0 24 24"><path d="M5 18 18 5M7 5h11v11"/></svg></span>
<h1>Accelerate <span>Bench</span></h1></div>
<p class="tag">Can coding agents make whole scientific applications faster?</p>
<p class="meta">32 tasks · 8 application areas · Harbor task packages · v1.1</p></div>
</body></html>"""


def main():
    tasks = json.loads((ASSETS / 'results.json').read_text())['tasks']
    assert len(tasks) == 32 and len(positions()) == 32
    with tempfile.TemporaryDirectory() as tmp:
        html, shot = Path(tmp) / 'banner.html', Path(tmp) / 'banner.png'
        html.write_text(page(tasks))
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
                        f'--window-size={W},{H}', f'--screenshot={shot}', html.as_uri()], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sips', '--resampleWidth', '2400', str(shot), '--out', str(OUT)], check=True, stdout=subprocess.DEVNULL)
    print('wrote', OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
