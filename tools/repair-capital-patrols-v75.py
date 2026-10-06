"""Apply exact-scene patrol detours to native authored walker paths."""
import bpy,json,runpy,os,hashlib
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1];report=json.loads((ROOT/os.environ.get('ASTRAEON_TRAVERSAL_REPORT','docs/review/wayfarer-capital-v75/traversal-final.json')).read_text());assert bpy.context.scene.get('capital_version')==75
assert report.get('sourceSHA256')==hashlib.sha256((ROOT/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest(),'Patrol repairs require a report from the current exact city source'
for name,route in report['repairs'].items():
 route=[p for i,p in enumerate(route) if not i or sum((p[j]-route[i-1][j])**2 for j in (0,1))>.000001]
 while len(route)>1 and sum((route[-1][j]-route[0][j])**2 for j in (0,1))<.000001:route.pop()
 o=bpy.data.objects[name];assert o.get('kind')=='walker' and not o.parent;o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([[*p,0] for p in route])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Patrol detours',len(report['repairs']),flush=True)
