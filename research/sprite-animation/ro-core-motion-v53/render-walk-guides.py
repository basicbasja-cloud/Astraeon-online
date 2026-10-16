"""Reopen saved new source; 64 dressed and 64 isolated anatomical-owner guide captures."""
from pathlib import Path
import bpy,json,hashlib
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;blend=P/'source/walk.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;rig=bpy.data.objects['Astraeon_Free_Local'];sc.cycles.samples=2;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;meshes=[o for o in sc.objects if o.type=='MESH'];original={o.name:(o.hide_render,list(o.data.materials)) for o in meshes};records=[]
materials={}
for name,col in [('left',(1,.23,.025,1)),('right',(.025,.3,1,1))]:
 m=bpy.data.materials.new('v53.owner.'+name);m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=col;n=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],n.inputs['Surface']);materials[name]=m
for view in ['S','SW','W','NW','N','NE','E','SE']:
 sc.camera=bpy.data.objects[view]
 for i in range(8):
  sc.frame_set(1+8*i);bpy.context.view_layer.update();assert bpy.data.objects['collectible'].hide_render and bpy.data.objects['collectible'].animation_data is None;points={b.name:{'world':list(rig.matrix_world@b.head),'xy':list((lambda q:(q.x*384,(1-q.y)*512))(world_to_camera_view(sc,sc.camera,rig.matrix_world@b.head)))} for b in rig.pose.bones};paths={}
  for mode in ['full','leg-owner']:
   for o in meshes:
    hidden,mats=original[o.name];o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    o.hide_render=hidden
    if mode=='leg-owner':
     groups={g.name for g in o.vertex_groups};owners=[s for s in ['left','right'] if groups.intersection({s+'.'+b for b in ['thigh','shin','foot']})]
     if len(owners)>1:raise ValueError('Mixed side surface requires explicit adapter')
     o.hide_render=not owners or hidden
     if owners:
      for j in range(len(o.data.materials)):o.data.materials[j]=materials[owners[0]]
   f=P/'guides'/view/mode/f'{i:02}.png';f.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(f);bpy.ops.render.render(write_still=True);paths[mode]={'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
  records.append({'view':view,'index':i,'phase':i/8,'source_frame':1+8*i,'source_bones':points,'captures':paths});print('V53_CAPTURE',view,i,flush=True)
(P/'source/walk-capture-receipt.json').write_text(json.dumps({'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'frames':records,'camera':'Same physical saved cameras as v52 neutral guides','owner_colors':{'left':'orange','right':'blue'},'source_only':True,'isolated_guide_is_not_fullscene_visibility':True,'saved_after_material_changes':False},indent=2)+'\n')
