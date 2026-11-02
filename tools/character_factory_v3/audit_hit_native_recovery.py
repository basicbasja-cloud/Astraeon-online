"""Inspect dense native Hit recovery without editing or approving its source motion."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render_hit_snapshot_guides import action_fingerprint


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix,Vector,Euler
    from bpy_extras.object_utils import world_to_camera_view
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists()or args.output.is_symlink():raise ValueError('Choose fresh output')
    manifest=json.loads(args.manifest.read_text());job=manifest['job'];source=Path(job['source_file']).resolve()
    if job['source_actions']!=['Hit_Chest']or source.is_symlink()or sha(source)!=job['source_sha256']:raise ValueError('Unexpected native source')
    if manifest.get('render_snapshot',{}).get('applied')is not True:raise ValueError('Use a verified declared-snapshot manifest')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
    scene=bpy.context.scene;rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
    if rig.parent is not None:raise ValueError('Unexpected native parent')
    for track in rig.animation_data.nla_tracks:track.mute=True
    action=bpy.data.actions.get('Hit_Chest_'+rig.name)
    if action is None:raise ValueError('Missing native action')
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    rig.animation_data.action=action
    if hasattr(rig.animation_data,'action_slot')and action.slots:rig.animation_data.action_slot=action.slots[0]
    initial=action_fingerprint(list(bpy.data.actions));start,end=map(float,action.frame_range)
    curves=[]
    for curve in action.fcurves:
        curves.append({'path':curve.data_path,'component':curve.array_index,'muted':curve.mute,
                       'keys':[{'frame':float(k.co.x),'value':float(k.co.y),'interpolation':k.interpolation}for k in curve.keyframe_points]})
    camera_data=bpy.data.cameras.new('RecordedCamera');camera=bpy.data.objects.new('RecordedCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
    camera_data.type='ORTHO';scene.render.resolution_x=scene.render.resolution_y=job['resolution'];scene.render.resolution_percentage=100
    samples=sorted(set([start+(end-start)*i/88 for i in range(89)]+[float(i)for i in range(math.ceil(start),math.floor(end)+1)]))
    snapshots=[];rows=[]
    for frame in samples:
        scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
        # Exactly the native guide's declared world state, before any rendering.
        rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
        matrices={bone.name:rig.matrix_world@bone.matrix for bone in rig.pose.bones}
        snapshots.append({name:matrix.copy()for name,matrix in matrices.items()})
        world={name:list(matrix.translation)for name,matrix in matrices.items()}
        grip=(matrices['index_01_r'].translation+matrices['pinky_01_r'].translation)*.5
        axis=(matrices['index_01_r'].translation-matrices['pinky_01_r'].translation).normalized()
        worlds={name:Vector(world[name])for name in ('head','pelvis','hand_r','hand_l','foot_r','foot_l')}
        worlds.update({'sword_grip':grip,'sword_tip':grip+axis*.8})
        views={}
        for direction,record in manifest['views'].items():
            c=record['camera'];camera.location=c['location'];camera.rotation_euler=Euler(c['rotation']);camera_data.ortho_scale=c['ortho_scale'];bpy.context.view_layer.update()
            def project(point):
                p=world_to_camera_view(scene,camera,point)
                return [float(p.x*240),float((1-p.y)*240)]
            views[direction]={name:project(point)for name,point in worlds.items()}
        rows.append({'source_frame':frame,'world_bone_origins':world,'runtime_projected_points':views})
    reference_error=0.
    for direction,view in manifest['views'].items():
        for index,reference in enumerate(view['frames']):
            row=min(rows,key=lambda r:abs(r['source_frame']-reference['source_frame']))
            if abs(row['source_frame']-reference['source_frame'])>1e-6:raise ValueError('Source sample correspondence changed')
            for name,point in reference['world_landmarks'].items():
                if name=='root':continue
                reference_error=max(reference_error,math.dist(row['world_bone_origins'][name],point))
    if reference_error>1e-5:raise ValueError('Dense evaluation differs from recorded declared poses')
    endpoint=max(abs(snapshots[0][name][r][c]-snapshots[-1][name][r][c])for name in snapshots[0]for r in range(4)for c in range(4))
    fingerprint=action_fingerprint(list(bpy.data.actions))
    if fingerprint!=initial or sha(source)!=job['source_sha256']:raise ValueError('Source modified during audit')
    result={'status':'DENSE_SOURCE_RECOVERY_DIAGNOSTIC_NOT_MOTION_OR_ART_APPROVAL','source_sha256':job['source_sha256'],
        'manifest_sha256':sha(args.manifest),'implementation_sha256':sha(Path(__file__)),
        'fingerprint_helper_sha256':sha(HERE/'render_hit_snapshot_guides.py'),
        'blender_version':bpy.app.version_string,'action_range':[start,end],
        'source_action_fcurves_before_and_after_sha256':initial,'fcurves_or_mute_flags_changed':False,
        'bones':len(snapshots[0]),'samples':len(rows),'max_recorded_landmark_world_error_m':reference_error,
        'first_last_all_bone_world_matrix_component_error':endpoint,'curves':curves,'frames':rows,
        'limitations':['No new source animation, transition, artwork or runtime package is approved.',
                       'Bone origins are not verified anatomical sole contacts.',
                       'Dense evaluation follows native interpolation; additional samples cannot remove a velocity reversal.',
                       'Source frame units have not been certified as final gameplay time.']}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('DENSE_NATIVE_HIT '+json.dumps({k:result[k]for k in ('samples','bones','max_recorded_landmark_world_error_m','first_last_all_bone_world_matrix_component_error')}))

if __name__=='__main__':main()
