"""Painted material textures on actual rest-surface UVs.

No sprite frame is generated or resized here. The same coated source supplies
every heading and equipment removal; topology/rigging remain separate gates.
"""
import bpy,math
from mathutils import Vector

scene=bpy.context.scene
assert scene.name=='ASTRAEON_SOURCE_LOOKDEV_03'
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/source-lookdev-03'
atlas=bpy.data.images.load(out+'/paint/material-atlas.png',check_existing=True);atlas.pack()
reference=bpy.data.images.load('C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/fresh-2d/candidate-01/candidate.png',check_existing=True);reference.pack()
geometry=[o for o in scene.objects if o.type in ('MESH','CURVE')]

for index,obj in enumerate(geometry):
    if obj.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
        obj=bpy.context.active_object;geometry[index]=obj
    data=obj.data
    uv=data.uv_layers.get('PainterSurface') or data.uv_layers.new(name='PainterSurface')
    faceuv=data.uv_layers.get('ApprovedFaceSE') or data.uv_layers.new(name='ApprovedFaceSE')
    ring=int(obj.get('paintRingSize',0));count=int(obj.get('paintRingCount',0))
    strips=ring>2 and count>1 and ring*count==len(data.vertices)
    xs=[v.co.x for v in data.vertices];ys=[v.co.y for v in data.vertices];zs=[v.co.z for v in data.vertices]
    axes=[xs,ys,zs];ranges=[max(a)-min(a) for a in axes]
    horizontal=0 if ranges[0]>=ranges[1] else 1
    hmin=min(axes[horizontal]);hspan=max(ranges[horizontal],.0001)
    zmin=min(zs);zspan=max(ranges[2],.0001)
    for polygon in data.polygons:
        wraps=strips and max(data.loops[i].vertex_index%ring for i in polygon.loop_indices)-min(data.loops[i].vertex_index%ring for i in polygon.loop_indices)>ring/2
        for li in polygon.loop_indices:
            vi=data.loops[li].vertex_index;p=data.vertices[vi].co
            if strips:
                u=(vi%ring)/ring
                if wraps and u<.5:u+=1
                v=(vi//ring)/(count-1)
            else:
                u=(p[horizontal]-hmin)/hspan;v=(p.z-zmin)/zspan
            uv.data[li].uv=(u,v)
            ru=(645+(math.cos(math.pi/4)*p.x-math.sin(math.pi/4)*p.y)/.0017)/1254
            rv=(99+(math.cos(math.radians(25))*p.z+math.sin(math.radians(25))*(math.sin(math.pi/4)*p.x+math.cos(math.pi/4)*p.y))/.0017)/1254
            faceuv.data[li].uv=(ru,rv)
    obj['paintUVAuthority']='Rest-surface UV; fixed with vertices'

families={'HairMass':0,'HairShadow':0,'HairLight':0,'WarmClay':1,'SkinShade':1,
          'Bronze':2,'BronzeLight':2,'Navy':3,'Ivory':4,'Mustard':5,'Olive':6,'BootBrown':7,'GloveSeam':7,'Teal':8}
coated={}

def coat(source):
    name=source.name.split('.')[0]
    mat=bpy.data.materials.new('Painter_'+source.name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    output=nodes.new('ShaderNodeOutputMaterial')
    diffuse=nodes.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(1,1,1,1)
    light=nodes.new('ShaderNodeShaderToRGB');links.new(diffuse.outputs[0],light.inputs[0])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
    palette=[(.0,(.38,.32,.42,1)),(.22,(.62,.57,.61,1)),(.65,(.94,.91,.88,1)),(1.,(1.12,1.07,1.,1))]
    for i,(position,color) in enumerate(palette):
        element=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(position)
        element.position=position;element.color=color
    links.new(light.outputs['Color'],ramp.inputs['Fac'])
    if name in families:
        cell=families[name];column=cell%3;row=2-cell//3
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map='PainterSurface'
        mapping=nodes.new('ShaderNodeMapping');mapping.vector_type='POINT'
        mapping.inputs['Scale'].default_value=(.96/3,.96/3,1)
        mapping.inputs['Location'].default_value=((column+.02)/3,(row+.02)/3,0)
        links.new(uv.outputs['UV'],mapping.inputs['Vector'])
        tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.extension='EXTEND'
        links.new(mapping.outputs['Vector'],tex.inputs['Vector']);base=tex.outputs['Color']
    else:
        rgb=nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=source.diffuse_color;base=rgb.outputs[0]
    shading=nodes.new('ShaderNodeMixRGB');shading.blend_type='MULTIPLY';shading.inputs[0].default_value=1
    links.new(base,shading.inputs[1]);links.new(ramp.outputs['Color'],shading.inputs[2])
    emission=nodes.new('ShaderNodeEmission');links.new(shading.outputs[0],emission.inputs['Color'])
    result=emission.outputs[0]
    if name in ('Bronze','BronzeLight','BladeGuide'):
        metal=nodes.new('ShaderNodeBsdfPrincipled');links.new(base,metal.inputs['Base Color'])
        metal.inputs['Metallic'].default_value=.4;metal.inputs['Roughness'].default_value=.4
        mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.18
        links.new(result,mix.inputs[1]);links.new(metal.outputs[0],mix.inputs[2]);result=mix.outputs[0]
    links.new(result,output.inputs['Surface'])
    mat['surfaceFamily']=name;mat['sourceTextureAtlas']=atlas.name
    return mat

for obj in geometry:
    for slot in obj.material_slots:
        if slot.material not in coated:coated[slot.material]=coat(slot.material)
        slot.material=coated[slot.material]

def face_paint(source,skin_only=False):
    mat=source.copy();mat.name='ApprovedFace_'+source.name
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    original=output.inputs['Surface'].links[0].from_socket
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='ApprovedFaceSE'
    tex=nodes.new('ShaderNodeTexImage');tex.image=reference;tex.extension='CLIP'
    links.new(uv.outputs[0],tex.inputs['Vector'])
    emission=nodes.new('ShaderNodeEmission');links.new(tex.outputs['Color'],emission.inputs['Color'])
    geom=nodes.new('ShaderNodeNewGeometry');normal=nodes.new('ShaderNodeVectorTransform')
    normal.vector_type='NORMAL';normal.convert_from='WORLD';normal.convert_to='OBJECT'
    links.new(geom.outputs['Normal'],normal.inputs['Vector'])
    dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.640856,-.640856,.422618)
    links.new(normal.outputs[0],dot.inputs[0])
    facing=nodes.new('ShaderNodeMapRange');facing.clamp=True
    facing.inputs['From Min'].default_value=.05;facing.inputs['From Max'].default_value=.32
    links.new(dot.outputs['Value'],facing.inputs['Value']);mask=facing.outputs['Result']
    def multiply(a,b):
        n=nodes.new('ShaderNodeMath');n.operation='MULTIPLY';links.new(a,n.inputs[0]);links.new(b,n.inputs[1]);return n.outputs[0]
    mask=multiply(mask,tex.outputs['Alpha'])
    if skin_only:
        color=nodes.new('ShaderNodeSeparateColor');color.mode='HSV';links.new(tex.outputs['Color'],color.inputs['Color'])
        warm=nodes.new('ShaderNodeMath');warm.operation='LESS_THAN';warm.inputs[1].default_value=.14
        links.new(color.outputs[0],warm.inputs[0]);mask=multiply(mask,warm.outputs[0])
        coords=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs[0],coords.inputs[0])
        for socket,low,high in [(coords.outputs['X'],.46,.67),(coords.outputs['Y'],.645,.765)]:
            lo=nodes.new('ShaderNodeMath');lo.operation='GREATER_THAN';lo.inputs[1].default_value=low;links.new(socket,lo.inputs[0])
            hi=nodes.new('ShaderNodeMath');hi.operation='LESS_THAN';hi.inputs[1].default_value=high;links.new(socket,hi.inputs[0])
            mask=multiply(mask,lo.outputs[0]);mask=multiply(mask,hi.outputs[0])
    mix=nodes.new('ShaderNodeMixShader');links.new(mask,mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(emission.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],output.inputs['Surface']);mat['scope']='Face only; no costume or hair on hidden body'
    return mat

