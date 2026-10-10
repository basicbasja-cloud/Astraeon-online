"""Source-native face, compatible cloth and cape refinement; static, unapproved.

No image-space pose correction, new skeleton, or runtime package is created.
"""
import bpy, math
from mathutils import Vector

scene=bpy.context.scene
assert scene.name=='ASTRAEON_ASSET_FIT_04'
root=bpy.data.objects['ROOT_AssetFit04']
prefix='SM_AssetFit04_'
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}

def toon(name,colors):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    diffuse=nodes.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(1,1,1,1)
    light=nodes.new('ShaderNodeShaderToRGB');links.new(diffuse.outputs[0],light.inputs[0])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
    for i,(position,color) in enumerate(colors):
        el=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(position)
        el.position=position;el.color=(*color,1)
    links.new(light.outputs[0],ramp.inputs['Fac'])
    emission=nodes.new('ShaderNodeEmission');links.new(ramp.outputs[0],emission.inputs['Color'])
    output=nodes.new('ShaderNodeOutputMaterial');links.new(emission.outputs[0],output.inputs['Surface'])
    return mat

skin=toon('Fit04_StylizedSkin',[(0,(.33,.13,.10)),(.20,(.64,.30,.20)),(.55,(.86,.51,.32)),(1,(.96,.70,.50))])
brow=toon('Fit04_SilverBrow',[(0,(.11,.075,.12)),(.5,(.25,.17,.22)),(1,(.43,.32,.36))])
body=bpy.data.objects[prefix+'Body'];body.data.materials[0]=skin
head_index=body.vertex_groups['Head'].index
backup=bpy.data.meshes.get('Fit04_BodyBeforeStyle')
if backup is None:
    backup=body.data.copy();backup.name='Fit04_BodyBeforeStyle';backup.use_fake_user=True
center=P['head']+Vector((-.025,-.070,.005))
for v,original in zip(body.data.vertices,backup.vertices):
    v.co=original.co
    weight=sum(g.weight for g in v.groups if g.group==head_index)
    if weight<.7:continue
    p=v.co;dx=p.x-center.x
    # Soften the adult nose projection and shorten its lower-face features.
    nose=math.exp(-((dx/.041)**2+((p.z-1.538)/.049)**2))
    front=max(0,min(1,(-p.y-.115)/.070))
    p.y+=.035*nose*front
    lower=max(0,min(1,(1.565-p.z)/.13))*front
    chin=max(0,min(1,(1.50-p.z)/.10))
    p.x=center.x+dx*(1+.10*lower)*(1-.20*chin)
    p.z+=.021*chin
body.data.update()

eyes=bpy.data.objects[prefix+'Eyes'];brows=bpy.data.objects[prefix+'Brows']
for obj in (eyes,brows):
    original=bpy.data.meshes.get(obj.name+'_PreStyle')
    if original is None:
        original=obj.data.copy();original.name=obj.name+'_PreStyle';original.use_fake_user=True
    for v,ov in zip(obj.data.vertices,original.vertices):
        side=-1 if ov.co.x<center.x else 1
        ec=center+Vector((side*.071,-.093,.007))
        v.co=ov.co
        v.co.x=ec.x+(ov.co.x-ec.x)*1.15
        if obj==eyes:
            v.co.z=ec.z+(ov.co.z-ec.z)*1.35
            v.co.y-=.018
        else:
            v.co.z+=.012;v.co.y-=.016
    obj.data.update()
brows.data.materials[0]=brow
eye_mat=eyes.data.materials[0].copy();eye_mat.name='Fit04_BlueEyes'
nodes=eye_mat.node_tree.nodes;links=eye_mat.node_tree.links
normal_image=bpy.data.images.load('C:/Users/Lenovo/Bas/Astra online/.character-tools/free-assets/quaternius-base-standard/extracted/Universal Base Characters[Standard]/Base Characters/Textures/T_Eye_Normal.png',check_existing=True)
normal_image.colorspace_settings.name='Non-Color';normal_image.pack()
for node in nodes:
    if node.type=='TEX_IMAGE' and node.image and 'Normal' in node.image.name:node.image=normal_image
color=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and 'Brown' in n.image.name)
principled=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
hue=nodes.new('ShaderNodeHueSaturation');hue.inputs['Hue'].default_value=.03
hue.inputs['Saturation'].default_value=1.6;hue.inputs['Value'].default_value=1.05
links.new(color.outputs['Color'],hue.inputs['Color']);links.new(hue.outputs[0],principled.inputs['Base Color'])
eyes.data.materials[0]=eye_mat

