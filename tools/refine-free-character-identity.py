"""Shared-source costume and facial refinement. No rig or view-specific patch."""
import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

s=bpy.context.scene
assert s.name=='ASTRAEON_ASSET_FIT_04'
p='SM_AssetFit04_';root=bpy.data.objects['ROOT_AssetFit04']
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
bronze=bpy.data.materials['Fit04_ForgedBronze'];gold=bpy.data.materials['Fit04_GoldTrim'];leather=bpy.data.materials['Fit04_BootLeather']

def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
palettes={
    bronze:[(.12,.055,.032),(.30,.15,.075),(.51,.31,.16),(.72,.49,.27),(.94,.79,.53)],
    gold:[(.23,.11,.04),(.51,.31,.12),(.78,.58,.30),(.97,.85,.56)],
    leather:[(.10,.045,.027),(.22,.095,.052),(.40,.22,.13),(.55,.34,.22)]}
atlas=bpy.data.images['material-atlas.png']
for mat,palette in palettes.items():
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    ramp=next(node for node in nodes if node.type=='VALTORGB')
    for e,col in zip(ramp.color_ramp.elements,palette):e.color=(*(linear(c) for c in col),1)
    # Existing painted swatch variation is sampled on native surface UVs.
    # Wrap the UV locally before remapping, preventing bleed into adjacent cells.
    uv=nodes.get('IdentitySurfaceUV') or nodes.new('ShaderNodeUVMap');uv.name='IdentitySurfaceUV';uv.uv_map='PainterSurface'
    fraction=nodes.get('IdentityUVWrap') or nodes.new('ShaderNodeVectorMath');fraction.name='IdentityUVWrap';fraction.operation='FRACTION'
    mapping=nodes.get('IdentityAtlasTile') or nodes.new('ShaderNodeMapping');mapping.name='IdentityAtlasTile'
    mapping.inputs['Scale'].default_value=(.30,.30,1)
    mapping.inputs['Location'].default_value=(.68,.68,0) if mat!=leather else (.35,.015,0)
    tex=nodes.get('IdentitySurfaceTexture') or nodes.new('ShaderNodeTexImage');tex.name='IdentitySurfaceTexture';tex.image=atlas
    bw=nodes.get('IdentityPaintValue') or nodes.new('ShaderNodeRGBToBW');bw.name='IdentityPaintValue'
    value=nodes.get('IdentityPaintRange') or nodes.new('ShaderNodeMath');value.name='IdentityPaintRange';value.operation='MULTIPLY_ADD';value.inputs[1].default_value=.65;value.inputs[2].default_value=.70
    mix=nodes.get('IdentitySurfaceMultiply') or nodes.new('ShaderNodeMixRGB');mix.name='IdentitySurfaceMultiply';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    links.new(uv.outputs[0],fraction.inputs[0]);links.new(fraction.outputs[0],mapping.inputs['Vector']);links.new(mapping.outputs[0],tex.inputs['Vector'])
    links.new(tex.outputs['Color'],bw.inputs[0]);links.new(bw.outputs[0],value.inputs[0]);links.new(value.outputs[0],mix.inputs[2]);links.new(ramp.outputs[0],mix.inputs[1])
    for node in nodes:
        if node.type=='EMISSION':links.new(mix.outputs[0],node.inputs['Color'])
        if node.type=='BSDF_PRINCIPLED':links.new(mix.outputs[0],node.inputs['Base Color']);node.inputs['Roughness'].default_value=.40
for obj in list(s.objects):
    if obj.name.startswith(p+'Identity_'):bpy.data.objects.remove(obj,do_unlink=True)

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(p+'Identity_'+name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(p+'Identity_'+name,data);s.collection.objects.link(obj);obj.parent=root
    data.materials.append(mat);obj['authority']='Native shared source geometry; static unapproved'
    return obj

def line(name,pts,radius,mat):
    data=bpy.data.curves.new(p+'Identity_'+name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    sp=data.splines.new('POLY');sp.points.add(len(pts)-1)
    for v,co in zip(sp.points,pts):v.co=(*co,1)
    obj=bpy.data.objects.new(p+'Identity_'+name,data);s.collection.objects.link(obj);obj.parent=root;data.materials.append(mat)
    return obj

def diamond(name,c,x,z,size,mat):
    x=x.normalized()*size;z=z.normalized()*size*1.25;n=x.cross(z).normalized()
    return mesh(name,[c-x,c+z,c+x,c-z,c+n*size*.5,c-n*size*.09],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)],mat)

