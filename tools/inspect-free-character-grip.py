"""Source-local grip diagnostics and same-frame weapon holdout proof via MCP.

Does not bake animation or admit a runtime package. Restores materials/camera.
"""
import bpy
import math
import json
from mathutils import Vector

scene=bpy.context.scene
assert scene.name=='ASTRAEON_ASSET_FIT_04'
root=bpy.data.objects['ROOT_AssetFit04']
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04'
camera=scene.camera
guard=bpy.data.objects['GUIDE_guard'].location.copy()
tip=bpy.data.objects['GUIDE_blade_tip'].location.copy()
axis=(tip-guard).normalized()
weapon=[o for o in scene.objects if not o.hide_render and o.name.startswith(('SM_AssetFit04_Blade_AxisGuide','SM_AssetFit04_Hilt_Provisional','SM_AssetFit04_Guard_Provisional','SM_AssetFit04_Identity_Weapon'))]
geometry=[o for o in scene.objects if o.type in ('MESH','CURVE')]
original_slots={o:[(s.link,s.material) for s in o.material_slots] for o in geometry}
original_hidden={o:o.hide_render for o in geometry}
original_render=(scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath)
original_yaw=root.rotation_euler.z
diagnostic_data=camera.data.copy()
diagnostic=bpy.data.objects.new('CAM_GripDiagnostic',diagnostic_data)
scene.collection.objects.link(diagnostic)
diagnostic.rotation_euler=camera.rotation_euler.copy()
diagnostic_data.ortho_scale=.53
holdouts={}
for culled in (False,True):
    holdout=bpy.data.materials.new('Fit04_GripHoldout_'+str(culled));holdout.use_nodes=True;holdout.use_backface_culling=culled
    nodes=holdout.node_tree.nodes;nodes.clear()
    surface=nodes.new('ShaderNodeHoldout');output=nodes.new('ShaderNodeOutputMaterial')
    holdout.node_tree.links.new(surface.outputs[0],output.inputs['Surface']);holdouts[culled]=holdout

def restore_slots():
    for obj,slots in original_slots.items():
        for slot,(link,mat) in zip(obj.material_slots,slots):
            slot.link=link;slot.material=mat

def holdout_others():
    for obj in geometry:
        if obj not in weapon:
            for slot in obj.material_slots:
                culled=bool(slot.material and slot.material.use_backface_culling)
                slot.link='OBJECT';slot.material=holdouts[culled]

def render(path):
    scene.render.filepath=out+'/renders/'+path
    bpy.ops.render.render(write_still=True)

try:
    for label,angle in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
        root.rotation_euler.z=math.radians(angle)
        bpy.context.view_layer.update()
        target=root.matrix_world@(guard-axis*.072)
        diagnostic.location=target+diagnostic.rotation_euler.to_quaternion()@Vector((0,0,10))
        scene.camera=diagnostic
        scene.render.resolution_x=640;scene.render.resolution_y=640
        restore_slots()
        for obj in geometry:obj.hide_render=original_hidden[obj]
        render('grip-'+label+'.png')
        hand_objects=[o for o in geometry if o.name.startswith(('SM_AssetFit04_Refitted_Glove_R','SM_AssetFit04_Fitted_Bracer_R'))]
        for obj in geometry:obj.hide_render=obj not in weapon+hand_objects
        render('grip-isolated-'+label+'.png')
        # Both isolated and occluded images share the exact diagnostic frame.
        for obj in geometry:obj.hide_render=obj not in weapon
        render('weapon-isolated-'+label+'.png')
        for obj in geometry:obj.hide_render=original_hidden[obj]
        holdout_others()
        render('weapon-visible-'+label+'.png')
        # The actual costume can conceal the whole grasp from a rear view.
        # Isolate glove + sword to diagnose contact without that occlusion.
        for obj in geometry:obj.hide_render=obj not in weapon+hand_objects
        render('weapon-hand-masked-'+label+'.png')
    restore_slots()
    for obj in geometry:obj.hide_render=original_hidden[obj]
    scene.camera=camera
    scene.render.resolution_x=320;scene.render.resolution_y=320
    # Full production frames distinguish grip-crop occlusion from visibility
    # of the complete sword. No crop or independent scaling is used here.
    for label,angle in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
        root.rotation_euler.z=math.radians(angle)
        restore_slots()
        for obj in geometry:obj.hide_render=original_hidden[obj]
        holdout_others()
        render('Weapon-visible-'+label+'-fullcanvas.png')
        restore_slots()
        for obj in geometry:obj.hide_render=obj not in weapon
        render('Weapon-isolated-'+label+'-fullcanvas.png')
    print('GRIP_DIAGNOSTICS_AND_WEAPON_HOLDOUT_BAKED')
finally:
    restore_slots()
    for obj in geometry:obj.hide_render=original_hidden[obj]
    scene.camera=camera
    root.rotation_euler.z=original_yaw
    scene.render.resolution_x,scene.render.resolution_y,scene.render.filepath=original_render
    bpy.data.objects.remove(diagnostic,do_unlink=True)
    bpy.data.cameras.remove(diagnostic_data)
    for mat in holdouts.values():bpy.data.materials.remove(mat)
    bpy.context.view_layer.update()
    print('SOURCE_CAMERA_MATERIALS_VISIBILITY_RESTORED')
