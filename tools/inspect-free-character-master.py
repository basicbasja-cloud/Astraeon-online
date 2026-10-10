from pathlib import Path
import json
import bpy
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/free-master-01'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'grip-master.blend'))
body=bpy.data.objects['CanonicalBody'];rig=bpy.data.objects['ASTRAEON_SourceRig']
result={'source':'grip-master.blend','bones':{},'groups':{}}
for name in ['head','neck01','neck03','eye.R','wrist.R','finger2-1.R','finger5-1.R']:
    b=rig.pose.bones[name];result['bones'][name]={'head':list(b.head),'tail':list(b.tail)}
for name in ['scalp','body','ears','lips']:
    g=body.vertex_groups[name].index
    ids=[v.index for v in body.data.vertices if any(q.group==g and q.weight>.5 for q in v.groups)]
    coords=[body.data.shape_keys.key_blocks[0].data[i].co for i in ids]
    result['groups'][name]={'count':len(ids),'bounds':[[min(p[j] for p in coords),max(p[j] for p in coords)] for j in range(3)]}
(OUT/'source-inspection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
