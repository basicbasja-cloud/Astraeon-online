"""Draw the reviewed owned-frontage proposals from their explicit native plan."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v78/frontage-placement';p=json.loads((O/'plan.json').read_text());city=json.loads((O.parent/'native-plan.json').read_text())
W,H=1024,1152;scale=3.5;ox,oy=64,70
xy=lambda x,y:(ox+x*scale,oy+y*scale)
def points(a):return ' '.join('%.2f,%.2f'%xy(*v[:2]) for v in a)
out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1152">','<rect width="1024" height="1152" fill="#182c39"/>','<text x="36" y="32" fill="#edcf8a" font-family="sans-serif" font-size="20">WAYFARER · OWNED FRONTAGE PLACEMENT</text>','<text x="36" y="53" fill="#b7c8cb" font-family="sans-serif" font-size="13">Original layout · Lower roof layers selected by door, plot and route clearance</text>',f'<polygon points="{points(city["land"])}" fill="#85866b" stroke="#ede0b5" stroke-width="3"/>']
for r in city['roads']:out.append(f'<polyline points="{points(r["centerline"])}" fill="none" stroke="#e9dbad" stroke-width="{r["width"]*scale}" stroke-linecap="butt" stroke-linejoin="round"/>')
for l in city['lots']:
 out.append(f'<polygon points="{points(l["lot"])}" fill="#c7bc99" stroke="#7e826a" stroke-width=".8"/>')
for l in city['landmarks']:
 x,y=l['center'];w,d=l['width']/2,l['depth']/2
 out.append(f'<polygon points="{points([[x-w,y-d],[x+w,y-d],[x+w,y+d],[x-w,y+d]])}" fill="#375b6c" stroke="#e1c779" stroke-width="2"/>')
for a in p['frontages']:
 out.append(f'<polygon points="{points(a["roofFootprint"])}" fill="#ecd283" stroke="#163647" stroke-width="1.4"><title>{html.escape(a["id"]+" · "+a["style"]+" · "+a["use"])}</title></polygon>')
 x,y=xy(*a['position'][:2]);out.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#e6f1ec"/>')
for name,x,y in [('CIVIC PRECINCT',128,45),('WAYFARER SQUARE',128,144),('WEST NEIGHBORHOOD',79,200),('ARTISANS COURT',104,165),('WILLOW COURT',154,200)]:
 xx,yy=xy(x,y);out.append(f'<text x="{xx}" y="{yy}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#172f3c" stroke="#e9dbad" stroke-width="3" paint-order="stroke">{name}</text>')
out += ['<text x="36" y="1112" fill="#edcf8a" font-family="sans-serif" font-size="14">Gold:19 selected secondary roofs · White:actual door anchors · All158 housing plots retained</text>','<text x="36" y="1134" fill="#b7c8cb" font-family="sans-serif" font-size="12">No copied Prontera blueprint. Streets, closed patrol routes and2.2m entrances remain clear.</text>','</svg>']
(O/'owned-frontage-plan.svg').write_text('\n'.join(out)+'\n')
