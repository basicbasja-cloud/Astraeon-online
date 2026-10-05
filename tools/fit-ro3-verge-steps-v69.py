"""Remove the eight trial patches spanning a native step; retain rooted grass.

Run on the first source69 trial, before final bakes. Tag source plant meshes so
Blender's 63-character name truncation cannot confuse blades with groundcover.
The main author now rejects step crossings before creating plants.
"""
import json
import runpy
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
removed=[]
for c in bpy.data.collections:
    bad_centers=[]
    for o in list(c.objects):
        if o.type!='MESH' or not o.name.startswith('ro3-v69-') or '-foundation-green-' not in o.name:continue
        if o.get('street_v69_patch') or len(o.data.vertices)==5:
            o['street_v69_patch']=True
            if max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)>.13:
                bad_centers.append(sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/5)
                removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
        else:o['street_v69_blade']=True
    for o in list(c.objects):
        if not o.get('street_v69_blade'):continue
        root=o.matrix_world@o.data.vertices[0].co
        if any((root.xy-p.xy).length<1.0 for p in bad_centers):bpy.data.objects.remove(o,do_unlink=True)
review=json.loads(scene['ro3_street_review_json'])
review['patches']=[p for p in review['patches'] if p['id'] not in removed]
review['removedStepCrossings']=removed
scene['ro3_street_review_json']=json.dumps(review)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Removed',len(removed),'step-crossing patches; retained',len(review['patches']),'grounded patches')
