"""Correct civic collection metadata without editing geometry or relaxing schemas."""
import bpy,json,runpy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert s.get('capital_architecture_revision')==76
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes()
expected=json.loads(raw);before=hashlib.sha256(raw).hexdigest();del raw
ids={a['id'] for a in json.loads(s['capital_plan_json'])['landmarks']}
assert len(ids)==3
for name in ids:
    c=bpy.data.collections[name];assert c.get('family') in ('guild','civic')
    c['family']='civic'
for o in expected['objects']:
    if o['id'] in ids:o['family']='civic'
export=runpy.run_path(str(R/'tools/export-world-v3.py'))['export']
actual=export(s)
assert actual==expected,'Civic metadata repair must leave all other exported data identical'
assert actual['lighting'].get('groundShadow'),'Unchanged geometry must retain the fresh ground bake'
del expected,actual
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
report={'beforeSourceSHA256':before,'afterSourceSHA256':hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest(),'civicIDs':sorted(ids),'geometryAndLightingUnchanged':True,'family':'civic'}
(R/'docs/review/wayfarer-capital-v76/civic-family-repair.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS native civic-family metadata correction; geometry and lighting identical',flush=True)
