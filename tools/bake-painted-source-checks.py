"""Static, full-canvas module/removal proof; never declares motion coverage."""
import bpy, math
scene=bpy.context.scene
assert scene.name=='ASTRAEON_SOURCE_LOOKDEV_03'
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/source-lookdev-03/renders/'
root=bpy.data.objects['ROOT_ReferenceFit']
geometry=[o for o in scene.objects if o.type=='MESH']
heads=list(bpy.data.collections['HEAD_FEATURES'].objects)
groups={'BaseBody':[bpy.data.objects['Body_VolumeBlockout']]+heads,
        'Hair':[o for o in geometry if o.name.startswith('Hair_')],
        'Weapon':[o for o in geometry if o.name.startswith(('Blade_AxisGuide','Hilt_Provisional','Guard_Provisional'))],
        'BackAccessory':[o for o in geometry if o.name.startswith('Cape_')]}
claimed=set(o for objects in groups.values() for o in objects)
groups['Outfit']=[o for o in geometry if o not in claimed]
hidden={o:o.hide_render for o in geometry}
materials={o:[(s.link,s.material) for s in o.material_slots] for o in geometry}
yaw=root.rotation_euler.z
settings=(scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
holdouts={}
for culled in (False,True):
    mat=bpy.data.materials.new('PaintedSourceHoldout_'+str(culled));mat.use_nodes=True;mat.use_backface_culling=culled
    nodes=mat.node_tree.nodes;nodes.clear();shader=nodes.new('ShaderNodeHoldout');output=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);holdouts[culled]=mat

def restore():
    for obj,slots in materials.items():
        obj.hide_render=hidden[obj]
        for slot,(link,mat) in zip(obj.material_slots,slots):slot.link=link;slot.material=mat

def render(name):
    scene.render.filepath=out+name+'.png';bpy.ops.render.render(write_still=True)

try:
    scene.render.resolution_x=320;scene.render.resolution_y=320
    for direction,angle in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
        root.rotation_euler.z=math.radians(angle)
        for removed in ('Outfit','Hair','Weapon','BackAccessory'):
            restore()
            for obj in groups[removed]:obj.hide_render=True
            render(removed.lower()+'-removed-'+direction)
        if direction=='SE':
            for name,target in groups.items():
                restore()
                for obj in geometry:
                    if obj not in target:
                        for slot in obj.material_slots:
                            culled=slot.material.use_backface_culling
                            slot.link='OBJECT';slot.material=holdouts[culled]
                render('equipped-layer-'+name+'-SE')
    print('PAINTED_SOURCE_REMOVALS_AND_SE_VISIBLE_LAYER_PROOF_RENDERED')
finally:
    restore();root.rotation_euler.z=yaw
    scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath=settings
    for mat in holdouts.values():bpy.data.materials.remove(mat)
    bpy.context.view_layer.update()
