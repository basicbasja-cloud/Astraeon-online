"""Actual arm surface visibility with and without physical occluders.
Orange LEFT arm only, opaque black other meshes. Never overlay hidden parts.
"""
import bpy,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;blend=P/'original-character.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.cycles.samples=1
views=['S','SE','E','NE','N','NW','W','SW'];meshes=[o for o in sc.objects if o.type=='MESH'];arms=[o for o in meshes if o.name.startswith(('left.continuous_arm','left.shoulder_plate','left.shoulder_rim','left.glove','left.knuckles','left.thumb','left.bracer_band'))]
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);return m
target_collection=bpy.data.collections.new('ActualLeftArmTarget');sc.collection.children.link(target_collection)
occluder_collection=bpy.data.collections.new('ActualOtherMeshOccluders');sc.collection.children.link(occluder_collection)
for obj in meshes:
 for col in list(obj.users_collection):col.objects.unlink(obj)
 (target_collection if obj in arms else occluder_collection).objects.link(obj)
orange=material('Actual canonical LEFT arm',(1,.30,.01));black=material('Physical occluder',(0,0,0))
for o in meshes:
 o.data.materials.clear();o.data.materials.append(orange if o in arms else black)
 for p in o.data.polygons:p.material_index=0
records=[]
for i in range(8):
 tick=1+39*i/7;sc.frame_set(int(tick),subframe=tick-int(tick));hidden={o.name:o.hide_render for o in meshes}
 for view in views:
  sc.camera=bpy.data.objects[view];paths={}
  for kind in ['depth_tested','isolated']:
   occluder_collection.hide_render=(kind=='isolated')
   folder=P/'arm-visibility'/kind/view;folder.mkdir(parents=True,exist_ok=True);p=folder/f'{i:02}.png';sc.render.filepath=str(p);bpy.ops.render.render(write_still=True);paths[kind]=dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  records.append(dict(index=i,view=view,images=paths))
 for o in meshes:o.hide_render=hidden[o.name]
(P/'arm-visibility-receipt.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),arm_mesh_names=[o.name for o in arms],scope='Source geometry only. Full-scene occlusion is respected; isolated pass is disclosed reference only. Hidden surfaces are not drawn over the actor and cannot receive image-anatomy approval.',frames=records,production_pass=False),indent=2)+'\n');print('ARM_VISIBILITY_CAPTURED',len(records)*2)
