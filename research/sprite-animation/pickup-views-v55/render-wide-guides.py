"""Widen the source viewport without changing physical pixel scale; preserve original captures as negatives."""
from pathlib import Path
import bpy,json,math,hashlib
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;d=json.loads((P/'source/retiming.json').read_text());blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;rig=bpy.data.objects['Astraeon_Free_Local'];gem=bpy.data.objects['collectible'];gem.animation_data_clear();gem.hide_render=True;sc.cycles.samples=2;sc.render.resolution_x=768;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;meshes=[o for o in sc.objects if o.type=='MESH'];original={o.name:list(o.data.materials) for o in meshes};materials={};records=[];max_error=0
for side,col in [('left',(1,.23,.025,1)),('right',(.025,.3,1,1))]:
 m=bpy.data.materials.new('v55.wide-owner.'+side);m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=col;n=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],n.inputs['Surface']);materials[side]=m
for view in ['S','W','E']:
 sc.camera=bpy.data.objects[view];sc.camera.data.ortho_scale=3.75
 for i,row in enumerate(d['views'][view]['frames']):
  tick=1+39*row['pose_phase'];sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));gem.hide_render=True;bpy.context.view_layer.update()
  for name,b in rig.pose.bones.items():
   for edge in ['head','tail']:
    q=world_to_camera_view(sc,sc.camera,rig.matrix_world@getattr(b,edge));old=row['source_bones'][name][edge]['xy'];max_error=max(max_error,abs(q.x*768-old[0]-192),abs((1-q.y)*512-old[1]))
  assert max_error<.001,('Physical pixel scale changed',max_error)
  for mode in ['full','owners']:
   if mode=='owners' and i not in [0,2,4,6,8,10,12,15]:continue
   for o in meshes:
    o.data.materials.clear()
    for m in original[o.name]:o.data.materials.append(m)
    if mode=='owners':
     groups={g.name for g in o.vertex_groups};sides=[s for s in ['left','right'] if groups.intersection({s+'.'+b for b in ['upperarm','forearm','hand','thigh','shin','foot']})];assert len(sides)<=1
     if sides:
      for j in range(len(o.data.materials)):o.data.materials[j]=materials[sides[0]]
   f=P/'source/wide'/view/mode/f'{i:02}.png';f.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(f);bpy.ops.render.render(write_still=True);a=np.array(Image.open(f))[:,:,3]>=128;y,x=np.where(a);box=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];assert box[0]>0 and box[1]>0 and box[2]<768 and box[3]<512,('Source clipping',view,i,mode,box);records.append({'view':view,'sample':i,'mode':mode,'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'alpha128_bbox':box})
(P/'source/wide-capture-receipt.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'canvas':[768,512],'ortho_scale':3.75,'original_canvas':[384,512],'original_ortho_scale':2.5,'expected_projection_translation':[192,0],'maximum_projection_error_px':max_error,'captures':records,'source_only':True,'prop_action_cleared_and_hidden':True,'original_clipped_inputs_preserved':True},indent=2)+'\n')
