"""Native surface finish and face contours on the static asset-fit study."""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

s=bpy.context.scene;assert s.name=='ASTRAEON_ASSET_FIT_04'
p='SM_AssetFit04_';root=bpy.data.objects['ROOT_AssetFit04']
for obj in s.objects:
    if obj.type=='LIGHT':
        if 'fit04OriginalEnergy' not in obj.data:obj.data['fit04OriginalEnergy']=obj.data.energy
        obj.data.energy=obj.data['fit04OriginalEnergy']*.55

def material(name,palette,metal=False):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True
    ns=mat.node_tree.nodes;ns.clear();ls=mat.node_tree.links
    diffuse=ns.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(1,1,1,1)
    light=ns.new('ShaderNodeShaderToRGB');ls.new(diffuse.outputs[0],light.inputs[0])
    ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
    for i,(pos,col) in enumerate(palette):
        e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=(*col,1)
    ls.new(light.outputs[0],ramp.inputs['Fac'])
    em=ns.new('ShaderNodeEmission');ls.new(ramp.outputs[0],em.inputs['Color']);result=em.outputs[0]
    if metal:
        principled=ns.new('ShaderNodeBsdfPrincipled');ls.new(ramp.outputs[0],principled.inputs['Base Color'])
        principled.inputs['Metallic'].default_value=.7;principled.inputs['Roughness'].default_value=.3
        mix=ns.new('ShaderNodeMixShader');mix.inputs[0].default_value=.25
        ls.new(result,mix.inputs[1]);ls.new(principled.outputs[0],mix.inputs[2]);result=mix.outputs[0]
    out=ns.new('ShaderNodeOutputMaterial');ls.new(result,out.inputs['Surface'])
    mat['authority']='Source-native shading; no generated frame paint'
    return mat

bronze=material('Fit04_ForgedBronze',[(0,(.085,.030,.017)),(.20,(.24,.095,.034)),(.5,(.49,.23,.068)),(.85,(.70,.40,.15)),(1,(.88,.64,.30))],True)
trim=material('Fit04_GoldTrim',[(0,(.18,.069,.020)),(.3,(.45,.20,.057)),(.7,(.71,.41,.14)),(1,(.91,.69,.32))],True)
leather=material('Fit04_BootLeather',[(0,(.075,.026,.014)),(.22,(.17,.063,.029)),(.65,(.34,.15,.065)),(1,(.47,.23,.11))])
ink=material('Fit04_FaceInk',[(0,(.025,.014,.022)),(1,(.055,.026,.030))])
for obj in s.objects:
    if obj.type!='MESH':continue
    for i,m in enumerate(obj.data.materials):
        if m is None:continue
        family=m.get('surfaceFamily','')
        if family=='Bronze':obj.data.materials[i]=bronze
        if family=='BronzeLight':obj.data.materials[i]=trim
        if family=='BootBrown':obj.data.materials[i]=leather
        # Material changes belong only to copied meshes in this scene.

for side in ['R','L']:
    boot=bpy.data.objects[p+'Refitted_Boot_'+side]
    toe=boot.vertex_groups.get('BootToeSurface') or boot.vertex_groups.new(name='BootToeSurface')
    for v in boot.data.vertices:
        if v.co.z<.11:toe.add([v.index],max(0,min(1,(.11-v.co.z)/.055)),'REPLACE')
    smooth=boot.modifiers.get('BootToeLeatherSmooth') or boot.modifiers.new('BootToeLeatherSmooth','SMOOTH')
    smooth.vertex_group=toe.name;smooth.factor=1;smooth.iterations=8
    # Round the toe after surface clearance; a leather shoe must not reproduce
    # every naked toe crease in the anatomical base.
    for name in ['Boot_KneeCrest_'+side,'Boot_KneeBorder_'+side,'Boot_AnkleBand_'+side,'Boot_ShinPiping_'+side+'_-1','Boot_ShinPiping_'+side+'_1']:
        bpy.data.objects[p+name].hide_render=False
    bpy.data.objects[p+'Boot_KneeCrest_'+side].location.y=-.040
    bpy.data.objects[p+'Bracer_Crest_'+side].location.y=-.013

for obj in list(s.objects):
    if obj.name.startswith(p+'FaceDetail_'):bpy.data.objects.remove(obj,do_unlink=True)
def line(name,pts,radius,mat):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(pts)-1)
    for pt,co in zip(spline.points,pts):pt.co=(*co,1)
    o=bpy.data.objects.new(p+'FaceDetail_'+name,data);s.collection.objects.link(o);o.parent=root;data.materials.append(mat)
    return o
eyes=bpy.data.objects[p+'Eyes']
verts=[v.co.copy() for v in eyes.data.vertices];faces=[tuple(f.vertices) for f in eyes.data.polygons]
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
cx=.055295749
for side in [-1,1]:
    vs=[v for v in verts if (v.x-cx)*side>0]
    xmin=min(v.x for v in vs);xmax=max(v.x for v in vs);zmin=min(v.z for v in vs);zmax=max(v.z for v in vs)
    pts=[]
    for j in range(13):
        t=j/12;x=xmin+(xmax-xmin)*(.10+.80*t)
        z=(zmin+zmax)/2+(zmax-zmin)*(.26*math.sin(math.pi*t)+.07)
        hit,normal,index,distance=bvh.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))
        if hit:pts.append(hit+Vector((0,-.003,0)))
    if len(pts)>2:line('UpperLid_'+str(side),pts,.0032,ink)

# Lip contour is located on the actual facial surface, not a floating card.
body=bpy.data.objects[p+'Body'];headidx=body.vertex_groups['Head'].index
vs=[v.co.copy() for v in body.data.vertices];fs=[tuple(f.vertices) for f in body.data.polygons if any(any(g.group==headidx and g.weight>.8 for g in body.data.vertices[i].groups) for i in f.vertices)]
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=False)
pts=[]
for j in range(11):
    t=j/10;x=cx+(t-.5)*.046;z=1.479-.002*math.sin(math.pi*t)
    hit,normal,index,distance=bvh.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))
    if hit:pts.append(hit+Vector((0,-.002,0)))
if len(pts)>2:line('Mouth',pts,.0017,leather)

out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/renders/'
root.rotation_euler.z=math.radians(45);s.render.resolution_x=1280;s.render.resolution_y=1280
s.render.filepath=out+'SE-surface-finish-large.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=320;s.render.resolution_y=320
for d,a in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z=math.radians(a);s.render.filepath=out+d+'-surface-finish.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45)
print('NATIVE_SURFACE_FINISH_RENDERED; OWNER_APPROVAL_FALSE')