for name in ['Refitted_Boot_R','Refitted_Boot_L','Refitted_Trouser_R','Refitted_Trouser_L','Refitted_Sleeve_R','Refitted_Sleeve_L','Refitted_Tunic','Refitted_Glove_R','Refitted_Glove_L']:
    obj=bpy.data.objects[prefix+name];obj.hide_render=False
    # Smooth the same extracted topology as the anatomy before offsetting it.
    # Keep the complete naked body data for equipment-removal bakes.
    for mod in list(obj.modifiers):
        if mod.name in ('FittedSurfaceSmooth','FittedSurfaceClearance'):obj.modifiers.remove(mod)
    smooth=obj.modifiers.new('FittedSurfaceSmooth','SUBSURF');smooth.levels=1;smooth.render_levels=1
    obj.modifiers.move(len(obj.modifiers)-1,0)
    wrap=obj.modifiers.new('FittedSurfaceClearance','SHRINKWRAP');wrap.target=body;wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE';wrap.offset=.016 if 'Glove' in name else (.007 if 'Sleeve' in name else .029)
    obj.modifiers.move(len(obj.modifiers)-1,1)
for name,family in [('Male_Ranger_Feet_Boots','Refitted_Boot_R'),('Male_Ranger_Legs','Refitted_Trouser_R')]:
    obj=bpy.data.objects[prefix+name];obj.hide_render=True;obj['inspectionOnly']=True
    obj.data.materials.clear();obj.data.materials.append(bpy.data.objects[prefix+family].data.materials[0])
    # Reuse actual donor UVs as garment surface coordinates, never frame UVs.
    obj.data.uv_layers.active.name='PainterSurface'
    obj['licenseReceipt']='FREE_ASSET_PROVENANCE.json'
    obj['purpose']='Compatible boot/trouser geometry with original ASTRAEON material'
for obj in scene.objects:
    if obj.name.startswith(prefix+'Boot_'):obj.hide_render=True
    if obj.name.startswith(prefix+'ClosedGlove_'):obj.hide_render=True
    if any(token in obj.name for token in ['Fitted_Bracer','Forged_Bracer','Bracer_Crest','Bracer_FrontRidge']):
        original=bpy.data.meshes.get(obj.name+'_PreFit')
        if original is None:
            original=obj.data.copy();original.name=obj.name+'_PreFit';original.use_fake_user=True
        side=obj.name[-1];a=P['elbow_'+side];axis=(P['wrist_'+side]-a).normalized()
        for v,ov in zip(obj.data.vertices,original.vertices):
            axial=a+axis*(ov.co-a).dot(axis)
            v.co=axial+(ov.co-axial)*.73
        obj.data.update()

for name in ['Cape_PrimaryMass','Cape_Hem','Cape_LightningStudy']:
    bpy.data.objects[prefix+name].hide_render=True
for obj in list(scene.objects):
    if obj.name.startswith(prefix+'CapeRefit_'):bpy.data.objects.remove(obj,do_unlink=True)
mustard=bpy.data.objects[prefix+'Cape_PrimaryMass'].data.materials[0]
ivory=bpy.data.objects[prefix+'Tunic_IvoryFront'].data.materials[0]
verts=[];faces=[];rows=13;cols=17
for r in range(rows):
    t=r/(rows-1);half=.205+.155*math.sin(t*math.pi/2)
    for c in range(cols):
        q=c/(cols-1)*2-1
        x=P['chest'].x+q*half
        y=.16+.14*t+.026*math.sin(q*math.pi*3)*t
        z=1.28-.70*t-.02*q+.05*t**6*(1-abs(q))
        verts.append((x,y,z))
for r in range(rows-1):
    for c in range(cols-1):
        i=r*cols+c;faces.append((i,i+cols,i+cols+1,i+1))
mesh=bpy.data.meshes.new('Fit04CapeSurface');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new(prefix+'CapeRefit_Cloth',mesh);scene.collection.objects.link(obj);obj.parent=root
mesh.materials.append(mustard)
uv=mesh.uv_layers.new(name='PainterSurface')
for face in mesh.polygons:
    face.use_smooth=True
    for li in face.loop_indices:
        i=mesh.loops[li].vertex_index;uv.data[li].uv=(i%cols/(cols-1),i//cols/(rows-1))
solid=obj.modifiers.new('CapeThickness','SOLIDIFY');solid.thickness=.008;solid.offset=0

def seam(name,indices,radius):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(indices)-1)
    for point,i in zip(spline.points,indices):point.co=(*(Vector(verts[i])+Vector((0,.010,0))),1)
    o=bpy.data.objects.new(prefix+'CapeRefit_'+name,data);scene.collection.objects.link(o);o.parent=root;data.materials.append(ivory)
    return o
seam('Hem',[r*cols for r in range(rows)]+list(range((rows-1)*cols+1,rows*cols))+[r*cols+cols-1 for r in range(rows-2,-1,-1)],.006)
seam('RuneLeft',[10*cols+1,9*cols+3,10*cols+4,8*cols+6],.012)
seam('RuneRight',[8*cols+10,10*cols+12,9*cols+13,10*cols+15],.012)

out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/renders/'
root.rotation_euler.z=math.radians(45)
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=out+'SE-style-refined-large.png';bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
for d,a in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z=math.radians(a);scene.render.filepath=out+d+'-style-refined.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45)
scene['status']='STATIC_SOURCE_STYLE_REFINEMENT_UNAPPROVED'
print('STYLE_REFINEMENT_COMPLETE; NO_ARMATURE_OR_ACTION_COVERAGE')
