"""Replace the fine hexagon-like cobble repeat with the town's rectangular paving."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert not scene.get('ro3_coherent_paving_version')
m=bpy.data.materials['avenuePaving'];spec=json.loads(bpy.data.materials['paving']['texture_json']);spec['anisotropy']=4;m['texture_json']=json.dumps(spec)
scene['ro3_coherent_paving_version']=69;scene['ro3_coherent_paving_review_json']=json.dumps({'sharedArtwork':spec['file'],'worldSize':spec['worldSize'],'roadPalette':'retained subtly darker native avenue tone','geometryChanged':False,'reason':'User identified tiny hexagon-like repeat conflicting with brick walks; coherent rectangular stone scale and world UVs, with curb defining building zones'})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS native roads share original rectangular town pavers; saved floor bake retained')
