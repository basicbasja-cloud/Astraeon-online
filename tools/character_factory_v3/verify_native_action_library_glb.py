"""Reimport the sampled action GLB and compare every native bone pose."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys


def main():
    import bpy
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library',type=Path,required=True)
    p.add_argument('--controls-library',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--glb-name',default='sampled-native-actions.glb')
    p.add_argument('--repository-root',type=Path,default=Path(__file__).resolve().parents[2])
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Preserve previous verification')
    manifest=json.loads((a.library/'manifest.json').read_text())
    source=json.loads((a.controls_library/'progress.json').read_text())
    if Path(a.glb_name).name!=a.glb_name:raise ValueError('Choose a GLB inside the library')
    glb=a.library/a.glb_name;binary=glb.read_bytes()
    expected=manifest['outputs'].get(glb.name)
    if expected is None:
        export=json.loads(glb.with_suffix('.export.json').read_text())
        if export['source_blend_sha256']!=manifest['outputs']['sampled-native-actions.blend']:
            raise ValueError('GLB source library differs')
        expected=export['output_sha256']
    if hashlib.sha256(binary).hexdigest()!=expected:raise ValueError('GLB changed')
    count,_=struct.unpack_from('<II',binary,12);gltf=json.loads(binary[20:20+count])
    if len(gltf.get('animations',[]))!=manifest['action_count']:raise ValueError('GLB action coverage differs')
    if any('uri'in image and not image['uri'].startswith('data:')for image in gltf.get('images',[])):
        raise ValueError('GLB depends on external texture')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb.resolve()))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    if len(rigs)!=1 or len(rigs[0].data.bones)!=60:raise ValueError('GLB skeleton differs')
    rig=rigs[0];scene=bpy.context.scene;results=[]
    root=a.repository_root.resolve()
    for row in manifest['actions']:
        candidates=[action for action in bpy.data.actions if action.name==row['action_name'] or action.name.startswith(row['action_name']+'_')]
        if len(candidates)!=1:raise ValueError('Missing/ambiguous imported action: '+row['action_name'])
        action=candidates[0];rig.animation_data_create();rig.animation_data.action=action
        rig.animation_data.action_slot=action.slots[0]
        entry=next(j for j in source['jobs']if j['job']==row['job'])
        controls=json.loads((root/entry['controls']).read_text())['views']['NE']['frames']
        first,last=action.frame_range
        worst=0.;position_error=0.;worst_bone=None
        for index,frame in enumerate(controls):
            time=first+(last-first)*index/(len(controls)-1)
            scene.frame_set(math.floor(time),subframe=time%1);bpy.context.view_layer.update()
            for name,expected in frame['world_matrices'].items():
                actual=rig.matrix_world@rig.pose.bones[name].matrix
                error=max(abs(actual[r][c]-expected[r][c])for r in range(4)for c in range(4))
                position_error=max(position_error,max(abs(actual[r][3]-expected[r][3])for r in range(3)))
                if error>worst:worst=error;worst_bone=name
        result={'job':row['job'],'action_name':action.name,'poses':len(controls),
                'maximum_world_matrix_error':worst,'maximum_world_position_error':position_error,
                'worst_bone':worst_bone,'pass':worst<3e-5}
        results.append(result)
        print('GLB_ACTION_CHECK '+json.dumps(result),flush=True)
    proof={'status':'GLB_ALL_NATIVE_SAMPLES_MATCH'if all(r['pass']for r in results)else'GLB_POSE_ROUNDTRIP_FAILED',
           'actions':results,'action_count':len(results),'poses':sum(r['poses']for r in results),
           'maximum_world_matrix_error':max(r['maximum_world_matrix_error']for r in results),
           'glb_sha256':hashlib.sha256(binary).hexdigest(),'production_timing_approved':False,
           'final_art_or_character_approval':False}
    a.output.write_text(json.dumps(proof,indent=2)+'\n')
    if not all(r['pass']for r in results):raise ValueError('GLB sampled motion does not match canonical controls')
    print('GLB_LIBRARY_ROUNDTRIP_PASS',len(results),flush=True)


if __name__=='__main__':main()
