"""Bake verified canonical world matrices into an editable rig action.

This is a native motion example, not new final illustration or a complete clip set.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix
    from bpy_extras.anim_utils import action_get_channelbag_for_slot
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rig','controls','output','proof']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--direction',default='NE')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists() or a.proof.exists():raise ValueError('Preserve prior motion examples')
    pins={str(f):sha(f) for f in [a.rig,a.controls]}
    data=json.loads(a.controls.read_text())
    frames=data['views'][a.direction]['frames']
    if [f['index']for f in frames]!=list(range(len(frames))):raise ValueError('Non-contiguous native samples')
    bpy.ops.wm.open_mainfile(filepath=str(a.rig.resolve()))
    rig=bpy.data.objects['ARM_FantasyCharacter01']
    if len(bpy.data.actions):raise ValueError('Expected clean shared rig package')
    scene=bpy.context.scene
    scene.camera=bpy.data.objects['CAM_'+a.direction]
    scene.render.fps=25
    scene.render.fps_base=2
    scene.frame_start=1
    scene.frame_end=len(frames)
    action=bpy.data.actions.new('Native_Walk_16')
    action.use_fake_user=True
    rig.animation_data_create()
    rig.animation_data.action=action
    ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
    previous={}
    direct_errors=[]
    for row in frames:
        scene.frame_set(row['index']+1)
        for bone in ordered:
            bone.rotation_mode='QUATERNION'
            bone.matrix_basis=Matrix.Identity(4)
        bpy.context.view_layer.update()
        inverse=rig.matrix_world.inverted()
        for bone in ordered:
            if bone.name in row['world_matrices']:
                bone.matrix=inverse@Matrix(row['world_matrices'][bone.name])
                bpy.context.view_layer.update()
        for bone in ordered:
            if bone.name not in row['world_matrices']:continue
            location,rotation,scale=bone.matrix_basis.decompose()
            if bone.name in previous and previous[bone.name].dot(rotation)<0:rotation.negate()
            previous[bone.name]=rotation.copy()
            bone.location=location;bone.rotation_quaternion=rotation;bone.scale=scale
            for prop in ['location','rotation_quaternion','scale']:
                bone.keyframe_insert(data_path=prop,frame=row['index']+1,group=bone.name)
        bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target[r][c])
                  for name,target in row['world_matrices'].items() for r in range(4) for c in range(4))
        direct_errors.append(error)
    bag=action_get_channelbag_for_slot(action,rig.animation_data.action_slot)
    for curve in bag.fcurves:
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    evaluated_errors=[]
    for row in frames:
        scene.frame_set(row['index']+1);bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target[r][c])
                  for name,target in row['world_matrices'].items() for r in range(4) for c in range(4))
        evaluated_errors.append(error)
    if max(direct_errors+evaluated_errors)>2e-5:
        raise ValueError('Baked action differs from native world controls')
    scene.frame_set(1)
    scene['native_motion_status']='VERIFIED_SAMPLED_WALK_NOT_COMPLETE_CHARACTER_CLIP_SET'
    scene['native_motion_controls_sha256']=pins[str(a.controls)]
    bpy.context.preferences.filepaths.save_version=0
    a.output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()),compress=True)
    # Reopen to validate persistence rather than trusting in-memory insertion.
    bpy.ops.wm.open_mainfile(filepath=str(a.output.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01']
    reopened=[]
    for row in frames:
        scene.frame_set(row['index']+1);bpy.context.view_layer.update()
        reopened.append(max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target[r][c])
                            for name,target in row['world_matrices'].items() for r in range(4) for c in range(4)))
    if max(reopened)>2e-5:raise ValueError('Saved native animation changed after reopen')
    if any(sha(f)!=h for f,h in pins.items()):raise ValueError('Source inputs changed')
    proof={'status':'EDITABLE_NATIVE_WALK_ACTION_WORLD_MATRICES_PASS',
           'source_sha256':pins,'implementation_sha256':sha(__file__),
           'frames':len(frames),'bones_per_frame':len(frames[0]['world_matrices']),
           'display_frame_duration_ms':80,'frame_range':[1,len(frames)],
           'maximum_direct_matrix_error':max(direct_errors),
           'maximum_evaluated_matrix_error':max(evaluated_errors),
           'maximum_reopened_matrix_error':max(reopened),
           'endpoint_cloned':False,'pose_fitting':False,
           'output_sha256':sha(a.output),'final_art':False,'all_actions_included':False}
    a.proof.write_text(json.dumps(proof,indent=2)+'\n')
    print('NATIVE_ACTION_PASS '+json.dumps(proof))


if __name__=='__main__':main()
