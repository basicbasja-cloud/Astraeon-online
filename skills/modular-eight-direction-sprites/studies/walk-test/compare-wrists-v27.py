import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];out=R/'research/sprite-animation/weighted-slash-v27/evidence'
def angle(a,b):return math.degrees(a.normalized().angle(b.normalized()))
def audit(path,rig,forearm,hand,hip,shoulders,frames,weapon=None):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);r=bpy.data.objects[rig];rest=r.data.bones;relrest=rest[forearm].matrix_local.to_3x3().transposed()@rest[hand].matrix_local.to_3x3();rows=[]
 for t in frames:
  bpy.context.scene.frame_set(t);bpy.context.view_layer.update();f=r.pose.bones[forearm];h=r.pose.bones[hand];relative=f.matrix.to_3x3().normalized().transposed()@h.matrix.to_3x3().normalized();delta=relative@relrest.transposed();shoulder=sum((r.pose.bones[n].head for n in shoulders),Vector())/2;trunk=r.matrix_world.to_3x3()@(shoulder-r.pose.bones[hip].head)
  row={'time_or_native_frame':t,'hand_relative_forearm_rotation_from_rest_degrees':math.degrees(delta.to_quaternion().angle),'trunk_angle_to_world_vertical_degrees':angle(trunk,Vector((0,0,1))),'hip_local':list(r.pose.bones[hip].head),'forearm_axis_hand_axis_degrees':angle(h.matrix.to_3x3().col[1],h.head-f.head),'hand_matrix_local':[list(x) for x in h.matrix]}
  if weapon:
   obj=bpy.data.objects[weapon].evaluated_get(bpy.context.evaluated_depsgraph_get());verts=[obj.matrix_world@v.co for v in obj.data.vertices];tip=min(range(len(obj.data.vertices)),key=lambda i:obj.data.vertices[i].co.x);base=max(range(len(obj.data.vertices)),key=lambda i:obj.data.vertices[i].co.x);axis=(verts[tip]-verts[base]).normalized();handlocal=(r.matrix_world@h.matrix).to_3x3().normalized().transposed()@axis;row['actual_blade_axis_hand_local']=list(handlocal);row['actual_blade_plane_normal_hand_local']=list((r.matrix_world@h.matrix).to_3x3().normalized().transposed()@obj.matrix_world.to_3x3().col[2].normalized())
  rows.append(row)
 return {'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':rows,'rest_hand_matrix':[list(x) for x in rest[hand].matrix_local],'bone_names':[b.name for b in rest]}
a=audit(R/'research/sprite-animation/combat-gait-study-v23/source/flare-shortsword.blend','MaleArm','Forearm.Right','Hand.Right','Hip',['Upperarm.Right','Upperarm.Left'],[13,14,15,16],'Shortsword')
b=audit(R/'research/sprite-animation/weighted-slash-v27/rig-source/weighted-slash.blend','original.walk.rig','lowerarm_r','hand_r','pelvis',['upperarm_r','upperarm_l'],[0,100,180,230,280,360,460,560])
(out/'native-vs-v27-wrist-audit.json').write_text(json.dumps({'flare':a,'own_v27':b,'scope':'Actual source matrices; rest-relative total hand-frame rotation includes axial roll, NOT anatomical flexion or a universal safe limit. Different rig/camera/weapon families, no hidden painted wrist recovery.'},indent=2)+'\n')
for name,d in [('flare',a),('ownv27',b)]:
 print(name,[(x['time_or_native_frame'],round(x['hand_relative_forearm_rotation_from_rest_degrees'],1),round(x['trunk_angle_to_world_vertical_degrees'],1),x.get('actual_blade_axis_hand_local')) for x in d['rows']]);print(d['bone_names'])
