"""Distinguish the existing continuous avenues from quieter flagstone courts.

Material-only source edit: preserve the concept layout, street widths, paving
meshes, UVs, ground heights and navigation. No road-placement override.
"""
import bpy,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('layout_id')=='wayfarer-concept-terraced-town-v49'
mat=bpy.data.materials.get('avenuePaving') or bpy.data.materials.new('avenuePaving')
mat.diffuse_color=(.60,.565,.48,1)
changed=[]
for o in bpy.data.collections['court-terrain'].objects:
    if o.type!='MESH' or not o.get('road_segment'):continue
    # Public avenues and the district circulation streets form one connected
    # network. Small doorstep lanes and the fountain/civic courts stay lighter.
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    width=(vs[0]-vs[3]).length
    if o.get('legacy_role')=='avenue' or width>=5.25 or o.name.startswith('south-bridge-road-'):
        o.data.materials.clear();o.data.materials.append(mat);changed.append(o.name)
scene['street_material_hierarchy_version']=56
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Source street material hierarchy:',len(changed),'existing segments; geometry unchanged',flush=True)
