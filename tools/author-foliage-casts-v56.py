"""Let the original leaf-card geometry cast alpha-aware ground shadows."""
import bpy,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];count=0
for o in bpy.data.objects:
    if o.type=='MESH' and o.get('render_visible',True) and o.data.materials and o.data.materials[0].name=='foliageCutout':
        o['shadow']=True;count+=1
bpy.context.scene['foliage_alpha_cast_version']=56
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Authored alpha-aware canopy casters:',count,flush=True)
