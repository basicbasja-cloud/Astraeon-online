"""Read third-party data only; no embedded scripts or re-saving external source."""
import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]);out=Path(args[1])
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
data={'source':str(source),'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions],
      'objects':[],'scene_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end]}
for o in bpy.data.objects:
    item={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'parent_bone':o.parent_bone,
          'active_action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
          'location':list(o.location),'rotation':list(o.rotation_euler)}
    if o.type=='ARMATURE':item['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local)} for b in o.data.bones]
    if o.type=='MESH':item['vertices']=len(o.data.vertices);item['groups']=[g.name for g in o.vertex_groups]
    data['objects'].append(item)
out.write_text(json.dumps(data,indent=2));print('SOURCE_INSPECTED',data['scene_range'],data['actions'])
