"""Replace the fused, fragmented source cape with a continuous fitted cloth.

Retains the supplied textured body/head, its rest proportions, and the fitted
rig. Concealed torso caps remain in BodyOutfit. Original FBX is untouched.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']]
old=bpy.data.objects['F01_Cape'];old.name='REFERENCE_FusedCape';old.hide_render=True;old.hide_set(True);del old['spriteModule'];old['referenceOnly']=True
def paint(name,color):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    geometry=nodes.new('ShaderNodeNewGeometry');dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=Vector((-.35,-.65,.68)).normalized();links.new(geometry.outputs['Normal'],dot.inputs[0])
    maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';maximum.inputs[1].default_value=0;links.new(dot.outputs['Value'],maximum.inputs[0])
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=.22;links.new(maximum.outputs[0],multiply.inputs[0])
    add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.78;links.new(multiply.outputs[0],add.inputs[0])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=(*color,1);links.new(add.outputs[0],mix.inputs[2])
    emission=nodes.new('ShaderNodeEmission');links.new(mix.outputs[0],emission.inputs['Color'])
    out=nodes.new('ShaderNodeOutputMaterial');links.new(emission.outputs[0],out.inputs['Surface']);mat['factoryPaintShader']=True;return mat
gold=paint('F01_ContinuousCapeGold',(.55,.31,.072));ivory=paint('F01_CapeIvory',(.91,.84,.66))
def point(u,t,offset=0):
    width=.115+.19*math.sin(t*1.15)
    return Vector((u*width,.086-.020*t+.007*math.cos(u*math.tau+t*.5)+offset,.745-.32*t-.05*(abs(u)**4)*(t**3)))
def bind(obj):
    obj.parent=rig;obj['spriteModule']='Cape'
    groups=[obj.vertex_groups.new(name='Cape'+str(j)) for j in range(3)]
    for v in obj.data.vertices:
        k=max(0,min(2,(.729-v.co.z)/.112));j=int(k);groups[j].add([v.index],1-k+j,'REPLACE')
        if j<2 and k>j:groups[j+1].add([v.index],k-j,'REPLACE')
    m=obj.modifiers.new('ClothBones','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat)
    obj=bpy.data.objects.new(name,me);s.collection.objects.link(obj);bind(obj);return obj
rows=25;cols=25;verts=[];faces=[]
for r in range(rows):
    for c in range(cols):verts.append(point(c/(cols-1)*2-1,r/(rows-1)))
for r in range(rows-1):
    for c in range(cols-1):a=r*cols+c;faces.append((a,a+1,a+1+cols,a+cols))
cape=mesh('F01_Cape',verts,faces,gold)
uv=cape.data.uv_layers.new(name='CapeSourceBake')
for polygon in cape.data.polygons:
    for li in polygon.loop_indices:
        vi=cape.data.loops[li].vertex_index;uv.data[li].uv=(vi%cols/(cols-1),1-vi//cols/(rows-1))
for p in cape.data.polygons:p.use_smooth=True
solid=cape.modifiers.new('ClothThickness','SOLIDIFY');solid.thickness=.0028;solid.offset=0
sub=cape.modifiers.new('ClothSurface','SUBSURF');sub.levels=1;sub.render_levels=1
# Original ASTRAEON lightning border, laid on the same cloth surface; not cards.
def ribbon(name,coordinates,width,offset):
    verts=[];faces=[]
    for j,(u,t) in enumerate(coordinates):
        a=Vector(coordinates[max(0,j-1)]);b=Vector(coordinates[min(len(coordinates)-1,j+1)]);d=(b-a).normalized()
        perp=Vector((-d.y,d.x))*width
        for sign in [-1,1]:p=Vector((u,t))+perp*sign;verts.append(point(p.x,p.y,offset))
    for j in range(len(coordinates)-1):faces.append((j*2,j*2+1,j*2+3,j*2+2))
    obj=mesh(name,verts,faces,ivory)
    sub=obj.modifiers.new('BorderDensity','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;sub.render_levels=2
for side in [-1,1]:
    ribbon('F01_LightningBorder_'+str(side),[(side*.97,.64),(side*.72,.69),(side*.88,.79),(side*.54,.81),(side*.75,.92),(side*.94,.95)],.018,-.0025)
    ribbon('F01_BackLightning_'+str(side),[(side*.94,.92),(side*.61,.91),(side*.38,.82),(side*.23,.93)],.015,.0025)
ribbon('F01_BackChevron',[(-.55,.97),(0,.77),(.55,.97)],.016,.0025)
s['capeConstruction']='Continuous quad cloth fitted to source dimensions; original geometric lightning ornament; 3 cloth bones.'
base=Path(__file__).resolve().parents[1]
# Bake supplied paint from its original UVs onto the reconstructed cloth through
# Blender's selected-to-active surface baker. No invented image tiles or UV seam
# interpolation. The donor stays in its bind pose, and the source file is intact.
source=old;rig.data.pose_position='REST'
solid.show_viewport=False;solid.show_render=False;sub.show_viewport=False;sub.show_render=False
source.hide_render=False;source.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');source.select_set(True);cape.select_set(True);bpy.context.view_layer.objects.active=cape
image=bpy.data.images.new('F01_CapeOriginalPaint',width=1024,height=1024,alpha=True);image.generated_color=(.55,.31,.072,1)
node=gold.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;gold.node_tree.nodes.active=node
engine=s.render.engine;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.device='CPU'
s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=.045;s.render.bake.max_ray_distance=.15;s.render.bake.use_clear=False;s.render.bake.margin=4
bpy.ops.object.bake(type='EMIT')
texture_dir=base/'authoring/characters/swordsman-production/fantasy-base-01/textures';texture_dir.mkdir(parents=True,exist_ok=True)
image.filepath_raw=str(texture_dir/'cape-source-bake.png');image.file_format='PNG';image.save();image.pack()
mix=next(n for n in gold.node_tree.nodes if n.type=='MIX_RGB');gold.node_tree.links.new(node.outputs['Color'],mix.inputs[1])
s.render.engine=engine;source.hide_render=True;source.hide_set(True);rig.data.pose_position='POSE'
solid.show_viewport=True;solid.show_render=True;sub.show_viewport=True;sub.show_render=True
s['capeTextureProvenance']='Blender EMIT selected-to-active bake from isolated original cape UV polygons and concealed gold caps; reconstructed cloth UVs.'
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parents[1]/'.character-tools/checkpoints/fantasy-base-01-fitted.blend'))
print('FANTASY_CONTINUOUS_CAPE_CREATED',flush=True)