# The approved guard has hooked quillons and a central lozenge. The blade axis,
# hilt diameter and anatomical hand placement remain the measured source frame.
g=P['guard'];axis=(P['blade_tip']-g).normalized()
x=Vector((0,1,0)).cross(axis).normalized();n=x.cross(axis).normalized()
outline=[(-.105,-.009),(-.111,-.027),(-.096,-.034),(-.079,-.025),(-.049,-.018),
         (-.020,-.014),(0,.032),(.024,-.010),(.065,-.006),(.096,.020),(.111,.016),
         (.111,-.005),(.102,-.014),(.074,-.027),(.038,-.034),(0,-.037),(-.041,-.030),(-.079,-.028)]
verts=[g+x*a+axis*b+n*d for d in [-.013,.013] for a,b in outline]
k=len(outline);faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
faces.extend((i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k))
guard=mesh('WeaponGuard',verts,faces,bronze)
bev=guard.modifiers.new('ForgedGuardEdges','BEVEL');bev.width=.004;bev.segments=3
for sign in [-1,1]:
    line('WeaponGuardRidge_'+str(sign),[g+x*a+axis*b+n*sign*.017 for a,b in outline]+[g+x*outline[0][0]+axis*outline[0][1]+n*sign*.017],.0024,gold)
    diamond('WeaponGuardCrest_'+str(sign),g+n*sign*.018,x,axis,.021,gold)
diamond('WeaponPommel',g-axis*.181,x,axis,.022,bronze)
bpy.data.objects[p+'Guard_Provisional'].hide_render=True

# Fit relief details to the actual evaluated garment instead of guessed depth.
deps=bpy.context.evaluated_depsgraph_get()
def surface_y(target,x,z):
    tree=BVHTree.FromObject(target,deps)
    hit,no,idx,dist=tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
    return hit.y if hit is not None else None

buckle_names=['Buckle_LeatherBack','Belt_Buckle','Belt_BucklePin','Belt_Rivet_-0.095','Belt_Rivet_0.095']
belt=bpy.data.objects[p+'Belt_Mass'];tunic=bpy.data.objects[p+'Refitted_Tunic']
waist=P['waist']+Vector((.025,0,-.008))
sy=surface_y(tunic,waist.x,waist.z)
front=min(sy if sy is not None else -.18,-.18)-.014
for name in buckle_names:
    obj=bpy.data.objects[p+name]
    if 'identityOriginalY' not in obj:obj['identityOriginalY']=obj.location.y
    # Buckle geometry was buried behind the thicker refitted shirt.
    obj.location.y=obj['identityOriginalY']+front+.157
    if name!='Buckle_LeatherBack':obj.location.y-=.030
for name,target in [('TunicGem','Tunic_FrontFlap'),('HipGem','Teal_HipMass'),('Chest_StarClasp','Refitted_Tunic')]:
    obj=bpy.data.objects[p+name];points=[v.co for v in obj.data.vertices]
    cx=sum(v.x for v in points)/len(points);cz=sum(v.z for v in points)/len(points)
    y=surface_y(bpy.data.objects[p+target],cx,cz)
    if y is not None:obj.location.y=y-.010-max(v.y for v in points)

