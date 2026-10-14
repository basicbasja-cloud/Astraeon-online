"""Actual saved Blender bone-frame evaluation, old track-frame vs common hinge."""
import bpy,math,json,hashlib
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent;rows=[]
for label,path in [('initial_track_frame',P/'skinned-arm-proof/continuous-arm-skin.blend'),('common_elbow_plane',P/'hinge-skin-proof/hinge-arm-skin.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));rig=bpy.data.objects['ContinuousArmSkin'];frames=[]
 for i in range(8):
  tick=1+39*i/7;bpy.context.scene.frame_set(math.floor(tick),subframe=tick-math.floor(tick));bpy.context.view_layer.update();arms={}
  for side in ['left','right']:
   u=rig.pose.bones[side+'.upperarm'].matrix.to_3x3().normalized();f=rig.pose.bones[side+'.forearm'].matrix.to_3x3().normalized();h=rig.pose.bones[side+'.hand'].matrix.to_3x3().normalized();z=(u.inverted()@f)@Vector((0,0,1));arms[side]=dict(relative_elbow_axis_deviation_degrees=math.degrees(math.atan2(math.hypot(z.x,z.y),z.z)),relative_elbow_axis_vector_error=(z-Vector((0,0,1))).length,hand_forearm_frame_error=sum((f.col[j]-h.col[j]).length for j in range(3)))
  frames.append(dict(index=i,arms=arms))
 rows.append(dict(label=label,blend_path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=frames))
(P/'actual-bone-frame-comparison.json').write_text(json.dumps(dict(cases=rows,scope='Actual pose-bone relative frames in the declared zero-pronation pickup. Common hinge axis is a source-authoring constraint, not universal anatomical correctness.'),indent=2)+'\n');print([(r['label'],max(a['relative_elbow_axis_deviation_degrees'] for f in r['frames'] for a in f['arms'].values())) for r in rows])
