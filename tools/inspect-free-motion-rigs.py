"""Inspect creator GLB skeleton/actions as data in an isolated Blender process."""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.character-tools/free-assets/quaternius-motions'
catalog=[]
for pack in ['universal-animation-library','universal-animation-library-2']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    paths=[p for p in (DEST/pack).rglob('*.glb') if 'Standard.glb' in p.name]
    assert len(paths)==1, paths
    bpy.ops.import_scene.gltf(filepath=str(paths[0]))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    rig=max(rigs,key=lambda r:len(r.data.bones)); actions=[]
    for a in bpy.data.actions:
        actions.append({'name':a.name,'range':list(a.frame_range),'slots':[slot.identifier for slot in a.slots]})
    record={'pack':pack,'path':str(paths[0].relative_to(ROOT)),'rig':rig.name,'worldMatrix':[list(row) for row in rig.matrix_world],
            'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None,
                             'matrix':[list(row) for row in b.matrix_local]} for b in rig.data.bones},
            'actions':actions,'fps':bpy.context.scene.render.fps}
    catalog.append(record)
    print('MOTION_CATALOG '+json.dumps({'pack':pack,'bones':len(record['bones']),'fps':record['fps'],'actions':actions}),flush=True)
(DEST/'rig-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
