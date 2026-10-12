"""Reopen actual accepted original rig; rotate geometry, never raster-mirror.

The quarter-cycle shift is an explicitly approximate RO phase correspondence.
Source poses/bones remain unchanged and do not recover hidden RO anatomy.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--phase-offset',type=int,default=12)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not a.out.exists(),'Fresh export required'
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;rig=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot'];cam=scene.camera
motion_path=a.blend.parent/'motion.json';motion=json.loads(motion_path.read_text());duration=motion['duration_seconds']
facings=['S','SE','E','NE','N','NW','W','SW'];keys=[(a.phase_offset+2*i)%16 for i in range(8)];meshes=[o for o in scene.objects if o.type=='MESH'];owners={}
colors={'r':(.025,.3,1,1),'l':(1,.28,.01,1),'other':(.35,.38,.42,1)};materials={}
for side,color in colors.items():
 m=bpy.data.materials.new('v20.owner.'+side);m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=color;o=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);materials[side]=m
for o in meshes:
 groups={g.name for g in o.vertex_groups};sides=[s for s in ['r','l'] if groups.intersection({n+'_'+s for n in ['thigh','calf','foot','ball','ball_leaf']})]
 if len(sides)>1:raise ValueError('Mixed anatomical mesh owner')
 side=sides[0] if sides else 'other';owners[o.name]={'side':side,'groups':sorted(groups),'slot':o.get('slot')};o.data.materials.clear();o.data.materials.append(materials[side])
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False;scene.cycles.device='CPU';scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.use_nodes=False;scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
a.out.mkdir(parents=True);records=[]
def xy(v):q=world_to_camera_view(scene,cam,v);return [q.x*512,(1-q.y)*512]
for facing in facings:
 pivot.rotation_euler.z=facings.index(facing)*math.pi/4
 for i,key in enumerate(keys):
  t=key/16*duration;pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
  bones={}
  for b in rig.pose.bones:
   point=rig.matrix_world@b.head;bones[b.name]={'world':list(point),'xy':xy(point),'camera_z':(cam.matrix_world.inverted()@point).z,'parent':b.parent.name if b.parent else None}
  soles={}
  for side in ['right','left']:
   for part in ['heel','toe']:
    name='sole.'+side+'.'+part;obj=bpy.data.objects[name].evaluated_get(deps);mesh=obj.to_mesh()
    try:
     pts=[obj.matrix_world@v.co for v in mesh.vertices];lowest=min(pts,key=lambda v:v.z);ground=Vector((lowest.x,lowest.y,0))
     soles[name]={'minimum_mesh_z':lowest.z,'lowest_xy':xy(lowest),'ground_projection_xy':xy(ground),'near_plane_candidate':lowest.z<=.004,'support_verified':False}
    finally:obj.to_mesh_clear()
  directory=a.out/facing/f'{i:02}';directory.mkdir(parents=True);paths={};hashes={}
  for mode in ['dressed-owner','cutaway-owner']:
   for o in meshes:o.hide_render=o.get('slot')=='hair.auburn' or (mode=='cutaway-owner' and owners[o.name]['side']=='other')
   path=directory/(mode+'.png');scene.render.filepath=str(path.resolve());bpy.ops.render.render(write_still=True);paths[mode]=str(path);hashes[mode]=hashlib.sha256(path.read_bytes()).hexdigest()
  records.append({'facing':facing,'key':i,'source_key16':key,'evaluated_time_seconds':t,'logical_time_seconds':i*duration/8,'bones':bones,'soles':soles,'paths':paths,'sha256':hashes})
  print('EIGHT_GAIT',facing,i,flush=True)
report={'schema':'original-eight-gait-source-v1','blend':{'path':str(a.blend),'sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest()},'motion':{'path':str(motion_path),'sha256':hashlib.sha256(motion_path.read_bytes()).hexdigest()},'active_action':rig.animation_data.action.name,'blender':bpy.app.version_string,'canvas':[512,512],'duration_seconds':duration,'facings':facings,'source_keys16':keys,'phase_correspondence':'Quarter-cycle source shift for approximate passing/swing/contact comparison; not recovered RO bones or exact painted bone fit','camera_matrix_world':[list(r) for r in cam.matrix_world],'camera_ortho_scale':cam.data.ortho_scale,'owners':owners,'records':records,'geometry_mirrored':False,'source_pose_edited':False,'source_saved':False,'other_views_user_approved':False}
(a.out/'source-index.json').write_text(json.dumps(report,indent=2)+'\n')
print('EXPORTED_ACTUAL_SOURCE',len(records),'poses,128owner renders; original source unchanged',flush=True)
