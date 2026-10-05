"""Plan house-owned paved aprons with room for roads, services and patrols."""
import json,runpy,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'))
w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());plan=[]
roads=[h['hull'](s['vertices']) for s in w['terrain']['surfaces'] if s.get('centerline') and s.get('width',0)>=1.8]
services=[s['position'][:2] for o in w['objects'] for s in o.get('services',[])]
patrols=[pair for o in w['objects'] for a in o.get('walkers',[]) for pair in zip(a['route'],a['route'][1:]+a['route'][:1])]
solids=[(o['id'],h['hull'](p['vertices'])) for o in w['objects'] for p in o['parts'] if p['role']=='solid']
for o in w['objects']:
 core=next((p for p in o['parts'] if p['id'].endswith('-ground-core') or p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls')),None)
 if not core:continue
 outline=h['hull'](core['vertices']);faces=[]
 for edge,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
  length=math.dist(a,b);t=((b[0]-a[0])/length,(b[1]-a[1])/length);n=(t[1],-t[0]);segments=max(1,math.ceil(length/1.3))
  for j in range(segments):
   l,r=length*j/segments,length*(j+1)/segments
   for depth in (.86,.64,.44,.29):
    # Leave a narrow wall-side planted gap. A short chamfer at outer corners
    # makes an architectural lot boundary rather than another road rectangle.
    q=[(a[0]+t[0]*s+n[0]*d,a[1]+t[1]*s+n[1]*d) for s,d in [(l,.18),(r,.18),(r,depth),(l,depth)]]
    if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in q):continue
    if any(h['overlap'](q,p,.10) for p in roads):continue
    if any(owner!=o['id'] and h['overlap'](q,p,.12) for owner,p in solids):continue
    if any(h['segment_overlap'](q,a,b,.55) for a,b in patrols):continue
    if any(h['inside'](p,q) or min(h['distance'](p,a,b) for a,b in zip(q,q[1:]+q[:1]))<.85 for p in services):continue
    if any(h['overlap'](q,p['polygon'],.04) for p in plan if p['owner']!=o['id']):continue
    plan.append({'owner':o['id'],'edge':edge,'segment':j,'segments':segments,'polygon':q,'tangent':t,'normal':n,'depth':depth});break
  faces.append({'edge':edge,'length':length})
path=ROOT/'authoring/ro3-house-aprons-v69.json';path.write_text(json.dumps({'sourcePass':69,'protected':['roads >=1.8','patrol capsules .55','services .85','other solids .12'],'segments':plan},indent=2)+'\n')
print('Planned',len(plan),'private apron segments across',len(set(p['owner'] for p in plan)),'houses')
