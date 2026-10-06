"""Organize actual complete house modules into continuous street-facing rows."""
import json,math,hashlib,argparse
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString,box
from shapely.ops import unary_union
from shapely.affinity import translate,rotate
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'world/v3/wayfarer-spatial.json');ap.add_argument('--plan',type=Path,default=O/'plan.json');args=ap.parse_args();p=json.loads(args.plan.read_text());assert not p.get('neighborhoodRefinement'),'Reviewed neighborhood plan already exists';raw=args.source.read_bytes();s=json.loads(raw);owners={o['id']:o for o in s['objects']}
# Preserve complete original service/civic precincts; reorganize movable homes.
def outline(owner):return MultiPoint([v[:2] for a in owner['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull
lots=p['lots'];movable=[l for l in lots if not l.get('fixed')];fixedhomes=[l for l in lots if l.get('fixed')];local={l['id']:rotate(translate(outline(owners[l['id']]),-l['center'][0],-l['center'][1]),-l['angle']*180/math.pi,origin=(0,0)) for l in movable}
# A small native module completes a frontage, rather than occupying a large plot.
for i in range(32):
 l={'id':f'capital-neighborhood-{i:03}','existing':False,'family':'residential','district':'Neighborhoods','center':[0,0],'angle':0,'lot':[],'road':'','width':4.2,'depth':6.4,'floors':2+(i%6==0),'roof':'gable','clay':['roofClayWarm','roofClayOchre','roofClayRose'][i%3],'balcony':False,'wing':False,'garden':i%3==0,'denseTownhouse':True,'neighborhoodInfill':True};movable.append(l);local[l['id']]=box(-2.85,-3.9,2.85,4.4)
land=Polygon(p['land']).buffer(-2);roads={r['id']:r for r in p['roads']};streetzone=unary_union([LineString(r['centerline']).buffer(r['width']/2+.3,cap_style=2,join_style=2) for r in p['roads']]);reserved=unary_union([box(102,126,154,162),box(97,32,159,76),box(174,145,203,165),box(179,86,205,110)]+[Polygon(a['polygon']).buffer(.25) for a in p['parks']])
occupied={l['id']:outline(owners[l['id']]) for l in fixedhomes};obstacles=[]
for o in s['objects']:
 if o['id'] in {l['id'] for l in lots} or o['id'] in ('capital-river-bank','capital-waterline','capital-curtain-walls','capital-owned-block-boundaries'):continue
 for a in o['parts']:
  if a['role']=='solid':obstacles.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.3))
obstacles=unary_union(obstacles);moves=[];placed=[];remaining=list(movable)
def acceptable(q):return land.covers(q) and q.intersection(streetzone).area<.001 and q.intersection(reserved).area<.001 and q.intersection(obstacles).area<.001 and all(q.distance(v)>=.75 for v in occupied.values())
def assign(l,x,y,angle,road,q):
 if not l.get('neighborhoodInfill'):moves.append({'id':l['id'],'before':l['center'][:],'after':[round(x,4),round(y,4)],'rotation':angle-l['angle']})
 district='Artisan Ward' if x<104 and 144<y<212 else 'Seafarer Ward' if x<104 and y<144 else 'South Commons' if x<128 else 'Lantern Market' if y<184 else 'Willow Borough'
 l.update(center=[round(x,4),round(y,4)],angle=angle,road=road,district=district,lot=list(q.buffer(.18,join_style=2).exterior.coords)[:-1],continuousFrontage=True);placed.append(l);remaining.remove(l);occupied[l['id']]=q
# Each block has a street face and a back courtyard. Both sides of a walking
# route are packed in matching runs, with full roof/awning envelopes separated.
runs=[]
for roadname in ['west-district-spine','east-district-spine','royal-boulevard-south','royal-boulevard-north','inner-west-street','inner-east-street','capital-circuit']:
 r=roads[roadname]
 for a,b in zip(r['centerline'],r['centerline'][1:]):
  if a[0]!=b[0]:continue
  lo,hi=sorted([a[1],b[1]])
  for ya,yb in [(84,108),(116,137),(151,180),(188,212),(220,236)]:
   ya,yb=max(ya,lo+1),min(yb,hi-1)
   if yb-ya<6:continue
   for side in (-1,1):runs.append((roadname,a[0],side,ya,yb,r['width']))
for roadname,axis,side,start,end,width in runs:
 cursor=start;angle=math.pi/2 if side>0 else -math.pi/2;count=0
 while cursor<end and remaining:
  success=False
  # Use compact frontage modules first. Large inherited houses fit the wider
  # residual courts and secondary row ends in the next pass.
  for l in sorted(remaining,key=lambda l:(local[l['id']].bounds[2]-local[l['id']].bounds[0],not l['existing'],l['id'])):
   shape=rotate(local[l['id']],angle*180/math.pi,origin=(0,0));x=axis+side*(width/2+local[l['id']].bounds[3]+.35);y=cursor-shape.bounds[1];q=translate(shape,x,y)
   if q.bounds[3]>end:continue
   if not acceptable(q):continue
   assign(l,x,y,angle,roadname,q);cursor=q.bounds[3]+.8;count+=1;success=True;break
  if not success:cursor+=.5
 if count:print('ROW',roadname,side,start,end,count,flush=True)
# Finish cross-street faces, keeping true shared courtyards rather than isolated
# private squares. All placement choices are cardinal and backed by a street.
for l in sorted(remaining[:],key=lambda l:(not l['existing'],-local[l['id']].area)):
 chosen=None
 for r in p['roads']:
  for a,b in zip(r['centerline'],r['centerline'][1:]):
   horizontal=a[1]==b[1];lo=min(a[0],b[0]) if horizontal else min(a[1],b[1]);hi=max(a[0],b[0]) if horizontal else max(a[1],b[1])
   for side in (-1,1):
    angle=(math.pi if side>0 else 0) if horizontal else (math.pi/2 if side>0 else -math.pi/2);shape=rotate(local[l['id']],angle*180/math.pi,origin=(0,0));offset=r['width']/2+local[l['id']].bounds[3]+.35
    for t in range(math.ceil(lo+5),math.floor(hi-4)):
     x,y=(t,a[1]+side*offset) if horizontal else (a[0]+side*offset,t)
     if not (22<x<234 and 35<y<262):continue
     q=translate(shape,x,y)
     if acceptable(q):
      nearest=min(q.distance(v) for v in occupied.values());score=(0 if 50<x<206 and 82<y<239 else 100)+nearest
      if chosen is None or score<chosen[0]:chosen=(score,x,y,angle,r['id'],q)
 if chosen:
  _,x,y,angle,road,q=chosen;assign(l,x,y,angle,road,q)
 else:print('UNPLACED',l['id'],flush=True)
assert not remaining,[l['id'] for l in remaining]
p['lots']=fixedhomes+placed;p['newHouses']=sum(not l['existing'] for l in p['lots']);p['densityStrategy']='Continuous street-facing neighborhood rows, paired frontages, shared back courtyards and narrow side passages; ceremonial precincts remain broad';p['neighborhoodRefinement']={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'moves':moves,'added':[l['id'] for l in placed if l.get('neighborhoodInfill')],'rowRuns':len(runs),'streetEnvelopeClearance':.3,'minimumFacadeSeparation':.75};p['ambientPopulation']=28
(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print('NEIGHBORHOOD PLAN',len(p['lots']),'homes;',len(moves),'complete modules reorganized;',len(p['neighborhoodRefinement']['added']),'new homes',flush=True)
