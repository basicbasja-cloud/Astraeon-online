"""Reorganize complete native house assemblies around RO3-scale city streets.

RO1 Prontera supplies placement principles, not coordinates. Four redundant
through lanes are removed so broad public streets can bound substantial blocks
with close frontages and shared back courts. All current house models are kept.
"""
import argparse,hashlib,json,math
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString,box
from shapely.ops import unary_union
from shapely.affinity import translate,rotate
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
p=json.loads(args.plan.read_text());assert not p.get('ro3StreetScaleRefinement')
raw=args.source.read_bytes();s=json.loads(raw);owners={o['id']:o for o in s['objects']};digest=hashlib.sha256(raw).hexdigest();del raw
removed={'inner-west-street','inner-east-street','west-wall-lane','east-wall-lane','south-parterre-road'}
oldwidths={r['id']:r['width'] for r in p['roads']}
p['roads']=[r for r in p['roads'] if r['id'] not in removed]
for r in p['roads']:
 if r['id'] in ('west-district-spine','east-district-spine'):r['width']=9
 elif r['id']=='capital-circuit':r['width']=10
 elif r['width']<8:r['width']=8
def outline(o):return MultiPoint([v[:2] for a in o['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull
lots=p['lots'];fixed=[l for l in lots if l.get('fixed')];remaining=[l for l in lots if not l.get('fixed')]
local={l['id']:rotate(translate(outline(owners[l['id']]),-l['center'][0],-l['center'][1]),-l['angle']*180/math.pi,origin=(0,0)) for l in remaining}
land=Polygon(p['land']).buffer(-2);roads={r['id']:r for r in p['roads']}
streetzone=unary_union([LineString(r['centerline']).buffer(r['width']/2+.35,cap_style=2,join_style=2) for r in p['roads']])
reserved=unary_union([box(102,126,154,162),box(97,32,159,76),box(174,145,203,165),box(179,86,205,110)]+[Polygon(a['polygon']).buffer(.25) for a in p['parks']])
occupied={l['id']:outline(owners[l['id']]) for l in fixed};obstacles=[]
for o in s['objects']:
 if o['id'] in {l['id'] for l in lots} or o['id'] in ('capital-river-bank','capital-waterline','capital-curtain-walls','capital-owned-block-boundaries'):continue
 for a in o['parts']:
  if a['role']=='solid':obstacles.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.3))
obstacles=unary_union(obstacles);moves=[];placed=[];runs=[]
def acceptable(q):
 return land.covers(q) and q.intersection(streetzone).area<.001 and q.intersection(reserved).area<.001 and q.intersection(obstacles).area<.001 and all(q.distance(v)>=.75 for v in occupied.values())
def assign(l,x,y,angle,road,q):
 moves.append({'id':l['id'],'before':l['center'][:],'after':[round(x,4),round(y,4)],'rotation':angle-l['angle']})
 district='Artisan Ward' if x<104 and 144<y<212 else 'Seafarer Ward' if x<104 and y<144 else 'South Commons' if x<128 else 'Lantern Market' if y<184 else 'Willow Borough'
 l.update(center=[round(x,4),round(y,4)],angle=angle,road=road,district=district,lot=list(q.buffer(.18,join_style=2).exterior.coords)[:-1],continuousFrontage=True)
 placed.append(l);remaining.remove(l);occupied[l['id']]=q
for roadname in ['west-district-spine','east-district-spine','capital-circuit','royal-boulevard-south','royal-boulevard-north']:
 r=roads[roadname]
 for a,b in zip(r['centerline'],r['centerline'][1:]):
  if a[0]!=b[0]:continue
  lo,hi=sorted([a[1],b[1]])
  for ya,yb in [(84.5,107.5),(116.5,137),(151,179.5),(188.5,211.5),(220.5,235)]:
   ya,yb=max(ya,lo+1),min(yb,hi-1)
   if yb-ya<6:continue
   for side in (-1,1):runs.append((roadname,a[0],side,ya,yb,r['width']))
for roadname,axis,side,start,end,width in runs:
 cursor=start;angle=math.pi/2 if side>0 else -math.pi/2;count=0;last=None
 while cursor<end and remaining:
  success=False
  def order(l):
   b=local[l['id']].bounds
   same=last is not None and l.get('roof')==last.get('roof') and abs(l.get('width',0)-last.get('width',0))<.1
   return (same,b[3]-b[1],b[2]-b[0],not l['existing'],l['id'])
  for l in sorted(remaining,key=order):
   shape=rotate(local[l['id']],angle*180/math.pi,origin=(0,0));x=axis+side*(width/2+local[l['id']].bounds[3]+.40);y=cursor-shape.bounds[1];q=translate(shape,x,y)
   if q.bounds[3]>end or not acceptable(q):continue
   assign(l,x,y,angle,roadname,q);cursor=q.bounds[3]+.8;count+=1;success=True;last=l;break
  if not success:cursor+=.5
 if count:print('BROAD STREET ROW',roadname,side,start,end,count,flush=True)
# Cross-street and upper-quarter plots complete the blocks. They remain close
# to another house and face real streets, rather than filling arbitrary ground.
for l in sorted(remaining[:],key=lambda l:(not l['existing'],-local[l['id']].area)):
 chosen=None
 for r in p['roads']:
  for a,b in zip(r['centerline'],r['centerline'][1:]):
   horizontal=a[1]==b[1];lo=min(a[0],b[0]) if horizontal else min(a[1],b[1]);hi=max(a[0],b[0]) if horizontal else max(a[1],b[1])
   for side in (-1,1):
    angle=(math.pi if side>0 else 0) if horizontal else (math.pi/2 if side>0 else -math.pi/2);shape=rotate(local[l['id']],angle*180/math.pi,origin=(0,0));offset=r['width']/2+local[l['id']].bounds[3]+.40
    for t in range(math.ceil(lo+5),math.floor(hi-4)):
     x,y=(t,a[1]+side*offset) if horizontal else (a[0]+side*offset,t)
     if not (22<x<234 and 35<y<262):continue
     q=translate(shape,x,y)
     if not acceptable(q):continue
     nearest=min(q.distance(v) for v in occupied.values());score=(0 if 50<x<206 and 82<y<239 else 30)+nearest
     if chosen is None or score<chosen[0]:chosen=(score,x,y,angle,r['id'],q)
 if chosen:
  _,x,y,angle,road,q=chosen;assign(l,x,y,angle,road,q)
 else:print('UNPLACED',l['id'],flush=True)
assert not remaining,('Not enough reviewed street frontage',[l['id'] for l in remaining])
p['lots']=fixed+placed;p['densityStrategy']='RO3-scale public streets bounding dense inhabited blocks, close varied frontages and shared back courts; ceremonial precincts broad'
p['ro3StreetScaleRefinement']={'beforeSourceSHA256':digest,'moves':moves,'removedThroughLanes':sorted(removed),'oldRoadWidths':oldwidths,'minimumPublicStreetWidth':8,'districtStreetWidth':9,'circuitWidth':10,'ceremonialWidths':[14,12],'minimumVisibleFacadeGap':.75,'streetEnvelopeClearance':.35,'buildingModelsRescaled':False}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(p,indent=2)+'\n');print('RO3 STREET PLAN',len(p['lots']),'homes;',len(moves),'complete assemblies;',len(p['roads']),'public road objects',flush=True)
