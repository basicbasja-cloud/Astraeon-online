"""Pin a native Hit render to its declared object/bone snapshot, without muting curves.

Opt-in source diagnostic. The unchanged canonical renderer supplies poses and
camera. No source action keys, source samples, root policy or artwork are edited.
"""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument(source):
    tree=ast.parse(source);count=0
    class Guard(ast.NodeTransformer):
        def visit_Call(self,node):
            nonlocal count
            node=self.generic_visit(node)
            if isinstance(node.func,ast.Attribute)and ast.unparse(node.func)=='bpy.ops.render.render':
                count+=1
                return ast.copy_location(ast.Call(func=ast.Name(id='_snapshot_render',ctx=ast.Load()),
                    args=[ast.Name(id='rig',ctx=ast.Load()),ast.Name(id='i',ctx=ast.Load()),
                          ast.Name(id='rec',ctx=ast.Load()),node.func,*node.args],keywords=node.keywords),node)
            return node
    tree=Guard().visit(tree)
    if count!=1:raise ValueError('Expected one canonical render boundary')
    tree.body=[node for node in tree.body if not(isinstance(node,ast.If)and
        isinstance(node.test,ast.Compare)and isinstance(node.test.left,ast.Name)and node.test.left.id=='__name__')]
    return ast.fix_missing_locations(tree)


def validate_job(job):
    unsupported=('retarget_to','entry_transition','exit_transition','staff_arm_reference',
                 'staff_grip_alignment_revision','floor_sit_adapter','hero_fit_study','explicit_source_samples')
    if job.get('source_actions')!=['Hit_Chest']or any(job.get(k)for k in unsupported):
        raise ValueError('Requires one unadapted native Hit_Chest action')
    if type(job.get('render_snapshot_revision'))is not int or job['render_snapshot_revision']!=1:
        raise ValueError('Explicit snapshot revision required')
    if job.get('render_snapshot_sha256')!=sha(__file__):raise ValueError('Snapshot implementation changed')
    if job.get('renderer_sha256')!=sha(HERE/'render_patch001_guides.py'):raise ValueError('Canonical renderer changed')
    if job.get('render_snapshot_png_sha256')!=sha(HERE/'seal_source_guide_replay.py'):raise ValueError('Snapshot PNG implementation changed')


def planned_geometry(geometry,profile):
    if profile!='native-hit-declared-pose-v1':raise ValueError('Unknown native render snapshot profile')
    result={**geometry,'render_snapshot_revision':1,'render_snapshot_sha256':sha(__file__),
            'render_snapshot_png_sha256':sha(HERE/'seal_source_guide_replay.py')}
    validate_job(result)
    return result


def matrix_error(expected,actual):
    values=[abs(actual[r][c]-expected[r][c])for r in range(4)for c in range(4)]
    if any(not math.isfinite(v)for v in values):raise ValueError('Nonfinite render matrix')
    return max(values)


