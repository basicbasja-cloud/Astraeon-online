"""Source-native projection-painting diagnostic; not a completed painted factory.

The approved reference pixels are unchanged. Actual mesh UVs store the registered
SE projection, so surface color follows vertices rather than a floating card.
Opposing surfaces keep their structural material. Rear textures remain missing.
"""
import bpy,math
from mathutils import Vector

scene=bpy.context.scene
assert scene.name=='ASTRAEON_SOURCE_LOOKDEV_03'
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/source-lookdev-03'
reference=bpy.data.images.load('C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/fresh-2d/candidate-01/candidate.png',check_existing=True)
reference.pack()
geometry=[o for o in scene.objects if o.type in ('MESH','CURVE')]
for index,obj in enumerate(geometry):
    if obj.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target='MESH')
        obj=bpy.context.active_object;geometry[index]=obj
    uv=obj.data.uv_layers.get('PaintReferenceSE') or obj.data.uv_layers.new(name='PaintReferenceSE')
    for loop in obj.data.loops:
        p=obj.data.vertices[loop.vertex_index].co
        u=(645+(math.cos(math.pi/4)*p.x-math.sin(math.pi/4)*p.y)/.0017)/1254
        v=(99+(math.cos(math.radians(25))*p.z+math.sin(math.radians(25))*(math.sin(math.pi/4)*p.x+math.cos(math.pi/4)*p.y))/.0017)/1254
        uv.data[loop.index].uv=(u,v)
    obj['paintStudyUV']='Rest-surface SE reference projection; not a complete multi-view texture'

painted={}
for obj in geometry:
    for slot in obj.material_slots:
        source=slot.material
        if source not in painted:
            mat=source.copy();mat.name='PaintStudy_'+source.name
            nodes=mat.node_tree.nodes;links=mat.node_tree.links
            output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
            original=output.inputs['Surface'].links[0].from_socket
            uv=nodes.new('ShaderNodeUVMap');uv.uv_map='PaintReferenceSE'
            texture=nodes.new('ShaderNodeTexImage');texture.image=reference;texture.extension='CLIP'
            links.new(uv.outputs['UV'],texture.inputs['Vector'])
            emission=nodes.new('ShaderNodeEmission');links.new(texture.outputs['Color'],emission.inputs['Color'])
            geometry_node=nodes.new('ShaderNodeNewGeometry')
            transform=nodes.new('ShaderNodeVectorTransform');transform.vector_type='NORMAL';transform.convert_from='WORLD';transform.convert_to='OBJECT'
            links.new(geometry_node.outputs['Normal'],transform.inputs['Vector'])
            dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.640856,-.640856,.422618)
            links.new(transform.outputs['Vector'],dot.inputs[0])
            facing=nodes.new('ShaderNodeMapRange');facing.clamp=True
            facing.inputs['From Min'].default_value=-.08;facing.inputs['From Max'].default_value=.12
            links.new(dot.outputs['Value'],facing.inputs['Value'])
            coverage=nodes.new('ShaderNodeMath');coverage.operation='MULTIPLY'
            links.new(facing.outputs['Result'],coverage.inputs[0]);links.new(texture.outputs['Alpha'],coverage.inputs[1])
            mix=nodes.new('ShaderNodeMixShader');links.new(coverage.outputs[0],mix.inputs[0])
            links.new(original,mix.inputs[1]);links.new(emission.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
            mat['studyOnly']=True;mat['missingRearPaint']=True;painted[source]=mat
        slot.material=painted[source]
root=bpy.data.objects['ROOT_ReferenceFit']
for label,angle in [('SE',45),('S',0),('W',-90),('NW',-135),('N',-180)]:
    root.rotation_euler.z=math.radians(angle)
    scene.render.resolution_x=1280 if label=='SE' else 320
    scene.render.resolution_y=scene.render.resolution_x
    scene.render.filepath=out+'/renders/'+label+'-projection-study.png'
    bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45)
scene.render.resolution_x=320;scene.render.resolution_y=320
bpy.ops.wm.save_as_mainfile(filepath=out+'/projection-study.blend')
print('SOURCE_NATIVE_UV_PAINTING_STUDY_SAVED_NOT_FULL_TEXTURE_APPROVAL')
