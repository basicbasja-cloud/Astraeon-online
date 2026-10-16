"""Independent readback of saved original retarget; projected driver, not painted-joint truth."""
from pathlib import Path
import bpy,json,math,hashlib
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;blend=P/'source/unarmed-inplace.blend';receipt=json.loads((P/'source/authoring-receipt.json').read_text());assert hashlib.sha256(blend.read_bytes()).hexdigest()==receipt['blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;rig=bpy.data.objects['Astraeon_Free_Local'];views=['S','W','N','E'];cams={v:bpy.data.objects[v] for v in views};sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;gem=bpy.data.objects['collectible'];gem.hide_render=True
def capture():
 bones={};project={v:{} for v in views}
 for b in rig.pose.bones:
  bones[b.name]={}
  for edge in ['head','tail']:
   w=rig.matrix_world@getattr(b,edge);bones[b.name][edge]=list(w)
   for v in views:
    q=world_to_camera_view(sc,cams[v],w);project[v].setdefault(b.name,{})[edge]=[q.x*384,(1-q.y)*512]
 headq=(rig.matrix_world@rig.pose.bones['head'].matrix).to_quaternion();up=(headq@Quaternion(receipt['neutral_bones']['head']['rotation_wxyz']).inverted())@Vector((0,0,1));return {'world_bones':bones,'projected':project,'head_up_world':list(up)}
# Neutral is the frozen original standing reference, not the first guard pose.
neutral=receipt['neutral_bones'];projection={v:{} for v in views}
from mathutils import Vector,Quaternion
for v in views:
 for n,a in neutral.items():
  projection[v][n]={}
  for edge in ['head','tail']:
   q=world_to_camera_view(sc,cams[v],Vector(a[edge]));projection[v][n][edge]=[q.x*384,(1-q.y)*512]
clips={};checks=[];worst_ankle=0;worst_length=0;worst_floor=0
for key,a in receipt['actions'].items():
 rig.animation_data.action=bpy.data.actions[a['action']];frames=[]
 for i in range(1025):
  frame=1+i/4;sc.frame_set(math.floor(frame),subframe=frame-math.floor(frame));gem.hide_render=True;bpy.context.view_layer.update()
  for side in ['left','right']:
   foot=rig.matrix_world@rig.pose.bones[side+'.foot'].head;target=Vector(receipt['fixed_guard_feet_world'][side]);worst_ankle=max(worst_ankle,(foot-target).length)
   obj=bpy.data.objects[side+'.sole'];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();z=min((ev.matrix_world@v.co).z for v in mesh.vertices);ev.to_mesh_clear();worst_floor=max(worst_floor,abs(z))
  for n,b in rig.pose.bones.items():
   length=(rig.matrix_world@b.tail-rig.matrix_world@b.head).length;expected=(Vector(neutral[n]['tail'])-Vector(neutral[n]['head'])).length;worst_length=max(worst_length,abs(length-expected))
  if i%4==0:frames.append({'index':i//4,'phase':i/1024,**capture()})
 clips[key]={'duration_ms':a['duration_ms'],'frames':frames,'source_clip':a['source_clip']};print('READBACK',key,len(frames),flush=True)
data={'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'external_source_sha256':receipt['external_source_sha256'],'neutral_world':neutral,'neutral_projection':projection,'cameras':{v:[list(row) for row in cams[v].matrix_world] for v in views},'clips':clips,'scope':'Actual saved retargeted3D source, explicitly in-place adaptation. No original painted joint recovery or completed art approval.'};(P/'source/retargeted-endpoints.json').write_text(json.dumps(data,separators=(',',':'))+'\n');r={'samples_per_action':1025,'max_ankle_target_error_m':worst_ankle,'max_bone_length_change_m':worst_length,'max_actual_sole_floor_error_m':worst_floor,'budgets_m':{'ankle':.001,'bone_length':.0001,'sole_floor':.001},'source_geometry_pass':worst_ankle<=.001 and worst_length<=.0001 and worst_floor<=.001,'production_pass':False};(P/'source/source-geometry-review.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
if not r['source_geometry_pass']:raise ValueError('Saved source geometry failed')
