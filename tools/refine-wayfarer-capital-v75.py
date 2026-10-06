"""Small native contact/ownership corrections after the integrated author pass."""
import bpy,bmesh,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75
if not s.get('capital_contact_refinement'):
 c=bpy.data.collections['capital-ambient-life'];target=bpy.data.collections['astral-fountain']
 for o in list(c.objects):c.objects.unlink(o);target.objects.link(o)
 del c['family']
 for name in ('food-market','market-spices','market-supplies','market-textiles'):
  c=bpy.data.collections[name]
  for o in c.objects:
   if not o.parent:o.matrix_world=Matrix.Translation(Vector((0,0,-.015)))@o.matrix_world
 s['capital_contact_refinement']=75
if not s.get('capital_counter_contacts'):
 bpy.context.view_layer.update()
 for name,pos in [('food-market',[182,153]),('market-spices',[194,153]),('market-supplies',[182,158]),('market-textiles',[194,158])]:
  c=bpy.data.collections[name];counter=bpy.data.objects[name+'-counter'];vs=[counter.matrix_world@v.co for v in counter.data.vertices];center=Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs),min(v.z for v in vs)))
  mat=Matrix.Translation(Vector((*pos,.025))-center);members=set(c.objects)
  for o in c.objects:
   par=o.parent;child=False
   while par:
    if par in members:child=True;break
    par=par.parent
   if not child:o.matrix_world=mat@o.matrix_world
 s['capital_counter_contacts']=75
if not s.get('capital_retained_contacts'):
 import subprocess
 baseline=json.loads(subprocess.check_output(['git','show','7b72b3f:world/v3/wayfarer-spatial.json'],cwd=ROOT))
 for a in baseline['terrain']['surfaces']:
  owner=a.get('objectId')
  if owner not in ('guild-hall','moon-shrine','astral-fountain') or not a['walkable'] or a['visible']:continue
  o=bpy.data.objects[a['id']];delta=[74,28,0] if owner=='guild-hall' else [108,75.5,0] if owner=='moon-shrine' else [74,91.25,0]
  o.matrix_world=Matrix.Translation(Vector(delta))@o.matrix_world;o['export_reference_only']=False;o['render_visible']=False
 for o in bpy.data.collections['court-terrain'].objects:
  if '-entry-contact-' in o.name or '-entry-tread-' in o.name:o['render_visible']=False
 s['capital_retained_contacts']=75
# Restore every retained native contact, including the hidden shrine landing.
# Align from its current first vertex so retries do not translate it twice.
plan=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text())
bpy.context.view_layer.update()
for a in plan['retainedFloors']:
 o=bpy.data.objects[a['id']];current=o.matrix_world@o.data.vertices[0].co;delta=Vector(a['vertices'][0])-current
 if delta.length>.000001:o.matrix_world=Matrix.Translation(delta)@o.matrix_world
 o['export_reference_only']=False
s['capital_plan_json']=json.dumps(plan,separators=(',',':'))
if not s.get('capital_floor_normals'):
 for o in bpy.data.collections['court-terrain'].objects:
  if o.type!='MESH' or o.get('export_reference_only'):continue
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if f.normal.z<-.5]
  if faces:bmesh.ops.reverse_faces(bm,faces=faces)
  bm.to_mesh(o.data);bm.free()
 s['capital_floor_normals']=75
for c in bpy.data.collections:
 if not c.get('building_preset_json'):continue
 preset=json.loads(c['building_preset_json'])
 if preset.get('clay')=='roofSlateBlue':preset['clay']='roofClayWarm';c['building_preset_json']=json.dumps(preset)
 for o in c.objects:
  if o.type=='MESH' and o.data.materials[0].name=='roofSlateBlue':o.data.materials[0]=bpy.data.materials['roofClayWarm']
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
