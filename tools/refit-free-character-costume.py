"""Fit original costume shells to the licensed anatomy in the shared pose."""
import bpy,math
from mathutils import Vector
scene=bpy.context.scene
assert scene.name=='ASTRAEON_ASSET_FIT_04'
root=bpy.data.objects['ROOT_AssetFit04'];body=bpy.data.objects['SM_AssetFit04_Body']
source=bpy.data.scenes['ASTRAEON_SOURCE_LOOKDEV_03']
geometry=[]
families={}
for obj in source.objects:
    if obj.type=='MESH' and obj.name.startswith('Fitted_'):
        families[obj.name.removeprefix('Fitted_')]=obj.data.materials[0]

def group(poly):
    weights={}
    for index in poly.vertices:
        for influence in body.data.vertices[index].groups:
            name=body.vertex_groups[influence.group].name
            weights[name]=weights.get(name,0)+influence.weight
    name=max(weights,key=weights.get)
    if name=='Head':return None
    if name in ('root','pelvis','spine_01','spine_02','spine_03','neck_01'):return 'Tunic'
    side='R' if name.endswith('_r') else 'L'
    if name.startswith(('clavicle','upperarm')):return 'Sleeve_'+side
    if name.startswith('lowerarm'):return 'Sleeve_'+side  # continuous navy cloth under the separate forged bracer
    if name.startswith('thigh'):return 'Trouser_'+side
    if name.startswith(('calf','foot','ball')):return 'Boot_'+side
    return 'Glove_'+side

groups={}
for poly in body.data.polygons:
    name=group(poly)
    if name:groups.setdefault(name,[]).append(poly)

for name,polys in groups.items():
    indices=sorted({i for face in polys for i in face.vertices});remap={i:j for j,i in enumerate(indices)}
    offset=.007 if name.startswith('Glove') else .021
    vertices=[body.data.vertices[i].co+body.data.vertices[i].normal*offset for i in indices]
    faces=[tuple(remap[i] for i in poly.vertices) for poly in polys]
    data=bpy.data.meshes.new('Fit04Cloth_'+name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new('SM_AssetFit04_Refitted_'+name,data);scene.collection.objects.link(obj);obj.parent=root
    data.materials.append(families[name])
    for face in data.polygons:face.use_smooth=True
    uv=data.uv_layers.new(name='PainterSurface')
    xs=[v.co.x for v in data.vertices];ys=[v.co.y for v in data.vertices];zs=[v.co.z for v in data.vertices]
    horizontal=0 if max(xs)-min(xs)>max(ys)-min(ys) else 1
    hs=xs if horizontal==0 else ys;hmin=min(hs);hspan=max(max(hs)-hmin,.0001)
    zmin=min(zs);zspan=max(max(zs)-zmin,.0001)
    for face in data.polygons:
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co
            uv.data[li].uv=((p[horizontal]-hmin)/hspan,(p.z-zmin)/zspan)
    solid=obj.modifiers.new('RefittedClothThickness','SOLIDIFY');solid.thickness=.008;solid.offset=-1
    obj['sourceOrigin']='Shell fitted to fresh licensed anatomy; original ASTRAEON material'
    obj['ownerApproved']=False;geometry.append(obj)

light=bpy.data.images.load('C:/Users/Lenovo/Bas/Astra online/.character-tools/free-assets/quaternius-base-standard/extracted/Universal Base Characters[Standard]/Base Characters/Textures/T_Superhero_Male_Ligh.png',check_existing=True)
light.pack()
skin=body.data.materials[0].copy();skin.name='Fit04_LightSkin'
for n in skin.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('T_Superhero_Male_Dark'):n.image=light
body.data.materials[0]=skin
# Subdivision smooths the source-study surface; it does not certify deformation
# edge flow, remove inherited poles, or approve a retopology/rig handoff.
sub=body.modifiers.new('AnatomyStudySurface','SUBSURF');sub.levels=1;sub.render_levels=1

out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/renders/'
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=out+'SE-costume-refit.png';bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
for d,a in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z=math.radians(a);scene.render.filepath=out+d+'.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45)
print('STATIC_COSTUME_FITTED_TO_LICENSED_ANATOMY',len(geometry),'NOT_OWNER_APPROVED')
