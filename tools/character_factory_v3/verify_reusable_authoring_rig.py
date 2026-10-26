"""Reopen Blender/GLB rig outputs and exercise live bone sockets and skinning."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    import bpy
    from mathutils import Matrix,Euler
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Preserve previous checks')
    package=args.package
    manifest=json.loads((package/'manifest.json').read_text())
    for name,record in manifest['outputs'].items():
        if hashlib.sha256((package/name).read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('Rig output changed after packaging')
    expected={r['name'] for r in manifest['bones']}
    results=[]
    for kind in ['blend','glb']:
        if kind=='blend':
            bpy.ops.wm.open_mainfile(filepath=str((package/'shared-authoring-rig.blend').resolve()))
        else:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str((package/'shared-authoring-rig.glb').resolve()))
        rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
        if len(rigs)!=1 or set(rigs[0].data.bones.keys())!=expected:
            raise ValueError('Reopened skeleton does not preserve all 60 named bones')
        rig=rigs[0]
        cameras=[o for o in bpy.data.objects if o.type=='CAMERA']
        if len(cameras)!=8:raise ValueError('Native cameras lost in round trip')
        for direction,record in manifest['cameras'].items():
            camera=bpy.data.objects['CAM_'+direction]
            if camera.data.type!='ORTHO' or abs(camera.data.ortho_scale-record['ortho_scale'])>1e-5:
                raise ValueError('Camera framing changed')
            if (camera.matrix_world.translation-Matrix.Translation(record['location']).translation).length>1e-5:
                raise ValueError('Camera position changed')
            target_rotation=Euler(record['rotation'],'XYZ').to_quaternion()
            difference=camera.matrix_world.to_quaternion().rotation_difference(target_rotation).angle
            if min(difference,abs(6.283185307179586-difference))>1e-5:
                raise ValueError('Camera orientation changed')
        sockets={name:bpy.data.objects[row['object']] for name,row in manifest['sockets'].items()}
        max_socket_error=0
        for phase in [0,.25,-.25]:
            for name in ['Head','Hand.R','Hand.L','Chest','Foot.R','Foot.L']:
                bone=rig.pose.bones[name];bone.rotation_mode='XYZ';bone.rotation_euler.z=phase
            bpy.context.view_layer.update()
            graph=bpy.context.evaluated_depsgraph_get()
            for name,socket in sockets.items():
                desired=rig.matrix_world@rig.pose.bones[manifest['sockets'][name]['bone']].matrix
                actual=socket.evaluated_get(graph).matrix_world
                error=max(abs(actual[r][c]-desired[r][c]) for r in range(4) for c in range(4))
                max_socket_error=max(error,max_socket_error)
                if error>2e-5:raise ValueError('Socket not live at pose '+str(phase)+': '+name)
        meshes=[]
        bone_shapes={b.custom_shape for b in rig.pose.bones if b.custom_shape}
        actual_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in bone_shapes]
        if {o.name for o in actual_meshes}!={r['name'] for r in manifest['meshes']}:
            raise ValueError('Roundtrip character meshes differ')
        for obj in actual_meshes:
            if obj.data.validate():raise ValueError('Roundtrip mesh is invalid')
            modifiers=[m for m in obj.modifiers if m.type=='ARMATURE' and m.object==rig]
            rigid_parent = obj.parent == rig and obj.parent_type == 'BONE' and obj.parent_bone in expected
            if not modifiers and not rigid_parent:raise ValueError('Mesh lost skin binding: '+obj.name+' '+str([(m.type,getattr(m,'object',None))for m in obj.modifiers]))
            unweighted=0;max_weight_error=0
            bone_groups={g.index for g in obj.vertex_groups if g.name in expected}
            for vertex in obj.data.vertices:
                total=1.0 if rigid_parent and not modifiers else sum(g.weight for g in vertex.groups if g.group in bone_groups)
                if total<.0001:unweighted+=1
                max_weight_error=max(max_weight_error,abs(1-total))
            if unweighted:raise ValueError('Unweighted vertices in rig export')
            meshes.append({'name':obj.name,'vertices':len(obj.data.vertices),
                           'binding':'rigid_bone_parent' if rigid_parent and not modifiers else 'skinned_armature','unweighted_vertices':unweighted,'max_weight_sum_error':max_weight_error})
        unpacked=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file]
        if unpacked or bpy.data.libraries:raise ValueError('Rig output has external file dependencies: '+str(unpacked))
        results.append({'external_image_files':0,'linked_libraries':0,'format':kind,'bones':len(expected),'cameras':len(cameras),
                        'sockets':len(sockets),'socket_pose_cases':3,
                        'maximum_live_socket_matrix_error':max_socket_error,'meshes':meshes})
    args.output.write_text(json.dumps({'status':'ROUNDTRIP_SKELETON_SKIN_AND_SOCKETS_PASS',
                                      'checks':results,'final_art_approval':False,
                                      'complete_character_claim':False},indent=2)+'\n')
    print('RIG_ROUNDTRIP_PASS '+json.dumps(results))


if __name__=='__main__':main()
