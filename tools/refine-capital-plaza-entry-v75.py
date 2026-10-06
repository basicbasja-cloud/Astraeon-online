"""Correct one legacy assembly's geometric front, retaining all indexed parts."""
import bpy,json,hashlib,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;p=json.loads((R/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());m=p['plazaEntryCorrection'];assert s.get('capital_plaza_frontages')==75
if not s.get('capital_plaza_entry_correction'):
 assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==m['beforeSourceSHA256']
 c=bpy.data.collections[m['id']];members=set(c.objects);t=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
 for o in c.objects:
  par=o.parent
  while par and par not in members:par=par.parent
  if par is None:o.matrix_world=t@o.matrix_world
 for o in bpy.data.collections['court-terrain'].objects:
  if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=t@o.matrix_world
 if c.get('building_preset_json'):c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 os.environ['ASTRAEON_DEFER_NATIVE_SAVE']='1';runpy.run_path(str(R/'tools/refine-capital-gardens-v75.py'),run_name='__main__');del os.environ['ASTRAEON_DEFER_NATIVE_SAVE']
 s['capital_plaza_entry_correction']=75;s['capital_plan_json']=json.dumps(p,separators=(',',':'));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('NATIVE ACTUAL PLAZA ENTRY',s.get('capital_plaza_entry_correction'),flush=True)
