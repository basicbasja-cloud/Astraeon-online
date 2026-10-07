"""Version the refreshed floor atlas so old cache83 clients cannot mix bakes."""
import bpy, json, hashlib, runpy, subprocess, struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert s.get('capital_property_frontages')==1
new='assets/wayfarer-ground-shadow-v76-frontages.png'
bake=json.loads(s['ground_shadow_bake_json']);old=bake['file']
assert old=='assets/wayfarer-ground-shadow-v75.png',old
bits=(R/old).read_bytes();assert struct.unpack('>II',bits[16:24])==(4096,4096)
assert not (R/new).exists() or (R/new).read_bytes()==bits
(R/new).write_bytes(bits)
s['ground_shadow_asset']=new;bake['file']=new
s['ground_shadow_bake_json']=json.dumps(bake,separators=(',',':'))
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));data=exporter['export'](s)
assert data['lighting']['groundShadow']==bake,'Versioned atlas must retain source-matched geometry'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
# Preserve the checkpoint atlas for historical sources and future comparisons.
original=subprocess.check_output(['git','show','d7f9f15:'+old],cwd=R)
(R/old).write_bytes(original)
receipt={'oldFile':old,'file':new,'SHA256':hashlib.sha256(bits).hexdigest(),
         'resolution':4096,'geometryDigest':bake['geometryDigest'],
         'checkpointAtlasRestored':True,'pixelBytesPreserved':True}
(R/'docs/review/wayfarer-capital-v76/property-frontages/atlas-version.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
