"""Apply reviewed broad city streets by rigidly moving complete native models."""
import hashlib,json,math,runpy
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert s.get('capital_continuous_neighborhoods')==75
p=json.loads((R/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());revision=p['ro3StreetScaleRefinement'];terrain=bpy.data.collections['court-terrain']
if not s.get('capital_ro3_street_scale'):
 assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==revision['beforeSourceSHA256'],'Street-scale update requires its recorded complete native baseline'
 for m in revision['moves']:
  c=bpy.data.collections[m['id']];assert c.get('family') in ('residential','market','workshop','inn')
  transform=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
  members=set(c.objects)
  for o in c.objects:
   par=o.parent
   while par and par not in members:par=par.parent
   if par is None:o.matrix_world=transform@o.matrix_world
  for o in terrain.objects:
   if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=transform@o.matrix_world
  if c.get('building_preset_json'):c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 # Old lane metadata must leave the export as well as the paving plan.
 for o in terrain.objects:
  if o.get('road_segment') and any(o.name.startswith(n+'-') for n in revision['removedThroughLanes']):o['export_reference_only']=True
 for road in p['roads']:
  for j,(a,b) in enumerate(zip(road['centerline'],road['centerline'][1:])):
   o=bpy.data.objects[road['id']+'-'+str(j)];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2
   pts=[[a[0]+nx,a[1]+ny,.025],[b[0]+nx,b[1]+ny,.025],[b[0]-nx,b[1]-ny,.025],[a[0]-nx,a[1]-ny,.025]]
   for v,q in zip(o.data.vertices,pts):v.co=q
   o['export_reference_only']=False;o['road_width']=road['width'];o['legacy_role']='avenue';o['centerline_json']=json.dumps([a,b])
 s['capital_ro3_street_scale']=75
 runpy.run_path(str(R/'tools/refine-capital-gardens-v75.py'),run_name='__main__')
 bpy.context.view_layer.update()
 floors=[]
 for a in p['floors']+p['retainedFloors']:
  for face in a['faces']:
   vs=[a['vertices'][i] for i in face];floors.append(([(v[0],v[1]) for v in vs],max(v[2] for v in vs)))
 def inside(x,y,poly):
  hit=False
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 for c in bpy.data.collections:
  if c.get('family')!='vegetation':continue
  trunk=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid');vs=[trunk.matrix_world@v.co for v in trunk.data.vertices]
  x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=(min(v.y for v in vs)+max(v.y for v in vs))/2;z=min(v.z for v in vs)
  ground=max([0]+[zz for poly,zz in floors if inside(x,y,poly)]);delta=ground-.015-z;members=set(c.objects)
  for o in c.objects:
   if o.parent not in members:o.matrix_world=Matrix.Translation(Vector((0,0,delta)))@o.matrix_world
 stats=json.loads(s['capital_stats_json']);stats.update(ro3StreetScale=True,publicRoads=len(p['roads']),minimumPublicStreetWidth=8,districtStreetWidth=9,circuitWidth=10);s['capital_stats_json']=json.dumps(stats)
 s['capital_plan_json']=json.dumps(p,separators=(',',':'));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
 runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Native RO3-scale capital streets',s['capital_stats_json'],flush=True)
