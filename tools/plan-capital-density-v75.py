"""Fill neighborhood frontage gaps from explicit native pre-density geometry."""
import argparse,json,math,copy
from pathlib import Path
from shapely.geometry import Polygon,LineString,box,MultiPoint,Point
from shapely.ops import unary_union
from shapely.affinity import translate,rotate
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True,help='Explicit native export before density changes');ap.add_argument('--plan',type=Path,default=O/'before-density/plan.json');args=ap.parse_args();p=json.loads(args.plan.read_text());assert not p.get('densityRefinement'),'Plan from the pre-density layout';s=json.loads(args.source.read_text());owners={o['id']:o for o in s['objects']};lots=p['lots'];land=Polygon(p['land']).buffer(-2)

for r in p['roads']:
 if r['id'] in ('west-district-spine','east-district-spine','commons-cross'):r['width']=4.5
 elif r['id'].startswith('district-cross-'):r['width']=5
 elif r['id'].startswith('inner-'):r['width']=4
 elif r['id']=='capital-circuit':r['width']=6
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2+.4,cap_style=2,join_style=2) for r in p['roads']]);reserved=unary_union([box(102,126,154,162),box(97,32,159,76),box(174,145,203,165),box(179,86,205,110)]+[Polygon(a['polygon']).buffer(.4) for a in p['parks']])
def footprint(o):return MultiPoint([v[:2] for a in o['parts'] if a.get('visible',True) and a['role'] not in ('ground',) for v in a['vertices']]).convex_hull
occupied={l['id']:footprint(owners[l['id']]) for l in lots}
obstacles=[]
for o in s['objects']:
 if o['id'] in occupied or o['id'] in ('capital-river-bank','capital-waterline','capital-curtain-walls','capital-owned-block-boundaries'):continue
 for a in o['parts']:
  if a['role']=='solid':obstacles.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.35))
fixed=unary_union(obstacles)
donors=[l for l in lots if not l['existing'] and (l['center'][0]<45 or l['center'][0]>211)]
# Retain perimeter homes at alternating positions; transfer only new modules.
donors=donors[::2][:32]
for l in donors:occupied.pop(l['id'])
moves=[]
# Bring existing new frontages to the street edge where physical roofs permit.
for l in lots:
 if l['existing'] or l in donors:continue
 road=next(r for r in p['roads'] if r['id']==l['road']);a=l['angle'];forward=(-math.sin(a),math.cos(a));poly=occupied[l['id']];delta=(forward[0]*1.5,forward[1]*1.5);q=translate(poly,*delta)
 if land.covers(q) and q.intersection(roads).area<.001 and q.intersection(fixed).area<.001 and not any(q.distance(v)<.65 for k,v in occupied.items() if k!=l['id']):
  old=l['center'][:];l['center']=[round(old[i]+delta[i],3) for i in range(2)];l['lot']=[list(v) for v in translate(Polygon(l['lot']),*delta).exterior.coords[:-1]];occupied[l['id']]=q;moves.append({'id':l['id'],'before':old,'after':l['center'],'rotation':0})
def candidates(poly,angle):
 local=rotate(poly,-angle*180/math.pi,origin=(0,0));minx,miny,maxx,maxy=local.bounds
 found=[]
 for r in p['roads']:
  if r['id'].startswith(('north-','civic-')) or r['id']=='south-parterre-road':continue
  for a,b in zip(r['centerline'],r['centerline'][1:]):
   horizontal=a[1]==b[1];lo=min(a[0],b[0]) if horizontal else min(a[1],b[1]);hi=max(a[0],b[0]) if horizontal else max(a[1],b[1])
   for side in (-1,1):
    ang=(math.pi if side>0 else 0) if horizontal else (math.pi/2 if side>0 else -math.pi/2);orient=rotate(local,ang*180/math.pi,origin=(0,0));offset=r['width']/2+maxy+1.0
    for t in range(math.ceil(lo+5),math.floor(hi-4)):
     x,y=(t,a[1]+side*offset) if horizontal else (a[0]+side*offset,t)
     if not (50<x<206 and 82<y<239):continue
     q=translate(orient,x,y)
     if not land.covers(q) or q.intersection(roads).area>.001 or q.intersection(reserved).area>.001 or q.intersection(fixed).area>.001:continue
     dist=min(q.distance(v) for v in occupied.values())
     if dist<.8:continue
     # Fill local facade gaps first, instead of isolated buildings in empty land.
     found.append((dist,y,x,q,ang,r['id']))
 return sorted(found,key=lambda v:(v[0],v[1],v[2]))
unplaced=[]
for l in donors:
 old=l['center'][:];oldangle=l['angle'];poly=translate(footprint(owners[l['id']]),-old[0],-old[1]);choices=candidates(poly,oldangle)
 if not choices:occupied[l['id']]=footprint(owners[l['id']]);unplaced.append(l['id']);continue
 dist,y,x,q,ang,road=choices[0];l.update(center=[round(x,3),round(y,3)],angle=ang,road=road,district='South Commons' if x<128 and y>180 else 'Willow Borough' if y>180 else 'Artisan Ward' if x<128 and y>144 else 'Lantern Market' if x>128 else 'Seafarer Ward',denseTownhouse=True)
 l['lot']=list(q.buffer(.22,join_style=2).exterior.coords)[:-1];occupied[l['id']]=q;moves.append({'id':l['id'],'before':old,'after':l['center'],'rotation':ang-oldangle})
# New narrow-fronted modules complete the rows without changing city bounds.
added=[]
for i in range(28):
 poly=box(-2.85,-3.9,2.85,4.25);choices=candidates(poly,0)
 if not choices:break
 dist,y,x,q,ang,road=choices[0];l={'id':f'capital-infill-{i:03}','existing':False,'family':'market' if x>152 and y<180 else 'workshop' if x<104 and 144<y<210 else 'residential','district':'South Commons' if x<128 and y>180 else 'Willow Borough' if y>180 else 'Artisan Ward' if x<128 and y>144 else 'Lantern Market' if x>128 else 'Seafarer Ward','center':[round(x,3),round(y,3)],'angle':ang,'lot':list(q.buffer(.22,join_style=2).exterior.coords)[:-1],'road':road,'width':4.2,'depth':6.4,'floors':2,'roof':'gable','clay':['roofClayWarm','roofClayOchre','roofClayRose'][i%3],'balcony':False,'wing':False,'garden':i%3==0,'denseTownhouse':True,'densityInfill':True}
 lots.append(l);added.append(l['id']);occupied[l['id']]=q
p.update(newHouses=sum(not l['existing'] for l in lots),densityStrategy='Close-set street frontages with small side passages; wider ceremonial precinct retained',densityRefinement={'moves':moves,'added':added,'unplacedDonors':unplaced,'minimumVisibleFacadeGap':.8,'streetFrontageSetback':1.0,'districtStreetsNarrowed':True})
(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print('DENSITY PLAN',len(lots),'houses',len(moves),'new module relocations',len(added),'infill',len(unplaced),'donors unchanged')
