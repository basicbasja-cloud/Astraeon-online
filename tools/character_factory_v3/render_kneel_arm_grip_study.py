"""Isolated native-rig study: resample kneel and rotate only sword upper arm.

The source action, production renderer and bindings are never modified. This is
not a motion, grip, contact, art, or runtime approval.
"""
import hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render_kneel_pickup_sampling_study import validate_samples
CANONICAL=HERE/'render_patch001_guides.py'
SAMPLE='f=start+(end-start)*local'
POSE="        for name,matrix in staff_pose.items():rig.pose.bones[name].matrix_basis=matrix\n"
INTERVALS="    intervals=job.get('source_ranges',{})\n"

def validate(job):
 validate_samples(job)
 axis=job.get('study_arm_axis');angle=job.get('study_arm_degrees')
 if axis not in ('X','Y','Z') or type(angle) not in (int,float) or not math.isfinite(angle) or abs(angle)>50:raise ValueError('Expected a finite bounded single-axis arm adjustment')
 if type(job.get('study_closed_fingers',False)) is not bool:raise ValueError('Expected an explicit boolean for the grip study')
 samples=job['study_source_frames']
 if samples[0]!=0 or samples[-1]!=156:raise ValueError('Study envelope assumes the preserved original endpoints')

def main():
 import bpy
 from bpy.app.handlers import persistent
 args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());validate(job)
 source=CANONICAL.read_text()
 if hashlib.sha256(CANONICAL.read_bytes()).hexdigest()!=job['renderer_sha256'] or source.count(SAMPLE)!=1 or source.count(POSE)!=1 or source.count(INTERVALS)!=1:raise ValueError('Pinned canonical renderer changed')
 source=source.replace(SAMPLE,"f=job['study_source_frames'][i]\n        if not start<=f<=end:raise ValueError('Study frame outside action range')")
 grip_reference="""    finger_reference={}
    if job.get('study_closed_fingers',False):
        action('Idle_Sword');sc.frame_set(0);bpy.context.view_layer.update()
        prefixes=('index_','middle_','ring_','pinky_','thumb_')
        finger_reference={b.name:b.matrix_basis.copy() for b in rig.pose.bones if b.name.endswith('_r') and b.name.startswith(prefixes) and 'leaf' not in b.name}
        if len(finger_reference)!=15:raise ValueError('Unexpected native sword hand')
"""
 source=source.replace(INTERVALS,grip_reference+INTERVALS)
 addition="""        t=sc.frame_current_final
        weight=max(0.,min(1.,t/30.,(156.-t)/26.))
        arm=rig.pose.bones['upperarm_r']
        arm.matrix_basis=arm.matrix_basis @ Matrix.Rotation(math.radians(job['study_arm_degrees'])*weight,4,job['study_arm_axis'])
        for name,matrix in finger_reference.items():rig.pose.bones[name].matrix_basis=matrix.copy()
        bpy.context.view_layer.update()
"""
 source=source.replace(POSE,POSE+addition)
 @persistent
 def freeze(scene):
  for actor in [o for o in bpy.data.objects if o.type=='ARMATURE' and o.animation_data and o.animation_data.action]:
   basis={b.name:b.matrix_basis.copy() for b in actor.pose.bones}
   world={b.name:(actor.matrix_world@b.matrix).copy() for b in actor.pose.bones}
   actor.animation_data.action=None
   for bone in actor.pose.bones:bone.matrix_basis=basis[bone.name]
   bpy.context.view_layer.update()
   error=max((max(abs((actor.matrix_world@b.matrix)[r][c]-world[b.name][r][c]) for r in range(4) for c in range(4)) for b in actor.pose.bones),default=0.)
   if error>1e-5:raise ValueError('Frozen study pose changed')
 bpy.app.handlers.render_pre.append(freeze)
 try:exec(compile(source,str(CANONICAL),'exec'),{'__name__':'__main__','__file__':str(CANONICAL)})
 finally:
  if freeze in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(freeze)
if __name__=='__main__':main()
