"""One equipped 2D assembly proof plus removal and alternate-blade checks.

Visible-only layers are for this exact source combination. They are not a
complete substitution-ready runtime package and retain no hidden gear surfaces.
"""
import bpy
import math

scene=bpy.context.scene
assert scene.name=='ASTRAEON_SOURCE_REFINEMENT_02'
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/source-refinement-02'
root=bpy.data.objects['ROOT_ReferenceFit']
geometry=[o for o in scene.objects if o.type in ('MESH','CURVE')]
heads=[o for o in bpy.data.collections['HEAD_FEATURES'].objects]
groups={
    'BaseBody':[bpy.data.objects['Body_VolumeBlockout']]+heads,
    'Hair':[o for o in geometry if o.name.startswith('Hair_')],
    'Weapon':[o for o in geometry if o.name.startswith(('Blade_AxisGuide','Hilt_Provisional','Guard_Provisional'))],
    'BackAccessory':[o for o in geometry if o.name.startswith('Cape_')],
}
claimed=set(o for group in groups.values() for o in group)
groups['Outfit']=[o for o in geometry if o not in claimed]
hidden={o:o.hide_render for o in geometry}
slots={o:[(s.link,s.material) for s in o.material_slots] for o in geometry}
original_yaw=root.rotation_euler.z
original_render=(scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
blade=bpy.data.objects['Blade_AxisGuide']
original_data=blade.data
holdout=bpy.data.materials.new('MAT_EquippedLayerHoldout');holdout.use_nodes=True
nodes=holdout.node_tree.nodes;nodes.clear()
surface=nodes.new('ShaderNodeHoldout');output=nodes.new('ShaderNodeOutputMaterial')
holdout.node_tree.links.new(surface.outputs[0],output.inputs['Surface'])

def restore():
    for obj,old in slots.items():
        for slot,(link,mat) in zip(obj.material_slots,old):slot.link=link;slot.material=mat
        obj.hide_render=hidden[obj]

def render(name):
    scene.render.filepath=out+'/renders/'+name
    bpy.ops.render.render(write_still=True)

try:
    root.rotation_euler.z=math.radians(45)
    scene.render.resolution_x=320;scene.render.resolution_y=320
    for name,target in groups.items():
        restore()
        for obj in geometry:
            if obj not in target:
                for slot in obj.material_slots:slot.link='OBJECT';slot.material=holdout
        render('equipped-layer-'+name+'-SE.png')
    restore()
    for obj in groups['Outfit']:obj.hide_render=True
    render('outfit-removed-SE.png')
    restore()
    # Change blade geometry only. Grip, hilt, guard, source pose and camera stay.
    alternate=original_data.copy()
    guard=bpy.data.objects['GUIDE_guard'].location.copy()
    tip=bpy.data.objects['GUIDE_blade_tip'].location.copy()
    axis=(tip-guard).normalized()
    from mathutils import Vector
    across=Vector((0,1,0)).cross(axis).normalized()
    for vertex in alternate.vertices:
        p=vertex.co-guard
        vertex.co=guard+p+axis*(p.dot(axis)*(-.20))+across*(p.dot(across)*.55)
    blade.data=alternate
    render('alternate-blade-SE.png')
    blade.data=original_data
    bpy.data.meshes.remove(alternate)
    print('EQUIPPED_2D_LAYERS_REMOVAL_AND_ALTERNATE_BLADE_BAKED')
finally:
    blade.data=original_data
    restore()
    root.rotation_euler.z=original_yaw
    scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath=original_render
    bpy.data.materials.remove(holdout)
    bpy.context.view_layer.update()
    print('SOURCE_LAYER_BAKE_STATE_RESTORED')
