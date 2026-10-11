"""Give source-native cloth its own volume and surface-fitted details."""
import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05']
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
r=json.loads(s['anatomySourceReceipt'])
for side in ['R','L']:
    cloth=bpy.data.objects[p+'Cloth_Trouser_'+side];key='Anatomy05TrouserBeforeVolume_'+side;backup=bpy.data.meshes.get(key)
    if backup is None:backup=cloth.data.copy();backup.name=key;backup.use_fake_user=True
    a=P['hip_'+side];b=P['knee_'+side];direction=(b-a).normalized();length=(b-a).length
    for v,old in zip(cloth.data.vertices,backup.vertices):
        t=max(0,min(1,(old.co-a).dot(direction)/length));center=a+direction*(old.co-a).dot(direction);radial=old.co-center
        fullness=1+.33*math.sin(math.pi*t)**.8
        angle=math.atan2(radial.y,radial.x);fold=.0025*math.sin(4*angle+8*t)*math.sin(math.pi*t)
        v.co=center+radial*fullness+radial.normalized()*fold
    cloth.data.update()
# Small polished joins and relief sit on the actual fitted garment surface.
geometry=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
for name in ['TunicGem','HipGem','Chest_StarClasp']:
    detail=bpy.data.objects[p+name]
    target=bpy.data.objects[p+('Tunic_FrontFlap' if name=='TunicGem' else 'Teal_HipMass' if name=='HipGem' else 'Cloth_Tunic')]
    deps=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(target,deps)
    points=[v.co for v in detail.data.vertices];cx=sum(v.x for v in points)/len(points);cz=sum(v.z for v in points)/len(points)
    # FromObject supplies object-space vertices in this scene, all source
    # geometry has identity basis except the deliberately translated details.
    hit,no,index,distance=tree.ray_cast(Vector((cx,-1,cz)),Vector((0,1,0)),2)
    if hit is not None:detail.location.y=hit.y-.006-max(v.y for v in points)
r['clothVolumeStudy']={'trouserFullnessPeak':1.33,'sourceNativeModeledFolds':True,'surfaceFittedReliefs':['TunicGem','HipGem','Chest_StarClasp'],'ownerApproved':False};s['anatomySourceReceipt']=json.dumps(r)
saved=(root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
try:
    s.render.resolution_x=1280;s.render.resolution_y=1280;root.rotation_euler.z=math.radians(45)
    s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/SE-cloth-volume-study.png';bpy.ops.render.render(write_still=True)
finally:root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath=saved
print('CLOTH_VOLUME_STUDY_RENDERED')
