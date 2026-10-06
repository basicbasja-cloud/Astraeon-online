"""Measure actual visible neighborhood frontage gaps and preserve proof outlines."""
import argparse,json,hashlib,statistics
from pathlib import Path
from shapely.geometry import MultiPoint,Polygon
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v75';ap=argparse.ArgumentParser();ap.add_argument('--before',type=Path);args=ap.parse_args()
def outlines(source,plan):
 owners={o['id']:o for o in source['objects']};result={}
 for l in plan['lots']:
  poly=MultiPoint([v[:2] for a in owners[l['id']]['parts'] if a.get('visible',True) for v in a['vertices']]).convex_hull
  result[l['id']]={'center':l['center'],'outline':list(poly.exterior.coords)[:-1]}
 return result
basepath=O/'before-density/housing-footprints.json'
if args.before:
 raw=args.before.read_bytes();source=json.loads(raw);plan=json.loads((O/'before-density/plan.json').read_text());base={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'houses':outlines(source,plan)};basepath.write_text(json.dumps(base,indent=2)+'\n');del raw,source
base=json.loads(basepath.read_text());raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw);p=json.loads((O/'plan.json').read_text());now=outlines(s,p);polys={name:Polygon(o['outline']) for name,o in now.items()}
refinement=p.get('ro3StreetScaleRefinement',p.get('neighborhoodRefinement',p['densityRefinement']));changed={m['id'] for m in refinement['moves']}|set(refinement.get('added',[]));gaps=[]
for name in changed:
 poly=polys[name];nearest=min((poly.distance(other),owner) for owner,other in polys.items() if owner!=name);assert nearest[0]>.74,(name,nearest);gaps.append({'id':name,'nearestHouse':nearest[1],'visibleGap':round(nearest[0],5)})
def stats(items):
 neighborhood={name:Polygon(o['outline']) for name,o in items.items() if 50<o['center'][0]<206 and 82<o['center'][1]<239};near=[min(poly.distance(other) for owner,other in neighborhood.items() if owner!=name) for name,poly in neighborhood.items()]
 return {'homes':len(neighborhood),'medianNearestFacadeGap':statistics.median(near)}
actors=[a for o in s['objects'] for a in o.get('walkers',[])];assert len(actors)==28
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'beforeSHA256':base['sourceSHA256'],'beforeNeighborhood':stats(base['houses']),'afterNeighborhood':stats(now),'movedModules':len(refinement['moves']),'priorPerimeterTransfers':32,'infillHomes':len(refinement.get('added',[])),'houses':len(now),'ambientResidents':len(actors),'minimumChangedVisibleGap':min(a['visibleGap'] for a in gaps),'changedFrontages':gaps,'pass':True}
if p.get('ro3StreetScaleRefinement'):report['streetScale']={k:refinement[k] for k in ('minimumPublicStreetWidth','districtStreetWidth','circuitWidth','ceremonialWidths','removedThroughLanes','buildingModelsRescaled')}
(O/'density-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='changedFrontages'}))