# A leather sole establishes a shoe profile rather than an anatomical toe bulb.
# Its outline is measured from the evaluated fitted boot, never screen pixels.
for side in ['R','L']:
    boot=bpy.data.objects[p+'Refitted_Boot_'+side]
    evaluated=boot.evaluated_get(deps);vs=[v.co.copy() for v in evaluated.data.vertices]
    floor=min(v.z for v in vs);low=[v for v in vs if v.z<floor+.080]
    xmin=min(v.x for v in low);xmax=max(v.x for v in low);ymin=min(v.y for v in low);ymax=max(v.y for v in low)
    cx0=(xmin+xmax)/2;cy0=(ymin+ymax)/2;rx=(xmax-xmin)/2+.008;ry=(ymax-ymin)/2+.008
    verts=[];cols=48
    for z,factor in [(floor-.012,.95),(floor-.004,1.0),(floor+.020,1.0),(floor+.027,.97)]:
        for j in range(cols):
            a=math.tau*j/cols
            # Superellipse gives a rounded toe with a flatter leather welt.
            xx=math.copysign(abs(math.cos(a))**.78,math.cos(a));yy=math.copysign(abs(math.sin(a))**.80,math.sin(a))
            verts.append(Vector((cx0+rx*factor*xx,cy0+ry*factor*yy,z)))
    faces=[tuple(range(cols-1,-1,-1)),tuple(range(3*cols,4*cols))]
    faces.extend((r*cols+j,r*cols+(j+1)%cols,(r+1)*cols+(j+1)%cols,(r+1)*cols+j) for r in range(3) for j in range(cols))
    sole=mesh('BootSole_'+side,verts,faces,leather)
    bevel=sole.modifiers.new('LeatherSoleEdges','BEVEL');bevel.width=.003;bevel.segments=2
    line('BootWelt_'+side,verts[2*cols:3*cols]+[verts[2*cols]],.003,bronze)

# Reduce adult lip projection on the donor topology; keep the native surface,
# original UV registration, and vertex-group indices intact.
body=bpy.data.objects[p+'Body'];backup=bpy.data.meshes.get('Fit04_BodyBeforeIdentity')
if backup is None:
    backup=body.data.copy();backup.name='Fit04_BodyBeforeIdentity';backup.use_fake_user=True
cx=.055295749
head=body.vertex_groups['Head'].index
for v,old in zip(body.data.vertices,backup.vertices):
    v.co=old.co
    if sum(g.weight for g in v.groups if g.group==head)<.7:continue
    dx=v.co.x-cx;frontfac=max(0,min(1,(-v.co.y-.10)/.055))
    lips=math.exp(-((dx/.050)**2+((v.co.z-1.485)/.027)**2))*frontfac
    v.co.y+=.024*lips
    lower=max(0,min(1,(1.52-v.co.z)/.08))*frontfac
    v.co.x=cx+dx*(1-.09*lower)
body.data.update()
brows=bpy.data.objects[p+'Brows'];bb=bpy.data.meshes.get('Fit04_BrowsBeforeIdentity')
if bb is None:bb=brows.data.copy();bb.name='Fit04_BrowsBeforeIdentity';bb.use_fake_user=True
for v,old in zip(brows.data.vertices,bb.vertices):
    v.co=old.co;v.co.z=1.633+(old.co.z-1.633)*.58
