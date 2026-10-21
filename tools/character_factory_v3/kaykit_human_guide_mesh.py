"""Fit the CC0 human GUIDE mesh once to the native bow donor skeleton.

This adapts guide geometry, not animation curves or 2D artwork. Native bow
handslot trajectories remain authoritative. It is not a finished hero model.
"""
import bpy
from mathutils import Vector


def bind_human_guide(native,source_path):
    old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(source_path))
    human=next(o for o in bpy.data.objects if o not in old and o.type=='ARMATURE')
    for t in human.animation_data.nla_tracks:t.mute=True
    source_action=bpy.data.actions.get('Idle_Shield_'+human.name)
    if source_action:
        human.animation_data.action=source_action
        if hasattr(human.animation_data,'action_slot')and source_action.slots:human.animation_data.action_slot=source_action.slots[0]
    else:human.animation_data.action=None
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    maps={'root':'root','pelvis':'hips','spine_01':'spine','spine_02':'spine','spine_03':'chest','neck':'head','head':'head'}
    for s in ['l','r']:
        maps.update({f'clavicle_{s}':'chest',f'upperarm_{s}':f'upperarm.{s}',f'lowerarm_{s}':f'lowerarm.{s}',f'hand_{s}':f'hand.{s}',f'thigh_{s}':f'upperleg.{s}',f'calf_{s}':f'lowerleg.{s}',f'foot_{s}':f'foot.{s}',f'ball_{s}':f'toes.{s}'})
    target_rest={n:native.matrix_world@b.matrix_local for n,b in native.data.bones.items()}
    source_pose={n:human.matrix_world@b.matrix for n,b in human.pose.bones.items()}
    meshes=[o for o in bpy.data.objects if o not in old and o.type=='MESH'and any(m.type=='ARMATURE'and m.object==human for m in o.modifiers)]
    for obj in bpy.data.objects:
        if obj not in old and obj.type=='MESH'and obj not in meshes:obj.hide_render=True
    if not meshes:raise ValueError('Missing human guide geometry')
    for mesh_obj in meshes:
        evaluated=mesh_obj.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated_mesh=evaluated.to_mesh();positions=[];weights=[]
        groups={g.index:g.name for g in mesh_obj.vertex_groups}
        for vertex,posed_vertex in zip(mesh_obj.data.vertices,evaluated_mesh.vertices):
            world=evaluated.matrix_world@posed_vertex.co;location=Vector();total=0.;mapped={}
            for group in vertex.groups:
                bone=groups[group.group]
                if bone.endswith('_leaf'):bone=bone[:-5]
                if bone not in source_pose:continue
                if bone.startswith('clavicle_'):bone='spine_03'
                if bone not in maps:
                    side='l'if bone.endswith('_l')else'r'if bone.endswith('_r')else None
                    if side and any(bone.startswith(f)for f in ['index','middle','ring','pinky','thumb']):bone='hand_'+side
                    else:continue
                target=maps[bone];local=source_pose[bone].inverted()@world
                # Preserve radial volume; adapt longitudinal segment length.
                source_length=human.data.bones[bone].length;target_length=native.data.bones[target].length
                if source_length>.015 and bone not in ['head','neck','root']:local.y*=min(1.6,max(.65,target_length/source_length))
                target_matrix=target_rest[target].copy()
                if bone=='spine_02':target_matrix.translation=target_rest['spine'].translation.lerp(target_rest['chest'].translation,.5)
                if bone=='head':target_matrix.translation+=Vector((0,0,.07))
                point=target_matrix@local;location+=point*group.weight;total+=group.weight;mapped[target]=mapped.get(target,0)+group.weight
            if total<=0:raise ValueError(f'Unmapped human guide vertex {mesh_obj.name}/{vertex.index}: {[(groups[g.group],g.weight)for g in vertex.groups]}')
            positions.append(tuple(location/total));weights.append({n:w/total for n,w in mapped.items()})
        evaluated.to_mesh_clear()
        data=bpy.data.meshes.new('NativeBowHumanGuideMesh');data.from_pydata(positions,[],[tuple(p.vertices)for p in mesh_obj.data.polygons]);data.update()
        obj=bpy.data.objects.new('NativeBowHumanGuide',data);bpy.context.scene.collection.objects.link(obj)
        for material in mesh_obj.data.materials:data.materials.append(material)
        for p,old_polygon in zip(data.polygons,mesh_obj.data.polygons):p.material_index=old_polygon.material_index;p.use_smooth=True
        names={n for values in weights for n in values};vg={n:obj.vertex_groups.new(name=n)for n in names}
        for i,values in enumerate(weights):
            for n,w in values.items():vg[n].add([i],w,'REPLACE')
        # Vertices were built in world coordinates; the native armature's
        # world transform remains explicit through the normal armature modifier.
        obj.parent=native;obj.matrix_parent_inverse=native.matrix_world.inverted();modifier=obj.modifiers.new('NativeBowSkin','ARMATURE');modifier.object=native
        mesh_obj.hide_render=True
    human.hide_render=True
    return native
