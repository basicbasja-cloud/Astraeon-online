"""Stronger directional sunlight versus cool fill, authored in the source.

No texture sharpening. The same sun vector and source AO remain authoritative.
Rebake native floor shadows after saving; inspect actual gameplay to judge it.
"""
import bpy,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('side_facade_version')==59
scene['ambient']=.36;scene['sun_strength']=.72;scene['sun_balance_version']=60
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved sunlight/fill balance .72/.36; native shadow rebake required',flush=True)
