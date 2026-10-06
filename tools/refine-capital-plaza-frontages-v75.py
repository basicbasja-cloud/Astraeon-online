"""Apply complete square-facing models and keep their owned contacts coherent."""
import bpy,json,hashlib,math,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;p=json.loads((R/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());revision=p['plazaFrontageRefinement'];assert s.get('capital_inward_courts')==75
if not s.get('capital_plaza_frontages'):
 assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==revision['beforeSourceSHA256']
 terrain=bpy.data.collections['court-terrain']
 for m in revision['moves']:
  c=bpy.data.collections[m['id']];members=set(c.objects);t=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
  for o in c.objects:
   par=o.parent
   while par and par not in members:par=par.parent
   if par is None:o.matrix_world=t@o.matrix_world
  for o in terrain.objects:
   if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=t@o.matrix_world
  if c.get('building_preset_json'):c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 for m in revision['streetFurniture']:
  objects=[o for o in bpy.data.collections['capital-street-furniture'].objects if o.type=='MESH' and o.name.startswith(m['prefix'])];assert objects,m['prefix']
  for o in objects:o.matrix_world=Matrix.Translation(Vector(m['delta']))@o.matrix_world
 for m in revision['trees']:
  o=bpy.data.objects[m['id']+'-placement'];o.location.x,o.location.y=m['after']
 os.environ['ASTRAEON_DEFER_NATIVE_SAVE']='1';runpy.run_path(str(R/'tools/refine-capital-gardens-v75.py'),run_name='__main__');del os.environ['ASTRAEON_DEFER_NATIVE_SAVE']
 # Ground whole trees against the derived native face contacts after floor edits.
 bpy.context.view_layer.update();floors=[]
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
  trunk=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid');vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=(min(v.y for v in vs)+max(v.y for v in vs))/2;z=min(v.z for v in vs);ground=max([0]+[zz for poly,zz in floors if inside(x,y,poly)]);delta=ground-.015-z;members=set(c.objects)
  for o in c.objects:
   if o.parent not in members:o.matrix_world=Matrix.Translation(Vector((0,0,delta)))@o.matrix_world
 for court in p['courtyards']:bpy.data.collections['capital-'+court['id']]['capital_courtyard_json']=json.dumps(court)
 resident=bpy.data.objects['capital-resident-12'];assert resident.get('kind')=='walker';resident.parent=None;resident.matrix_world=Matrix.Identity(4);resident['route_json']=json.dumps([[x,y,0] for x,y in [[108,134],[117,130],[139,130],[149,137],[149,151],[139,158],[117,158],[108,150]]])
 stats=json.loads(s['capital_stats_json']);stats['plazaFacingFrontages']=len(revision['frontages']);stats['inwardFacingHomes']=sum(len(c['homes']) for c in p['courtyards']);s['capital_stats_json']=json.dumps(stats);s['capital_plaza_frontages']=75;s['capital_plan_json']=json.dumps(p,separators=(',',':'))
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('NATIVE PLAZA FRONTAGES',s.get('capital_plaza_frontages'),flush=True)
