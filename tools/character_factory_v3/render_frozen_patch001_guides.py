"""Render adapted source poses without animation overwriting them in render COW.

Blender's render dependency graph can reevaluate an active action after a manual
pose adaptation. Freeze the evaluated local bases for rendering, retaining the
original source action/sample in the canonical metadata. The next sample is
evaluated normally by the unchanged canonical renderer.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_job(job):
    if type(job.get('render_pose_freeze_revision'))is not int or job['render_pose_freeze_revision']!=1:raise ValueError('Missing explicit frozen-render revision')
    if job.get('render_pose_freeze_sha256')!=sha(__file__):raise ValueError('Frozen-render implementation changed after planning')


def compact_capture(path):
    import numpy as np
    from PIL import Image
    original=path.read_bytes();pixels=np.array(Image.open(io.BytesIO(original)).convert('RGBA'))
    alpha=pixels[:,:,3].copy();visible=pixels[alpha>0,:3].copy()
    pixels[alpha==0]=0
    stream=io.BytesIO();Image.fromarray(pixels).save(stream,format='PNG',optimize=True,compress_level=9)
    data=stream.getvalue();restored=np.array(Image.open(io.BytesIO(data)))
    if not np.array_equal(restored[:,:,3],alpha)or not np.array_equal(restored[alpha>0,:3],visible):raise ValueError('Guide packaging changed visible pixels')
    temp=path.with_suffix('.compact.tmp');temp.write_bytes(data);temp.replace(path)
    return {'image':str(path),'original_sha256':hashlib.sha256(original).hexdigest(),
            'normalized_sha256':hashlib.sha256(data).hexdigest(),
            'bytes_before':len(original),'bytes_after':len(data),'visible_rgb_or_alpha_changed':False}


def install(job,output):
    import bpy
    from bpy.app.handlers import persistent
    validate_job(job);state={'frames':[],'pngs':[]}

    @persistent
    def freeze(scene):
        actors=[]
        for actor in [o for o in bpy.data.objects if o.type=='ARMATURE']:
            if not actor.animation_data:continue
            name=actor.animation_data.action.name if actor.animation_data.action else None
            basis={b.name:b.matrix_basis.copy()for b in actor.pose.bones}
            world={b.name:actor.matrix_world@b.matrix for b in actor.pose.bones}
            actor.animation_data.action=None
            for bone in actor.pose.bones:bone.matrix_basis=basis[bone.name]
            actor.update_tag(refresh={'OBJECT','DATA','TIME'})
            bpy.context.view_layer.update()
            error=max((max(abs((actor.matrix_world@b.matrix)[r][c]-world[b.name][r][c])for r in range(4)for c in range(4))for b in actor.pose.bones),default=0.)
            if error>1e-5:raise ValueError('Pose changed while freezing render animation')
            actors.append({'actor':actor.name,'source_action':name,'bones':len(basis),'max_world_matrix_component_error':error})
        state['frames'].append({'image':str(Path(scene.render.filepath).resolve().relative_to(output.resolve())),'actors':actors})

    @persistent
    def written(scene):
        path=Path(scene.render.filepath)
        if path.is_file()and path.suffix.lower()=='.png':
            record=compact_capture(path);record['image']=str(path.resolve().relative_to(output.resolve()));state['pngs'].append(record)

    bpy.app.handlers.render_pre.append(freeze);bpy.app.handlers.render_write.append(written)
    return state,freeze,written


def run_capture(renderer_main=None):
    import bpy
    import render_patch001_guides
    argv=sys.argv[sys.argv.index('--')+1:]
    job=json.loads(Path(argv[argv.index('--job')+1]).read_text())
    output=Path(argv[argv.index('--output')+1]);implementation=sha(__file__);state,freeze,written=install(job,output)
    try:
        (renderer_main or render_patch001_guides.main)()
    finally:
        if freeze in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(freeze)
        if written in bpy.app.handlers.render_write:bpy.app.handlers.render_write.remove(written)
    path=output/'manifest.json';receipt=json.loads(path.read_text())
    expected=receipt['frame_count']*len(receipt['views'])
    if sha(__file__)!=implementation:raise ValueError('Frozen renderer changed while capture was running')
    if len(state['frames'])!=expected or len(state['pngs'])!=expected:raise ValueError('Incomplete frozen-render or visible-pixel packaging evidence')
    receipt['implementation_digests_at_process_start'][Path(__file__).name]=sha(__file__)
    receipt['render_pose_freeze']={'revision':1,'implementation_sha256':sha(__file__),
                                  'rendered_frames':state['frames'],
                                  'source_action_samples_changed':False,
                                  'policy':'Disable animation reevaluation after computing adapted local bone bases; no anatomical/pose interpolation.'}
    receipt['png_normalization']={'policy':'Clear only alpha-zero RGB and losslessly compress; preserve all visible RGB and every alpha value.','frames':state['pngs']}
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print('FROZEN_RENDER_CAPTURE '+json.dumps({'frames':expected,'bytes_before':sum(r['bytes_before']for r in state['pngs']),'bytes_after':sum(r['bytes_after']for r in state['pngs'])}),flush=True)


if __name__=='__main__':run_capture()
