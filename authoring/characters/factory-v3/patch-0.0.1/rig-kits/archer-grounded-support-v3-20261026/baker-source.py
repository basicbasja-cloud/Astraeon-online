"""Build a reusable sampled action library from verified native controls.

Uniform sample-index playback is for authoring review. Production clip timings,
root travel application and final motion/art acceptance are separate gates.
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
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['rig','controls-library','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--export-glb',action='store_true')
    parser.add_argument('--repository-root',type=Path,default=Path(__file__).resolve().parents[2])
    a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh sampled rig library')
    progress_path=a.controls_library/'progress.json';progress=json.loads(progress_path.read_text())
    if progress['status']!='NATIVE_RIG_CONTROL_COVERAGE_NOT_ART_APPROVAL' or progress['failed_jobs']:
        raise ValueError('Finish all actual source/control replays first')
    bpy.ops.wm.open_mainfile(filepath=str(a.rig.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01']
    if len(bpy.data.actions):raise ValueError('Start from the action-free shared authoring rig')
    scene.render.fps=25;scene.render.fps_base=2
    ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
    rows=[];inputs={str(a.rig):sha(a.rig),str(progress_path):sha(progress_path)}
    repository=a.repository_root.resolve()
    job_info=json.loads((repository/'authoring/characters/factory-v3/patch-0.0.1/ledger.json').read_text())
    canonical_rig_sha=scene.get('rig_sha256')
    a.output.mkdir(parents=True)
    for job in progress['jobs']:
        # Paths in the replay receipt are relative to the repository root.
        root=repository
        path=root/job['controls'];data=json.loads(path.read_text())
        if data['rig_sha256']!=canonical_rig_sha or sha(path)!=job['controls_sha256']:
            raise ValueError('Library controls do not belong to this canonical rig')
        inputs[str(path)]=sha(path)
        frames=data['views']['NE']['frames']
        if [f['index']for f in frames]!=list(range(len(frames))):raise ValueError('Native frame index gap')
        label=job['uses'][0].replace('/','_')
        action=bpy.data.actions.new('CF_'+label+'__'+job['job'])
        action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
        action['source_job']=job['job'];action['motion_provider']=job['motion_provider']
        action['timing_status']='UNIFORM_SAMPLE_INDEX_REVIEW_NOT_PRODUCTION_TIMING'
        action['loop_requested']=job_info['guide_jobs'][job['job']]['loop']
        action.use_frame_range=True;action.frame_start=1;action.frame_end=len(frames)
        previous={}
        for row in frames:
            scene.frame_set(row['index']+1)
            for bone in ordered:
                bone.rotation_mode='QUATERNION';bone.matrix_basis=Matrix.Identity(4)
            bpy.context.view_layer.update();inverse=rig.matrix_world.inverted()
            for bone in ordered:
                if bone.name in row['world_matrices']:
                    bone.matrix=inverse@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
            for bone in ordered:
                if bone.name not in row['world_matrices']:continue
                location,rotation,scale=bone.matrix_basis.decompose()
                if bone.name in previous and previous[bone.name].dot(rotation)<0:rotation.negate()
                previous[bone.name]=rotation.copy()
                bone.location=location;bone.rotation_quaternion=rotation;bone.scale=scale
                for prop in ['location','rotation_quaternion','scale']:
                    bone.keyframe_insert(data_path=prop,frame=row['index']+1,group=bone.name)
        bag=action_get_channelbag_for_slot(action,rig.animation_data.action_slot)
        for curve in bag.fcurves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
        errors=[]
        for row in frames:
            scene.frame_set(row['index']+1);bpy.context.view_layer.update()
            errors.append(max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target[r][c])
                              for name,target in row['world_matrices'].items() for r in range(4)for c in range(4)))
        if max(errors)>2e-5:raise ValueError('Baked action differs from canonical controls: '+job['job'])
        rows.append({'job':job['job'],'action_name':action.name,'uses':job['uses'],
                     'motion_provider':job['motion_provider'],'frames':len(frames),
                     'bones_per_pose':len(frames[0]['world_matrices']),
                     'maximum_matrix_error':max(errors),'controls_sha256':sha(path),
                     'source_samples':[{'action':f['source_action'],'source_frame':f['source_frame']}
                                       for f in frames],
                     'loop_requested':bool(action['loop_requested']),
                     'timing_status':'UNIFORM_SAMPLE_INDEX_REVIEW_NOT_PRODUCTION_TIMING',
                     'root_travel_applied_to_gameplay':False})
        print('ACTION_BAKED '+json.dumps({'count':len(rows),'job':job['job'],'frames':len(frames),'error':max(errors)}),flush=True)
    selected=next((r for r in rows if 'Mage/Walk'in r['uses']),rows[0])
    rig.animation_data.action=bpy.data.actions[selected['action_name']]
    rig.animation_data.action_slot=rig.animation_data.action.slots[0]
    scene.frame_start=1;scene.frame_end=selected['frames'];scene.frame_set(1)
    scene['library_status']='SAMPLED_NATIVE_ACTION_LIBRARY_REQUIRES_TIMING_AND_VISUAL_REVIEW'
    scene['production_timing_authored']=False
    bpy.context.preferences.filepaths.save_version=0
    blend=a.output/'sampled-native-actions.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()),compress=True)
    # Real reload and all action samples checked again.
    bpy.ops.wm.open_mainfile(filepath=str(blend.resolve()));rig=bpy.data.objects['ARM_FantasyCharacter01'];scene=bpy.context.scene
    for record in rows:
        action=bpy.data.actions[record['action_name']];rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
        controls=json.loads((repository/next(j['controls']for j in progress['jobs']if j['job']==record['job'])).read_text())
        errors=[]
        for row in controls['views']['NE']['frames']:
            scene.frame_set(row['index']+1);bpy.context.view_layer.update()
            errors.append(max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-target[r][c])
                              for name,target in row['world_matrices'].items() for r in range(4)for c in range(4)))
        record['maximum_reopened_matrix_error']=max(errors)
        if max(errors)>2e-5:raise ValueError('Saved action differs after reopen: '+record['job'])
    outputs={blend.name:sha(blend)}
    if a.export_glb:
        bpy.ops.object.select_all(action='SELECT')
        glb=a.output/'sampled-native-actions.glb'
        bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format='GLB',use_selection=True,
                                  export_animations=True,export_animation_mode='ACTIONS',
                                  export_cameras=True,export_extras=True,
                                  export_def_bones=False,export_all_influences=True,export_optimize_animation_size=False)
        outputs[glb.name]=sha(glb)
    if any(sha(name)!=digest for name,digest in inputs.items()):raise ValueError('Source library changed during bake')
    result={'status':'REUSABLE_SAMPLED_ACTIONS_NOT_FINAL_GAMEPLAY_ANIMATION',
            'actions':rows,'action_count':len(rows),'source_sha256':inputs,
            'maximum_reopened_matrix_error':max(r['maximum_reopened_matrix_error']for r in rows),
            'implementation_sha256':sha(__file__),'outputs':outputs,
            'export_optimize_animation_size':False,'native_pose_matrices_preserved':True,'endpoint_clones_added':False,
            'timing_authored':False,'gameplay_root_motion_authored':False,
            'final_art_or_character_approval':False,'new_complete_characters':0}
    (a.output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (a.output/'baker-source.py').write_bytes(Path(__file__).read_bytes())
    print('RIG_ACTION_LIBRARY_PASS '+json.dumps({'actions':len(rows),'maximum_reopened_matrix_error':result['maximum_reopened_matrix_error']}))


if __name__=='__main__':main()
