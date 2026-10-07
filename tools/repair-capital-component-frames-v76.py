"""Recover stale-parent packed coordinates and assert the actual local envelope.

Applies the exact evaluated placement matrix only to out-of-frame new parts.
All inherited art, indexed faces and UVs are untouched. No regenerated city.
"""
import json,bpy,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_architecture_revision')==76
bpy.context.view_layer.update();repairs=[]
for c in bpy.data.collections:
 preset=c.get('building_preset_json') or c.get('capital_landmark_json')
 if not preset:continue
 l=json.loads(preset);r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);w,d=l['width'],l['depth']
 def local(q):return abs(q.x)<=w/2+2 and abs(q.y)<=d/2+2
 for o in c.objects:
  if o.type!='MESH':continue
  vertices=list(o.data.vertices);bad=[v for v in vertices if not local(v.co)]
  if not bad:continue
  assert len(bad)==len(vertices),('Mixed transform frames require component inspection',o.name,len(bad),len(vertices))
  repaired=[r.matrix_world@v.co for v in vertices]
  assert all(local(q) for q in repaired),('Not the exact stale-parent transform',o.name)
  for v,q in zip(vertices,repaired):v.co=q
  o.data.update();repairs.append({'owner':c.name,'part':o.name,'vertices':len(vertices),'exactPlacementTransformApplied':True});print('RECOVERED NATIVE FRAME',o.name,len(vertices),flush=True)
assert repairs or s.get('capital_component_frames_repaired'), 'No transform issue found; inspect before claiming a repair'
s['capital_component_frames_repaired']=76
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
(R/'docs/review/wayfarer-capital-v76/component-frame-repair.json').write_text(json.dumps({'architectureRevision':76,'repairedParts':repairs,'inheritedAssembliesUntouched':True,'facesAndUVsRetained':True},indent=2)+'\n')
