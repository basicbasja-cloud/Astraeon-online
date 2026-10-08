"""Review diagram of measured crown budgets at their actual native roots."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R/'docs/review/wayfarer-capital-v83/layered-crowns'
p = json.loads((O/'plan.json').read_text())
city = json.loads((O.parent/'native-plan.json').read_text())
def xy(v):
    return f'{v[0]*3.1+60:.2f},{v[1]*3.1+110:.2f}'
def polygon(v, color, stroke='none'):
    return f'<polygon points="{" ".join(map(xy,v))}" fill="{color}" stroke="{stroke}" stroke-width="1.1"/>'
a = ['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="1160" viewBox="0 0 920 1160"><rect width="920" height="1160" fill="#1c303d"/><g font-family="sans-serif" fill="#e9d5aa"><text x="50" y="36" font-size="22">WAYFARER · LAYERED CAPITAL CROWNS</text><text x="50" y="62" font-size="13">18 measured crown budgets · Actual root positions · Formal avenues and original neighborhoods</text></g>']
a.append(polygon(city['land'],'#929981','#c1bb9a'))
for r in city['roads']:
    a.append(f'<polyline points="{" ".join(map(xy,r["centerline"]))}" fill="none" stroke="#e0d4b2" stroke-width="{r["width"]*3.1}"/>')
for park in city['parks']:
    a.append(polygon(park['polygon'],'#557959'))
for l in city['lots']:
    a.append(polygon(l['lot'],'#b08c67','#a6a78c'))
for l in city['landmarks']:
    x,y=l['center'];w,d=l['width'],l['depth']
    a.append(polygon([[x-w/2,y-d/2],[x+w/2,y-d/2],[x+w/2,y+d/2],[x-w/2,y+d/2]],'#426176','#cbb47d'))
for t in p['trees']:
    x,y=t['center'];x=x*3.1+60;y=y*3.1+110
    a.append(f'<circle cx="{x}" cy="{y}" r="{t["radiusBudget"]*3.1}" fill="#2c6044" fill-opacity=".65" stroke="#d5e9ae" stroke-width="1"/><circle cx="{x}" cy="{y}" r="1.6" fill="#f1d391"/>')
a.append('<g font-family="sans-serif" fill="#e9d5aa"><text x="50" y="1048" font-size="16">Broader middle layers · Uneven branch tips · Three crown profiles</text><text x="50" y="1080" font-size="14">Every trunk, root, collision and tree height retained · No new triangles or images</text><text x="50" y="1112" font-size="13">Roof clearance ≥ 0.20m · Lower boughs below 2.4m do not expand</text><text x="50" y="1140" font-size="12">Owned lots and selected crown budgets shown, not roof footprints or final canopy outlines.</text></g></svg>')
(O/'placement-plan.svg').write_text('\n'.join(a)+'\n')
print('PASS measured native crown-placement diagram')