# A three-quarter portrait projection duplicates/misplaces the native eyes when
# the head rotates. Keep facial features as actual surfaces with their own
# materials. The earlier portrait projection is a rejected diagnostic only.
body=bpy.data.objects['Body_VolumeBlockout']
body['portraitProjectionEnabled']=False

outline=bpy.data.materials.new('Painter_Contour');outline.use_nodes=True;outline.use_backface_culling=True
nodes=outline.node_tree.nodes;nodes.clear()
emission=nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(.018,.012,.021,1)
output=nodes.new('ShaderNodeOutputMaterial');outline.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
for obj in geometry:
    if obj.name in bpy.data.collections['HEAD_FEATURES'].objects or max(obj.dimensions)<.08:continue
    obj.data.materials.append(outline)
    solid=obj.modifiers.new('PainterContour','SOLIDIFY');solid.thickness=.0035 if obj.name.startswith('Hair') else .0028
    solid.offset=1;solid.use_flip_normals=True;solid.material_offset=len(obj.data.materials)-1
    solid.material_offset_rim=len(obj.data.materials)-1

root=bpy.data.objects['ROOT_ReferenceFit']
for label,angle in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z=math.radians(angle)
    scene.render.resolution_x=320;scene.render.resolution_y=320
    scene.render.filepath=out+'/renders/'+label+'-surface-painted.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45)
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=out+'/renders/SE-surface-painted-large.png';bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
bpy.ops.wm.save_as_mainfile(filepath=out+'/surface-painted-source.blend')
print('NATIVE_UV_PAINTED_SOURCE_SAVED_FOR_8_VIEW_QA_NOT_OWNER_APPROVED')
