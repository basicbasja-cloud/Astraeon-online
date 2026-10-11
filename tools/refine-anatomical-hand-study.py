"""Native donor rotational grip study with separate thumb opposition."""
import bpy, math, json
from mathutils import Vector, Quaternion
s=bpy.data.scenes['ASTRAEON_ANATOMICAL_HAND_STUDY_05'];bpy.context.window.scene=s
root=bpy.data.objects['ROOT_AnatomicalHand05'];rig=bpy.data.objects['RIG_DonorHandInspection05'];hand=bpy.data.objects['SM_DonorHandInspection05']
for name in ['Hand05_Handle','Hand05_Guard']:
    obj=bpy.data.objects.get(name)
    if obj:bpy.data.objects.remove(obj,do_unlink=True)
q1=Quaternion(Vector((0,1,0)),math.radians(-45))@Quaternion(Vector((0,0,1)),math.radians(10))
rig.pose.bones['J_Bip_R_Thumb1'].rotation_quaternion=q1
rig.pose.bones['J_Bip_R_Thumb2'].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(-30))
rig.pose.bones['J_Bip_R_Thumb3'].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(-35))
mat=bpy.data.materials.new('Hand05_HandleLeather');mat.use_nodes=True
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(.055,.022,.012,1);bsdf.inputs['Roughness'].default_value=.6
center=Vector((.689,.026,1.372));bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.009,depth=.136,location=center)
handle=bpy.context.object;handle.name='Hand05_Handle';handle.rotation_euler.x=math.pi/2;handle.parent=root;handle.data.materials.append(mat)
for f in handle.data.polygons:f.use_smooth=True
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'
camera=s.camera;camera.data.ortho_scale=.24
# Read the actual base's hand landmarks, rather than assuming Fumiriya's height.
target=(rig.data.bones['J_Bip_R_Hand'].head_local+rig.data.bones['J_Bip_R_Index1'].head_local)/2+Vector((.008,0,-.012))
for label,yaw in [('front',-45),('palm',135),('side',-90),('back',0)]:
    root.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    camera.location=root.matrix_world@target+camera.rotation_euler.to_quaternion()@Vector((0,0,10))
    s.render.filepath=out+'native-grip-'+label+'.png';bpy.ops.render.render(write_still=True)
s['nativeGripStudy']=json.dumps({'handleCenter':list(center),'handleRadius':.009,'thumbOppositionDegrees':[-45,-10,30,35],'originalJointLengthsPreserved':True,'boneScales':[1,1,1],'ownerApproved':False,'productionRigApproved':False})
print('NATIVE_GRIP_ROTATIONS_UPDATED '+s['nativeGripStudy'])
bpy.context.window.scene=bpy.data.scenes['ASTRAEON_ASSET_FIT_04']
