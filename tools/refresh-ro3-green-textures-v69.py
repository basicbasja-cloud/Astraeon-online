"""Apply reviewed leaf artwork and higher-resolution grass to native materials."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
leaf=json.loads((ROOT/'authoring/materials/wayfarer-foliage-v69.json').read_text());bpy.data.materials['foliageCutout']['texture_json']=json.dumps(leaf['texture'])
grass=json.loads((ROOT/'authoring/materials/wayfarer-street-v69.json').read_text())['materials']['groundcover']['texture'];grass['anisotropy']=4
for name in ['vergeGroundcover','vergeGroundcoverShade']:bpy.data.materials[name]['texture_json']=json.dumps(grass)
scene['ro3_tree_texture_review_json']=json.dumps({'foliage':leaf,'grassSize':[2048,2048],'obliqueAnisotropy':4,'treeGeometryPreserved':True})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Native leaf artwork1254, grass2048 and oblique4x sampling applied; rebake tree alpha shadows')
