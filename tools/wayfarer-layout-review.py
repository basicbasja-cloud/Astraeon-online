"""Compare supplied concept relationships with the actual exported authored layout.
The concept panel is a labelled schematic, not a substitute for the user's image.
"""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
roles=[('caravan-gate','West Gate',(7,27)),('astral-fountain','Central Plaza',(22,20)),('guild-hall','Consortium Hall',(22,10)),('east-inn',"Seafarer’s Rest",(11,15)),('artisan-workshop','Bronze Anvil',(11,26)),('moon-shrine','Luna Shrine',(33,11)),('market-shop','Market District',(33,21)),('residence','Southern residences',(22,32)),('northwest-cottage','Northern residences',(10,8))]
def polygon(points,fill,stroke='none'):
 return '<polygon points="'+ ' '.join(f'{x*13:.2f},{y*13:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
def position(o):
 body=next((p for p in o['parts'] if p['id']==o['id']+'-walls'),None)
 if body:return [round(sum(v[i] for v in body['vertices'])/len(body['vertices']),3) for i in range(3)]
 return o['presentation']['position']
def label(x,y,name):return f'<text x="{x*13}" y="{y*13}" text-anchor="middle" class="label">{html.escape(name)}</text>'
def panel(actual):
 out=['<svg viewBox="0 0 572 540" role="img">'];out.append('<rect width="572" height="540" fill="#38747c"/>')
 if actual:
  out.append(polygon(w['terrain']['walkablePolygon'],'#637c51','#c8bd96'))
  for s in w['terrain']['surfaces']:
   if s.get('visible') is False or s['role']=='water':continue
   out.append(polygon(s['polygon'],'#c4b58f' if s.get('material')=='paving' else '#718054' if s.get('material')=='grass' else '#a0875c'))
  for o in w['objects']:
   for p in o['parts']:
    if p['role']!='solid' or len(p['vertices'])<4:continue
    pts=[v[:2] for v in p['vertices'][:4]];out.append(polygon(pts,{'civic':'#467799','shrine':'#739baf','market':'#cc9567','residential':'#c1a27d','inn':'#ac6544','workshop':'#7d5940','fortification':'#d0c5a5'}.get(o['family'],'#596d49'),'#3d4940'))
  for id,name,unused in roles:
   o=next(o for o in w['objects'] if o['id']==id);x,y=position(o)[:2];out.append(label(x,y+1.5,name))
  route=[s['position'] for s in w['route'] if s['name'] in ['Arrival','Avenue','Plaza','Hall']]
 else:
  out.append(polygon([(4,7),(38,7),(40,34),(26,37),(7,35)],'#637c51','#c8bd96'))
  out.append(polygon([(19,9),(25,9),(25,22),(9,27),(7,25),(19,19)],'#c4b58f'))
  out.append('<ellipse cx="286" cy="260" rx="73" ry="60" fill="#c4b58f"/>')
  for id,name,(x,y) in roles:
   out.append(polygon([(x-2,y-1.5),(x+2,y-1.5),(x+2,y+1.5),(x-2,y+1.5)],'#467799' if id in ['guild-hall','moon-shrine','caravan-gate'] else '#ba805a','#efe2bb'));out.append(label(x,y+2.4,name))
  route=[(7,27),(15,23),(22,20),(22,14)]
 out.append('<polyline points="'+' '.join(f'{x*13},{y*13}' for x,y in route)+'" fill="none" stroke="#f8d06b" stroke-width="4" stroke-dasharray="8 5"/>');out.append('</svg>');return ''.join(out)
text='''<!doctype html><meta charset="utf-8"><title>Wayfarer concept-to-playable layout</title><style>body{margin:0;padding:26px;background:#14232b;color:#efe2c4;font:16px system-ui}h1,h2{font-family:Georgia}.panels{display:grid;grid-template-columns:1fr 1fr;gap:24px}section{background:#22363b;padding:18px}svg{width:100%;max-height:580px}.label{font:10px system-ui;paint-order:stroke;stroke:#17262b;stroke-width:3px;fill:#fff0cb;stroke-linejoin:round}p{line-height:1.5;color:#c5d0be}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #667565;text-align:left;padding:9px}</style><h1>Wayfarer — concept relationships and authored playable layout</h1><p>The supplied concept remains the art authority. Left: schematic transcription of its district relationships. Right: actual exported Blender terrain, surfaces and solid footprints. Yellow: arrival → avenue → plaza → Hall. Geometry is adapted to the fixed gameplay camera.</p><div class="panels"><section><h2>Concept relationship schematic</h2>'''+panel(False)+'''</section><section><h2>Actual authored town plan</h2>'''+panel(True)+'''</section></div><h2>District mapping</h2><table><tr><th>Concept role</th><th>Authored object</th><th>Source position</th></tr>'''
for id,name,_ in roles:
 o=next(o for o in w['objects'] if o['id']==id);text+=f'<tr><td>{html.escape(name)}</td><td>{id}</td><td>{position(o)}</td></tr>'
text+='</table><p>This comparison verifies layout derivation. Golden acceptance also requires the gameplay camera, building families, character motion and physical-device performance; this diagram does not approve them.</p>'
(ROOT/'tools/wayfarer-layout-review.html').write_text(text)
print('Generated actual source layout comparison')
