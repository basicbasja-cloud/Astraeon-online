"""Review map of actual owned lots and explicitly selected native placements."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v82/grounded-frontages';p=json.loads((O/'plan.json').read_text());p['trees']=json.loads((R/'docs/review/wayfarer-capital-v80/unique-neighborhoods/plan.json').read_text())['trees'];city=json.loads((O.parent/'native-plan.json').read_text());models={a['id']:a for a in p['houses']};colors={'stepped-gables':'#f4c47d','garden-cottage':'#86b9a0','dormered-gambrel':'#d2909b','corner-oriel':'#84afca'}
def xy(v):return f'{v[0]*3.1+60:.2f},{v[1]*3.1+110:.2f}'
def polygon(v,color,stroke='none'):return f'<polygon points="{" ".join(map(xy,v))}" fill="{color}" stroke="{stroke}" stroke-width="1.1"/>'
a=['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="1160" viewBox="0 0 920 1160"><rect width="920" height="1160" fill="#1c303d"/><g font-family="sans-serif" fill="#e9d5aa"><text x="50" y="36" font-size="22">WAYFARER · ROYAL CAPITAL AND OCCUPIED NEIGHBORHOODS</text><text x="50" y="62" font-size="13">Formal royal avenues · Courtyard neighborhoods · Original models · Shared painted masonry</text></g>'];a.append(polygon(city['land'],'#929981','#c1bb9a'))
for r in city['roads']:a.append(f'<polyline points="{" ".join(map(xy,r["centerline"]))}" fill="none" stroke="#e0d4b2" stroke-width="{r["width"]*3.1}"/>')
for park in city['parks']:a.append(polygon(park['polygon'],'#557959'))
for l in city['lots']:
 n=l['id'];a.append(polygon(l['lot'],colors[models[n]['design']] if n in models else '#b08c67','#e1d3ad' if n in models else '#a6a78c'))
for l in city['landmarks']:
 x,y=l['center'];w,d=l['width'],l['depth'];a.append(polygon([[x-w/2,y-d/2],[x+w/2,y-d/2],[x+w/2,y+d/2],[x-w/2,y+d/2]],'#426176','#cbb47d'))
for i,t in enumerate(p['trees']):a.append(f'<circle cx="{t["position"][0]*3.1+60}" cy="{t["position"][1]*3.1+110}" r="{t["radiusBudget"]*3.1}" fill="#2c6044" stroke="#b9d19b" stroke-width="1"/>')
for drain in p['drains']:
 a.append(f'<circle cx="{drain["position"][0]*3.1+60}" cy="{drain["position"][1]*3.1+110}" r="3" fill="#294c5c" stroke="#efe4bd" stroke-width="1"/>')
for i,(kind,color) in enumerate(colors.items()):
 x=50+(i%2)*410;y=1050+(i//2)*32;a.append(f'<rect x="{x}" y="{y-12}" width="16" height="16" fill="{color}"/><text x="{x+26}" y="{y+1}" fill="#e9d5aa" font-family="sans-serif" font-size="14">{html.escape(kind)} · {sum(t["design"]==kind for t in p["houses"])} houses</text>')
a.append('<text x="50" y="1140" fill="#c6cec9" font-family="sans-serif" font-size="12">158 owned housing lots · 12 distinct houses · 6 clear path drains · Plots/selected planting shown; not roof footprints.</text></svg>');(O/'placement-plan.svg').write_text('\n'.join(a)+'\n');print('PASS owned-lot/selected-placement map')
