"""Isolated staff-grip guide adaptation; canonical renderer/source stay unchanged."""
import ast,hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from staff_grip_alignment import alignment_angles


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def instrument(source):
    tree=ast.parse(source);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');found=0
    for node in main.body:
        if not isinstance(node,ast.If):continue
        if ast.unparse(node.test)!="job.get('staff_arm_reference')":continue
        places=[i for i,n in enumerate(node.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='staff_pose' for t in n.targets)]
        if len(places)!=1:raise ValueError('Reference pose capture boundary changed')
        node.body.insert(places[0],ast.parse('_align_reference_staff_grip(rig, job)').body[0]);found+=1
    if found!=1:raise ValueError('Expected one staff reference capture')
    tree.body=[n for n in tree.body if not(isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=='__name__')]
    return ast.fix_missing_locations(tree)


def main():
    import bpy
    from mathutils import Matrix,Vector,Quaternion
    from bpy.app.handlers import persistent
    args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());output=Path(args[args.index('--output')+1]);canonical=Path(__file__).with_name('render_patch001_guides.py');proof=[];frames=[];implementation=sha(__file__);adapter_source=Path(__file__).read_bytes()
    if job.get('staff_grip_alignment_revision')!=1 or job.get('staff_grip_alignment_sha256')!=implementation or job.get('renderer_sha256')!=sha(canonical):raise ValueError('Explicit pinned staff grip study required')
    def apply(rig,job):
        from staff_grip_alignment import apply_reference_staff_grip
        proof.append(apply_reference_staff_grip(rig,job))
    scope={'__file__':str(canonical),'__name__':'staff_grip_study','_align_reference_staff_grip':apply};exec(compile(instrument(canonical.read_text()),str(canonical),'exec'),scope);scope['IMPLEMENTATION_DIGESTS'][Path(__file__).name]=sha(__file__)
    @persistent
    def validate_frame(scene):
        rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones));bones=rig.pose.bones
        ix=rig.matrix_world@bones['index_01_r'].head;pk=rig.matrix_world@bones['pinky_01_r'].head;grip=(ix+pk)*.5
        shaft=bpy.data.objects['WeaponGuide'];points=shaft.data.splines[0].points;a=shaft.matrix_world@Vector(points[0].co[:3]);b=shaft.matrix_world@Vector(points[-1].co[:3]);axis=(b-a).normalized();error=math.degrees(axis.angle((ix-pk).normalized()));distance=(grip-a-axis*(grip-a).dot(axis)).length
        if error>.05 or distance>1e-5:raise ValueError('Rendered staff does not follow actual knuckle grip')
        frames.append({'image':str(Path(scene.render.filepath).relative_to(output)),'axis_error_degrees':error,'grip_axis_distance_m':distance})
    import render_colored_hand_guide
    math_helper=Path(__file__).with_name('staff_grip_alignment.py');math_digest=sha(math_helper)
    if job.get('staff_grip_alignment_math_sha256') not in [None,math_digest]:raise ValueError('Grip math differs from planned implementation')
    bpy.app.handlers.render_pre.append(validate_frame)
    try:
        if job.get('hand_color_guide_revision'):render_colored_hand_guide.main(renderer_main=scope['main'])
        else:
            from render_frozen_patch001_guides import run_capture
            run_capture(renderer_main=scope['main'])
    finally:
        if validate_frame in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(validate_frame)
    (output/'adapter-source.py').write_bytes(adapter_source)
    (output/'alignment-math-source.py').write_bytes(Path(__file__).with_name('staff_grip_alignment.py').read_bytes())
    if sha(__file__)!=implementation or sha(math_helper)!=math_digest:raise ValueError('Grip implementation changed during capture')
    capture_proof={'status':'AUTHORED_STAFF_REFERENCE_GRIP_STUDY_NOT_UNCHANGED_MOCAP','reference_adaptations':proof,'rendered_grip_checks':frames,'canonical_renderer_sha256':sha(canonical),'adapter_sha256':implementation,'alignment_math_sha256':math_digest,'source_glb_modified':False,'runtime_admitted':False}
    (output/'staff-grip-study-proof.json').write_text(json.dumps(capture_proof,indent=2)+'\n')
    path=output/'manifest.json';manifest=json.loads(path.read_text());manifest['staff_grip_adaptation']=capture_proof;path.write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
