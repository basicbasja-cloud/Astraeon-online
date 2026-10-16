"""Fresh actual physical cameras and anatomical owner labels; never painted-anatomy proof."""
from pathlib import Path
import bpy,json,math,hashlib
P=Path(__file__).resolve().parent;d=json.loads((P/'source/retiming.json').read_text());blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;gem=bpy.data.objects['collectible'];gem.animation_data_clear();gem.hide_render=True;sc.cycles.samples=2;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;meshes=[o for o in sc.objects if o.type=='MESH'];original={o.name:list(o.data.materials) for o in meshes};materials={};records=[]
for side,col in [('left',(1,.23,.025,1)),('right',(.025,.3,1,1))]:
 m=bpy.data.materials.new('v55.owner.'+side);m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=col;n=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],n.inputs['Surface']);materials[side]=m
for view in ['S','W','E']:
 sc.camera=bpy.data.objects[view]
 for i,k in enumerate([0,2,4,6,8,10,12,15]):
  phase=d['views'][view]['frames'][k]['pose_phase'];tick=1+39*phase;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));gem.hide_render=True
  for o in meshes:
   groups={g.name for g in o.vertex_groups};sides=[s for s in ['left','right'] if groups.intersection({s+'.'+b for b in ['upperarm','forearm','hand','thigh','shin','foot']})];assert len(sides)<=1
   o.data.materials.clear()
   for m in original[o.name]:o.data.materials.append(m)
   if sides:
    for j in range(len(o.data.materials)):o.data.materials[j]=materials[sides[0]]
  f=P/'source'/view/'owners'/f'{i:02}.png';f.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(f);bpy.ops.render.render(write_still=True);records.append({'view':view,'key':i,'source_sample':k,'source_phase':phase,'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'source/owner-key-receipt.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'frames':records,'left':'orange','right':'blue','source_only':True,'not_final_painted_anatomy_approval':True,'physical_E_near':'RIGHT','physical_W_near':'LEFT','prop_action_cleared_and_hidden_every_capture':True},indent=2)+'\n')
