"""Extract native blueprint evidence and floor/collision contacts after authoring."""
import bpy,json,runpy,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;exp=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exp['export'](scene);record=json.loads(scene['ro3_blueprint_review_json']);args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);before=json.loads(Path(args[1]).read_text());curbNames={r['id'] for r in record['curbs']};surfs={s['id']:s for s in w['terrain']['surfaces']};baseline={o['id']:o for o in before['objects']};changes=[]
for key in ('navigation','spawn','safeSpawn','route','districts'):assert w.get(key)==before.get(key),(key,'unexpected metadata change')
for o in w['objects']:
 old=baseline[o['id']];op={p['id']:p for p in old['parts']};assert {p['id'] for p in o['parts']}==set(op)
 for p in o['parts']:
  prev=op[p['id']]
  for key in ('role','shadow','material','faces','uvs','visible'):assert p.get(key)==prev.get(key),(p['id'],key)
  if p['vertices']!=prev['vertices']:changes.append(p['id'])
report={**record,'nativeChangedParts':changes,'status':'in_progress','source':w['source'],'objectCount':len(w['objects']),'actorAndNavigationMetadataPreserved':True,'curbTriangles':sum(len(surfs[name]['faces']) for name in curbNames),'groundShadow':w['lighting'].get('groundShadow')}
out.write_text(json.dumps(report,indent=2)+'\n');print('Native blueprint extracted',report['curbTriangles'],'curb faces;',len(changes),'translated parts')
