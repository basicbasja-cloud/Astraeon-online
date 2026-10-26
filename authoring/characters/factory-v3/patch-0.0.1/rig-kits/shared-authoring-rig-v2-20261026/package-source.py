"""Package the existing shared authoring skeleton; never claim six finished meshes.

Blender 5.2 CLI. Source art, source rig and native guide controls are read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['rig', 'spec', 'controls', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if bpy.app.version[:2] != (5, 2):
        raise ValueError('Use the pinned Blender 5.2 series')
    if args.output.exists():
        raise ValueError('Choose a fresh package; do not overwrite authoring work')
    pins = {str(p): sha(p) for p in [args.rig, args.spec, args.controls]}
    spec = json.loads(args.spec.read_text())
    controls = json.loads(args.controls.read_text())
    if sha(args.rig) != controls['rig_sha256']:
        raise ValueError('Native camera controls belong to another rig')
    if set(controls['available_cameras']) != {'S','SW','W','NW','N','NE','E','SE'}:
        raise ValueError('Eight actual cameras required')
    bpy.ops.wm.open_mainfile(filepath=str(args.rig.resolve()))
    if len(bpy.data.actions):
        raise ValueError('Source must be the clean action-free canonical rig')
    scene = bpy.context.scene
    rig = bpy.data.objects[spec['skeleton_object']]
    root = bpy.data.objects[spec['root_control_object']]
    if set(rig.data.bones.keys()) != set(spec['bones']):
        raise ValueError('Canonical skeleton differs from spec')
    root.scale = (controls['actor_scale'],)*3
    root.rotation_euler = (0,0,0)
    rig.animation_data_clear()
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
        for constraint in bone.constraints:
            constraint.influence = 0
    meshes = [bpy.data.objects[n] for n in ['F01_BodyOutfit','F01_HeadHair']]
    mesh_validation = []
    for obj in meshes:
        mesh = obj.data
        if mesh.shape_keys:
            raise ValueError('Shape keys require an explicit split remap')
        def signature():
            result = []
            for polygon in mesh.polygons:
                corners = []
                for i in polygon.loop_indices:
                    v = mesh.vertices[mesh.loops[i].vertex_index]
                    corners.append((tuple(v.co),tuple((g.group,g.weight) for g in v.groups),
                                    tuple(tuple(layer.data[i].uv) for layer in mesh.uv_layers)))
                result.append((polygon.material_index,polygon.use_smooth,tuple(corners)))
            return result
        before = signature()
        normals = [tuple(n.vector) for n in mesh.corner_normals]
        undefined_normals = [i for i,n in enumerate(normals) if sum(x*x for x in n)<.5]
        print('SOURCE_NORMALS',obj.name,'undefined',len(undefined_normals),flush=True)
        for polygon in mesh.polygons:
            if any(i in undefined_normals for i in polygon.loop_indices):
                if polygon.normal.length<.5:
                    raise ValueError('Undefined corner normal on degenerate face')
                for i in polygon.loop_indices:
                    if i in undefined_normals:
                        normals[i]=tuple(polygon.normal.normalized())
        duplicates = []
        seen = set()
        for face in mesh.polygons:
            key = tuple(sorted(face.vertices))
            if key in seen:
                duplicates.append((face.index,list(face.loop_indices),list(face.vertices)))
            seen.add(key)
        remap = []
        for face_index,loops,indices in duplicates:
            saved = [(tuple(mesh.vertices[i].co),[(g.group,g.weight) for g in mesh.vertices[i].groups])
                     for i in indices]
            first = len(mesh.vertices)
            mesh.vertices.add(len(indices))
            for offset,(loop,old_vertex,(co,groups)) in enumerate(zip(loops,indices,saved)):
                new_vertex = first+offset
                mesh.vertices[new_vertex].co = co
                mesh.attributes['.corner_vert'].data[loop].value = new_vertex
                for group,weight in groups:
                    obj.vertex_groups[group].add([new_vertex],weight,'REPLACE')
                remap.append({'face':face_index,'source_vertex':old_vertex,'split_vertex':new_vertex})
        mesh.update(calc_edges=True)
        mesh.normals_split_custom_set(normals)
        mesh.update()
        if mesh.validate(verbose=True):
            raise ValueError('Derived mesh still needed automatic destructive validation: '+obj.name)
        if before != signature():
            raise ValueError('Split repair changed textured surfaces or skin weights: '+obj.name)
        actual_normals = [tuple(n.vector) for n in mesh.corner_normals]
        normal_error = max((sum((a-b)**2 for a,b in zip(x,y))**.5
                            for x,y in zip(normals,actual_normals)),default=0)
        if len(normals)!=len(actual_normals) or normal_error>1e-3:
            raise ValueError('Split repair changed shading normals: '+str(normal_error))
        mesh_validation.append({'mesh':obj.name,'split_duplicate_faces':len(duplicates),
                                'vertex_remap':remap,'removed_faces':0,
                                'textured_surface_or_skin_weight_changes':0,
                                'maximum_corner_normal_error':normal_error,
                                'source_undefined_normals_repaired':len(undefined_normals),
                                'automatic_validation_changed_mesh':False})
    for obj in list(bpy.data.objects):
        if obj not in [root,rig,*meshes]:
            bpy.data.objects.remove(obj,do_unlink=True)
    scene.render.resolution_x = scene.render.resolution_y = 1536
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    cameras = []
    for direction, record in controls['available_cameras'].items():
        data = bpy.data.cameras.new('CAM_'+direction)
        data.type = 'ORTHO'
        data.ortho_scale = record['ortho_scale']
        obj = bpy.data.objects.new('CAM_'+direction,data)
        scene.collection.objects.link(obj)
        obj.location = record['location']
        obj.rotation_euler = record['rotation']
        obj['direction'] = direction
        obj['native_camera_source'] = str(args.controls)
        cameras.append(obj)
    scene.camera = bpy.data.objects['CAM_NE']
    bpy.context.view_layer.update()
    sockets = {}
    for name, bone_name in spec['anchor_bones'].items():
        socket = bpy.data.objects.new('SOCKET_'+name,None)
        scene.collection.objects.link(socket)
        socket.empty_display_type = 'ARROWS'
        socket.empty_display_size = .035
        socket.parent = rig
        socket.parent_type = 'BONE'
        socket.parent_bone = bone_name
        bpy.context.view_layer.update()
        desired = rig.matrix_world @ rig.pose.bones[bone_name].matrix
        socket.matrix_world = desired
        socket['bone'] = bone_name
        socket['anatomical_side_rule'] = 'L/R refers to anatomy, never screen side'
        bpy.context.view_layer.update()
        actual = socket.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
        error = max(abs(actual[r][c]-desired[r][c]) for r in range(4) for c in range(4))
        if error > 1e-5:
            raise ValueError('Socket attachment differs: '+name)
        sockets[name] = {'object':socket.name,'bone':bone_name,
                         'rest_world_matrix':[list(row) for row in desired],
                         'maximum_matrix_component_error':error}
    # Shared skeleton compatibility is not six mesh/anatomy approvals.
    profiles = []
    for klass in ['Swordsman','Mage','Archer']:
        for sex in ['male','female']:
            profiles.append({'class':klass,'sex':sex,'skeleton':'ARM_FantasyCharacter01',
                             'shared_skeleton_compatible':True,'class_mesh_included':False,
                             'sex_specific_anatomy_validated':False,
                             'required_parts':['HeadHair','BodyCostume','Weapon','WeaponHandOccluder'],
                             'optional_parts':['BackAccessory','Headgear','WeaponLightBack','WeaponLightFront']})
    args.output.mkdir(parents=True)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    scene['package_status'] = 'REUSABLE_AUTHORING_RIG_NOT_SIX_FINISHED_CHARACTERS'
    scene['rig_sha256'] = pins[str(args.rig)]
    scene['painting_camera_policy'] = 'Fixed native cameras; never reframe per pose'
    scene['illustration_status'] = 'Reference mesh only; not approved final character art'
    bpy.context.preferences.filepaths.save_version = 0
    blend = args.output/'shared-authoring-rig.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()),compress=True)
    glb = args.output/'shared-authoring-rig.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format='GLB',
                              use_selection=True,export_animations=False,
                              export_cameras=True,export_extras=True,
                              export_def_bones=False,export_all_influences=True)
    if any(sha(p)!=h for p,h in pins.items()):
        raise ValueError('A canonical input changed during packaging')
    report = {'status':'REUSABLE_AUTHORING_RIG_NOT_SIX_FINISHED_CHARACTERS',
              'blender':bpy.app.version_string,'source_sha256':pins,
              'implementation_sha256':sha(__file__), 'bone_count':len(rig.data.bones),
              'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,
                        'deform':b.use_deform,'rest_matrix':[list(row) for row in b.matrix_local]}
                       for b in rig.data.bones],
              'sockets':sockets,'cameras':controls['available_cameras'],
              'canvas':{'native':[1536,1536],'native_root':[768,1100.8]},
              'mesh_validation':mesh_validation,
              'meshes':[{'name':m.name,'base_vertices':len(m.data.vertices),
                         'armature_modifiers':[x.object.name for x in m.modifiers
                                               if x.type=='ARMATURE' and x.object]}
                        for m in meshes],
              'profiles':profiles,'actions_included':[],
              'female_mesh_included':False,'final_character_art':False,
              'runtime_admitted':False,'source_modified':False,
              'outputs':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in [blend,glb]}}
    (args.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copy2(__file__,args.output/'package-source.py')
    shutil.copy2(args.spec,args.output/'canonical-rig-spec.json')
    print('RIG_PACKAGE '+json.dumps({'bones':len(rig.data.bones),'cameras':len(cameras),
                                    'sockets':len(sockets),'outputs':report['outputs']}))


if __name__=='__main__':
    main()
