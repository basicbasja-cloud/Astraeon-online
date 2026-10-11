"""Native free-hair comparison; inactive until it earns an internal likeness fit."""
import bpy,math,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
donor=bpy.data.scenes['ASTRAEON_VROID_FUMIRIYA_INSPECTION'];source=next(o for o in donor.objects if o.name=='Hair001')
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05'];existing=bpy.data.objects.get(p+'FumiriyaHairComparison')
if existing:bpy.data.objects.remove(existing,do_unlink=True)
obj=source.copy();obj.data=source.data.copy();obj.modifiers.clear();obj.name=p+'FumiriyaHairComparison';s.collection.objects.link(obj);obj.parent=root;obj.matrix_basis=Matrix.Identity(4)
old=Vector((-.00075,-.049,1.768));new=Vector((.0553,-.045,1.601));canonical=Matrix.Rotation(math.pi,3,'Z');turn=Matrix.Rotation(math.radians(-20),3,'Z')
for v in obj.data.vertices:
    d=canonical@v.co-old;d=Vector((d.x*1.45,d.y*1.30,d.z*1.45));v.co=new+turn@d
obj.data.update()
for i,original in enumerate(list(obj.data.materials)):
    if original is None:continue
    mat=original.copy();mat.name='Anatomy05_FumiriyaHairSilver_'+str(i);obj.data.materials[i]=mat;nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tex=next(n for n in nodes if n.type=='TEX_IMAGE');bw=nodes.new('ShaderNodeRGBToBW');ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='LINEAR'
    colors=[(0,(.07,.045,.09)),(.03,(.20,.14,.24)),(.10,(.41,.31,.45)),(.22,(.67,.55,.69)),(.4,(.88,.79,.90)),(1,(.98,.96,1))]
    for j,(position,color) in enumerate(colors):
        element=ramp.color_ramp.elements[j] if j<2 else ramp.color_ramp.elements.new(position);element.position=position;element.color=(*color,1)
    for link in list(tex.outputs['Color'].links):links.new(ramp.outputs[0],link.to_socket)
    links.new(tex.outputs['Color'],bw.inputs[0]);links.new(bw.outputs[0],ramp.inputs[0])
    if tex.image:tex.image.pack()
hair=[o for o in s.objects if o.name.startswith(p+'Hair_')];hidden={o:o.hide_render for o in hair}
for o in hair:o.hide_render=True
saved=(root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
try:
    s.render.resolution_x=1280;s.render.resolution_y=1280;obj.hide_render=False
    for d,yaw in [('SE',45),('W',-90)]:
        root.rotation_euler.z=math.radians(yaw);s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'+d+'-fumiriya-hair-comparison.png';bpy.ops.render.render(write_still=True)
finally:
    for o,state in hidden.items():o.hide_render=state
    obj.hide_render=True;root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath=saved
obj['license']='Sakurada Fumiriya / pixiv Inc. / CC0-1.0';obj['comparisonOnly']=True
print('FREE_NATIVE_HAIR_COMPARISON_RENDERED; INACTIVE_IN_SOURCE')