brows.data.update()
eyes=bpy.data.objects[p+'Eyes']
em=bpy.data.materials.get('Fit04_IllustratedEyes') or bpy.data.materials.new('Fit04_IllustratedEyes');em.use_nodes=True
eyes.data.materials[0]=em;nodes=em.node_tree.nodes;nodes.clear();links=em.node_tree.links
uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap'
wrap=nodes.new('ShaderNodeVectorMath');wrap.operation='FRACTION';links.new(uv.outputs[0],wrap.inputs[0])
delta=nodes.new('ShaderNodeVectorMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=(.50,.50,0);links.new(wrap.outputs[0],delta.inputs[0])
distance=nodes.new('ShaderNodeVectorMath');distance.operation='LENGTH';links.new(delta.outputs[0],distance.inputs[0])
ramp_eye=nodes.new('ShaderNodeValToRGB');ramp_eye.color_ramp.interpolation='EASE'
eye_palette=[(0,(.035,.025,.045)),(.060,(.035,.025,.045)),(.075,(.34,.28,.40)),(.140,(.53,.49,.62)),(.155,(.15,.11,.21)),(.175,(.92,.89,.84)),(1,(.92,.89,.84))]
for i,(position,col) in enumerate(eye_palette):
    el=ramp_eye.color_ramp.elements[i] if i<2 else ramp_eye.color_ramp.elements.new(position);el.position=position;el.color=(*(linear(c) for c in col),1)
links.new(distance.outputs['Value'],ramp_eye.inputs[0])
bsdf=nodes.new('ShaderNodeBsdfPrincipled');bsdf.inputs['Roughness'].default_value=.55;links.new(ramp_eye.outputs[0],bsdf.inputs['Base Color'])
emission_eye=nodes.new('ShaderNodeEmission');links.new(ramp_eye.outputs[0],emission_eye.inputs['Color'])
mix_eye=nodes.new('ShaderNodeMixShader');mix_eye.inputs[0].default_value=.25;links.new(emission_eye.outputs[0],mix_eye.inputs[1]);links.new(bsdf.outputs[0],mix_eye.inputs[2])
out_eye=nodes.new('ShaderNodeOutputMaterial');links.new(mix_eye.outputs[0],out_eye.inputs['Surface'])
em['authority']='Native eye UV shader on modeled surfaces; no camera portrait projection'

# Warm cheek tint follows the actual head mesh through every view. It is a
# source color attribute, not a camera-projected face or altered reference image.
attr=body.data.color_attributes.get('IdentitySkinTint') or body.data.color_attributes.new(name='IdentitySkinTint',type='FLOAT_COLOR',domain='POINT')
for v in body.data.vertices:
    cheek=sum(math.exp(-(((v.co.x-(cx+side*.096))/.047)**2+((v.co.z-1.543)/.040)**2+((v.co.y+.175)/.070)**2)) for side in [-1,1])
    attr.data[v.index].color=(1,max(.77,1-.12*cheek),max(.72,1-.15*cheek),1)
skin=body.data.materials[0]
if skin.name!='Fit04_IdentitySkin':skin=skin.copy();skin.name='Fit04_IdentitySkin';body.data.materials[0]=skin
nodes=skin.node_tree.nodes;links=skin.node_tree.links
color=nodes.get('IdentityTint') or nodes.new('ShaderNodeVertexColor');color.name='IdentityTint';color.layer_name=attr.name
multiply=nodes.get('IdentityMultiply') or nodes.new('ShaderNodeMixRGB');multiply.name='IdentityMultiply';multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
ramp=next(node for node in nodes if node.type=='VALTORGB')
links.new(ramp.outputs['Color'],multiply.inputs[1]);links.new(color.outputs['Color'],multiply.inputs[2])
emission=next(node for node in nodes if node.type=='EMISSION');links.new(multiply.outputs[0],emission.inputs['Color'])
base_ramp=next(node for node in bpy.data.materials['Fit04_StylizedSkin'].node_tree.nodes if node.type=='VALTORGB')
for element,base in zip(ramp.color_ramp.elements,base_ramp.color_ramp.elements):
    element.color=(base.color[0],base.color[1]*.95,base.color[2]*1.03,1)

# Rebuild the thin lip contour at the changed surface, avoiding a floating line.
lip=bpy.data.objects.get(p+'FaceDetail_Mouth')
if lip:
    vs=[v.co.copy() for v in body.data.vertices]
    fs=[tuple(f.vertices) for f in body.data.polygons if any(any(g.group==head and g.weight>.8 for g in body.data.vertices[i].groups) for i in f.vertices)]
    tree=BVHTree.FromPolygons(vs,fs,all_triangles=False)
    for j,point in enumerate(lip.data.splines[0].points):
        t=j/(len(lip.data.splines[0].points)-1);x0=cx+(t-.5)*.040;z=1.479-.001*math.sin(math.pi*t)
        hit,no,idx,dist=tree.ray_cast(Vector((x0,-.4,z)),Vector((0,1,0)))
        if hit:point.co=(*(hit+Vector((0,-.002,0))),1)
    lip.data.bevel_depth=.0012

s['identityRefinement']=json.dumps({'ownerApproved':False,'runtimeAdmitted':False,'generatedUVOutput':'No output artifact from prior built-in attempt; not used','changes':['ornate source guard and pommel','surface-fitted buckle and garment relief','defined boot soles','linear bronze and leather colors with native UV paint variation','reduced adult lip projection','thinner brows','mesh-space cheek tint','native UV illustrated eye shading']})
root.rotation_euler.z=math.radians(45);s.render.resolution_x=1280;s.render.resolution_y=1280
s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/renders/SE-identity-refined-large.png'
bpy.ops.render.render(write_still=True)
s.render.resolution_x=320;s.render.resolution_y=320
print('IDENTITY_SOURCE_REFINED; OWNER_APPROVED_FALSE')