def action_fingerprint(actions):
    """Record key/handle values, mute and interpolation, not the current action slot."""
    records=[]
    for action in sorted(actions,key=lambda a:a.name):
        curves=[]
        for curve in action.fcurves:
            curves.append({'path':curve.data_path,'index':curve.array_index,'muted':curve.mute,
                'keys':[{'co':list(p.co),'left':list(p.handle_left),'right':list(p.handle_right),
                         'interpolation':p.interpolation}for p in curve.keyframe_points]})
        records.append({'name':action.name,'curves':curves})
    return hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from seal_source_guide_replay import normalize_png
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--observe-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    job=json.loads(args.job.read_text());validate_job(job)
    if args.output.exists()or args.output.is_symlink():raise ValueError('Choose fresh capture output')
    rows=[];initial_actions=[];initial_fingerprint=[]
    implementation=sha(__file__)
    png_implementation=sha(HERE/'seal_source_guide_replay.py')
    def capture(rig,index,record,render,*positional,**keywords):
        if rig.parent is not None or rig.animation_data is None:raise ValueError('Expected unparented native armature')
        if not initial_actions:
            initial_actions.extend(bpy.data.actions);initial_fingerprint.append(action_fingerprint(initial_actions))
        before_world=rig.matrix_world.copy()
        basis={b.name:b.matrix_basis.copy()for b in rig.pose.bones}
        before_bones={b.name:(before_world@b.matrix).copy()for b in rig.pose.bones}
        source_action=rig.animation_data.action.name if rig.animation_data.action else None
        if not args.observe_only:
            rig.animation_data.action=None
            rig.matrix_world=before_world
            for bone in rig.pose.bones:bone.matrix_basis=basis[bone.name]
            rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
        locked_error=max(matrix_error(before_bones[b.name],rig.matrix_world@b.matrix)for b in rig.pose.bones)
        if not args.observe_only and locked_error>1e-5:raise ValueError('Snapshot changed declared pose before render')
        render(*positional,**keywords)
        scene=bpy.context.scene;graph=bpy.context.evaluated_depsgraph_get();evaluated=rig.evaluated_get(graph)
        actual_world=evaluated.matrix_world
        after_error=max(matrix_error(before_bones[b.name],actual_world@evaluated.pose.bones[b.name].matrix)for b in rig.pose.bones)
        if not args.observe_only and after_error>1e-5:raise ValueError('Render dependency graph changed snapshot pose')
        def projected(point):
            p=world_to_camera_view(scene,scene.camera,point)
            return [float(p.x*job['resolution']),float((1-p.y)*job['resolution'])]
        joints={}
        for name in ('head','pelvis','hand_r','hand_l','foot_r','foot_l'):
            expected=projected(before_bones[name].translation)
            actual=projected((actual_world@evaluated.pose.bones[name].matrix).translation)
            joints[name]={'declared_source_px':expected,'evaluated_after_render_px':actual,
                          'distance_runtime_px':math.dist(expected,actual)*240/job['resolution']}
        path=Path(scene.render.filepath);encoded,pixel_hash,canvas=normalize_png(path)
        path.write_bytes(encoded)
        rows.append({'image':str(path.resolve().relative_to(args.output.resolve())),
            'index':index,'source_action':record['action'],'source_frame':record['source_frame'],
            'active_source_action_before':source_action,'bones':len(before_bones),
            'declared_object_world_matrix':[list(r)for r in before_world],
            'evaluated_object_world_matrix_after_render':[list(r)for r in actual_world],
            'max_before_render_matrix_component_error':locked_error,
            'max_after_render_matrix_component_error':after_error,'joints':joints,
            'png_sha256':hashlib.sha256(encoded).hexdigest(),'rgba_sha256':pixel_hash,'canvas':canvas})
    canonical=HERE/'render_patch001_guides.py'
    scope={'__name__':'hit_snapshot_capture','__file__':str(canonical),'_snapshot_render':capture}
    exec(compile(instrument(canonical.read_text()),str(canonical),'exec'),scope)
    # The canonical parser must see only its supported arguments.
    original_argv=sys.argv[:]
    if '--observe-only'in sys.argv:sys.argv.remove('--observe-only')
    try:scope['main']()
    finally:sys.argv[:]=original_argv
    if not initial_actions or action_fingerprint(initial_actions)!=initial_fingerprint[0]:raise ValueError('Source fcurve data or mute flags changed')
    if sha(__file__)!=implementation:raise ValueError('Snapshot implementation changed during capture')
    if sha(HERE/'seal_source_guide_replay.py')!=png_implementation:raise ValueError('Snapshot PNG implementation changed during capture')
    if sha(Path(job['source_file']).resolve())!=job['source_sha256']:raise ValueError('Source GLB changed during capture')
    expected=job['frames']*len(job['directions'])
    if len(rows)!=expected:raise ValueError('Incomplete render snapshot evidence')
    path=args.output/'manifest.json';manifest=json.loads(path.read_text())
    manifest['implementation_digests_at_process_start'][Path(__file__).name]=implementation
    manifest['implementation_digests_at_process_start']['seal_source_guide_replay.py']=png_implementation
    manifest['render_snapshot']={'revision':1,'applied':not args.observe_only,'implementation_sha256':implementation,
        'source_fcurves_sha256_before_and_after':initial_fingerprint[0],
        'blender_version':bpy.app.version_string,'python_version':sys.version.split()[0],
        'source_fcurves_or_mute_flags_changed':False,'source_samples_or_camera_changed':False,
        'frames':rows,'status':'OBSERVATION_ONLY_NOT_APPROVED'if args.observe_only else'SNAPSHOT_MATCHES_DECLARED_RENDER_POSES_NOT_ART_APPROVAL'}
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('HIT_RENDER_SNAPSHOT '+json.dumps({'applied':not args.observe_only,'frames':len(rows),
        'max_world_matrix_error':max(r['max_after_render_matrix_component_error']for r in rows),
        'max_joint_render_displacement_runtime_px':max(j['distance_runtime_px']for r in rows for j in r['joints'].values())}),flush=True)


if __name__=='__main__':main()
