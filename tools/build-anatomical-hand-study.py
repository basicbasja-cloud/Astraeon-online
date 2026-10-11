"""Licensed native donor hand pose inspection, preserving phalanx lengths.

This is not a new production rig, accepted anatomy, or animation handoff.
No forced circular finger paths or per-bone length scaling are used.
"""
import bpy, bmesh, math, json
from mathutils import Vector, Matrix, Quaternion
donor=bpy.data.scenes['ASTRAEON_VROID_BASE_MALE_INSPECTION']
assert bpy.data.scenes.get('ASTRAEON_ANATOMICAL_HAND_STUDY_05') is None
source=bpy.data.scenes['ASTRAEON_ASSET_FIT_04']
s=bpy.data.scenes.new('ASTRAEON_ANATOMICAL_HAND_STUDY_05');bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=48;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.view_settings.view_transform='Standard'
root=bpy.data.objects.new('ROOT_AnatomicalHand05',None);s.collection.objects.link(root)
rig0=next(o for o in donor.objects if o.type=='ARMATURE')
rig=rig0.copy();rig.data=rig0.data.copy();rig.name='RIG_DonorHandInspection05';s.collection.objects.link(rig);rig.parent=root
body0=next(o for o in donor.objects if o.type=='MESH' and o.name.startswith('Body'))
hand=body0.copy();hand.data=body0.data.copy();hand.name='SM_DonorHandInspection05';s.collection.objects.link(hand)
hand.parent=rig;hand.matrix_parent_inverse=body0.matrix_parent_inverse.copy()
for mod in hand.modifiers:
    if mod.type=='ARMATURE':mod.object=rig;mod.use_deform_preserve_volume=True
# Keep the entire donor hand and wrist, discarding unrelated clothes/torso.
names={g.index:g.name for g in hand.vertex_groups}
keep=set()
for v in hand.data.vertices:
    if any(g.weight>.01 and names[g.group].startswith(('J_Bip_R_Hand','J_Bip_R_Index','J_Bip_R_Middle','J_Bip_R_Ring','J_Bip_R_Little','J_Bip_R_Thumb')) for g in v.groups):keep.add(v.index)
bm=bmesh.new();bm.from_mesh(hand.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS')
# glTF vertices are split at UV seams. Weld matching locations without changing
# per-loop UVs; material is neutral for anatomy inspection.
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
bm.to_mesh(hand.data);bm.free();hand.data.update()
mat=bpy.data.materials.new('Hand05_NeutralClay');mat.use_nodes=True
bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(.38,.42,.48,1);bsdf.inputs['Roughness'].default_value=.72
hand.data.materials.clear();hand.data.materials.append(mat)
for f in hand.data.polygons:f.material_index=0;f.use_smooth=True
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.scale=(1,1,1)
camera0=source.camera;camera=camera0.copy();camera.data=camera0.data.copy();camera.name='CAM_AnatomicalHand05';s.collection.objects.link(camera);s.camera=camera
camera.data.ortho_scale=.34
for obj in source.objects:
    if obj.type=='LIGHT':
        copy=obj.copy();copy.data=obj.data.copy();copy.name='Hand05_'+obj.name;s.collection.objects.link(copy)
        # Source lights target a full character; reposition them around the hand.
        copy.location+=Vector((.70,0,.5));copy.data.energy*=.35
world=bpy.data.worlds.new('Hand05_World');world.use_nodes=True
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.35,.35,.35,1)
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.65;s.world=world
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'
target=Vector((.700,.026,1.520))
def aim(yaw):
    root.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    camera.location=root.matrix_world@target+camera.rotation_euler.to_quaternion()@Vector((0,0,10))
def render(name):s.render.filepath=out+name+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=640;s.render.resolution_y=640
aim(-45);render('native-open-hand')
angles={'Index':[48,87,48],'Middle':[52,90,48],'Ring':[57,92,50],'Little':[62,92,50]}
for digit,values in angles.items():
    for index,angle in enumerate(values,1):
        rig.pose.bones['J_Bip_R_'+digit+str(index)].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(-angle))
# Thumb opposition has a separate metacarpal motion and two flexion joints.
rig.pose.bones['J_Bip_R_Thumb1'].rotation_quaternion=Quaternion(Vector((0,1,0)),math.radians(-32))@Quaternion(Vector((0,0,1)),math.radians(-18))
rig.pose.bones['J_Bip_R_Thumb2'].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(-32))
rig.pose.bones['J_Bip_R_Thumb3'].rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(-18))
for label,yaw in [('front',-45),('palm',135),('side',-90),('back',0)]:aim(yaw);render('native-curl-'+label)
s['handInspection']=json.dumps({'donor':'VRoid Base Male beta / pixiv Inc.','license':'CC0-1.0','method':'Original mesh and inherited finger skeleton; rotational curl with unchanged bone scales','jointAngles':angles,'forcedCircularPaths':False,'productionRigApproved':False,'ownerApproved':False,'topologyNeedsReview':True,'vertices':len(hand.data.vertices),'faces':len(hand.data.polygons)})
print('NATIVE_HAND_STUDY '+s['handInspection'])
bpy.context.window.scene=source
