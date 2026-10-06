"""Derive native transforms, raised contacts and clipped public/private floors."""
import json,math,subprocess
from pathlib import Path
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely.affinity import translate,rotate
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'docs/review/wayfarer-capital-v75'
s=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
if s.get('layoutId')=='wayfarer-regional-capital-v75':s=json.loads(subprocess.check_output(['git','show','7b72b3f:world/v3/wayfarer-spatial.json'],cwd=ROOT))
assert s['layoutId']=='wayfarer-concept-terraced-town-v49'
p=json.loads((out/'plan.json').read_text());assert p['royalGeometricCity'];roots=json.loads((out/'source74-roots.json').read_text());contacts=json.loads((out/'source74-ground.json').read_text())
transforms={}
for name,(dx,dy) in p['fixedTranslations'].items():transforms[name]={'before':[0,0,0],'after':[dx,dy,0],'rotation':0}
for l in p['lots']:
 if l['existing'] and not l.get('fixed'):
  old=contacts[l['id']];transforms[l['id']]={'before':[*old['center'],old['floor']],'after':[*l['center'],.04],'rotation':l['angle']-roots[l['id']]['angle']}
# Exact existing landmark floor geometry travels with the models.
keep=[];civic=[74,28];shrine=[108,75.5];plaza=[74,91.25]
for a in s['terrain']['surfaces']:
 if not a['walkable'] or a['id'].startswith('blueprint72-'):continue
 vs=a['vertices'];xc=sum(v[0] for v in vs)/len(vs);yc=sum(v[1] for v in vs)/len(vs);maxz=max(v[2] for v in vs);delta=None
 if a.get('objectId') in ('guild-hall','moon-shrine'):delta=p['fixedTranslations'][a['objectId']]
 elif a.get('objectId')=='astral-fountain':delta=plaza
 elif (a['id'].startswith('terrace-v49-') or a['id']=='civic-terrace' or a['id']=='civic-terrace-private74') and maxz>.12:delta=civic
 elif maxz>.08 and 80<xc<92 and 17<yc<28:delta=shrine
 if delta:
  clone={k:v for k,v in a.items() if k not in ('polygon','centerline','width','legacyRole','uvs')};clone['vertices']=[[v[0]+delta[0],v[1]+delta[1],v[2]] for v in vs];keep.append(clone)
def region(m):return unary_union([Polygon([m['vertices'][i][:2] for i in f]) for f in m['faces'] if abs(Polygon([m['vertices'][i][:2] for i in f]).area)>.000001])
retained=unary_union([region(m) for m in keep if m.get('visible',True)]);land=Polygon(p['land']);parks=unary_union([Polygon(x['polygon']) for x in p['parks']]);private=unary_union([Polygon(l['lot']).buffer(.08,join_style=2) for l in p['lots']]+[box(x['center'][0]-x['width']/2-2,x['center'][1]-x['depth']/2-2,x['center'][0]+x['width']/2+2,x['center'][1]+x['depth']/2+3) for x in p['landmarks']])
# Merge neighboring plots into coherent owned blocks, clipped clear of avenues.
street_region=unary_union([LineString(a['centerline']).buffer(a['width']/2,cap_style=2,join_style=2) for a in p['roads']])
private=private.buffer(.48,join_style=2).buffer(-.48,join_style=2).intersection(land).difference(parks).difference(retained).difference(street_region)
if p.get('neighborhoodRefinement'):
 # Curbs define the shared building-block edge beside the walking street.
 # Continuous owned paving replaces separate rectangular island aprons.
 from shapely.geometry import Point
 interior=box(20,84,236,237) if p.get('ro3StreetScaleRefinement') else box(51,84,205,237)
 core=interior.difference(street_region).difference(parks).difference(retained)
 royal_court=box(108,132,148,156).buffer(4,quad_segs=12).difference(retained)
 core=core.difference(royal_court).difference(box(174,145,203,165))
 parcels=list(core.geoms) if hasattr(core,'geoms') else [core]
 inhabited=[a for a in parcels if any(a.covers(Point(*l['center'])) for l in p['lots'])]
 private=unary_union([private,*inhabited]).difference(royal_court).difference(street_region).difference(parks).difference(retained)
 p['curbStrategy']='Continuous shared residential/building-block boundaries beside walking streets; individual island aprons removed in neighborhoods'

public=land.difference(private).difference(parks).difference(retained)
# Roads outside the perimeter are actual authored bridge contacts.
bridge=unary_union([box(2,138,24,150),box(234,138,254,150),box(121,260,135,281),box(123.5,6,132.5,35)]);public=unary_union([public,bridge]).difference(retained)
def mesh(poly,z):
 pts=[];faces=[];index={}
 for t in constrained_delaunay_triangles(poly).geoms:
  f=[]
  for x,y in list(t.exterior.coords)[:-1]:
   key=(round(x,5),round(y,5))
   if key not in index:index[key]=len(pts);pts.append([*key,z])
   f.append(index[key])
  a,b,c=[pts[i] for i in f[:3]]
  if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:f.reverse()
  faces.append(f)
 return {'vertices':pts,'faces':faces}
court=box(108,132,148,156).buffer(4,quad_segs=12).difference(retained)
public=public.difference(court)
floors=[{'id':'capital-royal-plaza','material':'publicTownStone','role':'plaza',**mesh(court,.025)}]
for y in range(0,288,16):
 for x in range(0,256,16):
  cell=box(x,y,x+16,y+16)
  for name,reg,mat,z,role in [('public',public,'publicTownStone',.025,'forecourt'),('private',private,'houseApronPaving',.04,'yard')]:
   clip=reg.intersection(cell)
   if clip.area>.001:floors.append({'id':f'capital-{name}-{x}-{y}','material':mat,'role':role,**mesh(clip,z)})
for park in p['parks']:floors.append({'id':'capital-'+park['name'].lower().replace(' ','-'),'material':'grass','role':'garden',**mesh(Polygon(park['polygon']),.035)})
# Closed textured curb bands; exact face union avoids filling their court holes.
loops=[];owned_blocks=[]
for i,zone in enumerate(private.geoms if hasattr(private,'geoms') else [private]):
 if zone.area<.2:continue
 zone=orient(zone,sign=1.0)
 owned_blocks.append({'outer':list(zone.exterior.coords)[:-1],'holes':[list(ring.coords)[:-1] for ring in zone.interiors]})
 loops.append(list(zone.exterior.coords)[:-1]);loops.extend(list(ring.coords)[:-1] for ring in zone.interiors);band=zone.difference(zone.buffer(-.22,join_style=2))
 floors.append({'id':f'capital-owned-curb-{i}','material':'roadCurbStone','role':'forecourt',**mesh(band,.20)})
# Flat formal fountain court is in the continuous public union; the existing
# complete fountain and its two actual stone steps keep their original scale.
p.update(ownedBlocks=owned_blocks,transforms=transforms,retainedFloors=keep,floors=floors,privateLoops=loops,groundMesh=mesh(land,0),groundArea=land.area,privateArea=private.area,publicArea=public.area,raisedArea=retained.area)
(out/'native-plan.json').write_text(json.dumps(p,separators=(',',':'))+'\n')
print('NATIVE PLAN',len(transforms),'existing assemblies;',len(keep),'retained contact meshes;',len(floors),'clipped floors;',len(owned_blocks),'owned blocks;',len(loops),'boundary loops')
