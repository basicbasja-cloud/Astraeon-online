"""Replay actual baked rig at fractional times, sample real soles and floor projection.

No source edits/saves, no inferred contact support. Includes dense between-key
sampling and final endpoint; exported art keys exclude duplicated endpoint.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--count',type=int,default=16);p.add_argument('--dense-count',type=int,default=129);p.add_argument('--view',choices=['E','W'],default='W')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.output.exists() or a.count<3 or a.dense_count<2:raise ValueError('Fresh output and valid sample counts required')
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;cam=scene.camera;rig=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot']
motion_path=a.blend.parent/'motion.json';motion=json.loads(motion_path.read_text());duration=motion['duration_seconds'];pivot.rotation_euler.z=math.radians({'E':90,'W':270}[a.view]);bpy.context.view_layer.update()
a.output.mkdir(parents=True);patches={}
for side in ['right','left']:
 for part in ['heel','toe']:
  name=f'sole.{side}.{part}';patches[name]=[v.index for v in bpy.data.objects[name].data.vertices if v.co.z<.003]
  if not patches[name]:raise ValueError('Missing source sole patch')
def xy(point):
 v=world_to_camera_view(scene,cam,point);return [v.x*512,(1-v.y)*512]
def sample(t,index):
 pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 q=t/duration*(len(motion['frames'])-1);lo=min(int(q),len(motion['frames'])-1);hi=min(lo+1,len(motion['frames'])-1);mix=q-lo
 travel=Vector(motion['frames'][lo]['root_world']).lerp(Vector(motion['frames'][hi]['root_world']),mix);travel=pivot.matrix_world.to_3x3()@travel
 bones={}
 for name in ['root','pelvis','Head','thigh_r','calf_r','foot_r','ball_leaf_r','thigh_l','calf_l','foot_l','ball_leaf_l']:
  point=rig.matrix_world@rig.pose.bones[name].head;bones[name]={'world':list(point),'xy':xy(point)}
 soles={}
 for name,indices in patches.items():
  obj=bpy.data.objects[name].evaluated_get(deps);mesh=obj.to_mesh()
  try:
   points=[obj.matrix_world@v.co for v in mesh.vertices];lowest=min(range(len(points)),key=lambda j:points[j].z);point=points[lowest];floor=Vector((point.x,point.y,0))
   soles[name]={'minimum_mesh_z':point.z,'lowest_vertex_index':lowest,'lowest_vertex_world_in_place':list(point),'lowest_vertex_world_traveled':list(point+travel),'lowest_xy':xy(point),'same_xy_on_ground_world':list(floor),'same_xy_on_ground_projected':xy(floor),
      'vertical_clearance_projected_px':xy(floor)[1]-xy(point)[1],
      'near_plane_candidate':point.z<=.004,'support_verified':False}
  finally:obj.to_mesh_clear()
 return {'key':index,'time_seconds':t,'source_sample_position':q,'root_travel_world':list(travel),'bones':bones,'soles':soles,'both_feet_airborne_candidate':min(s['minimum_mesh_z'] for s in soles.values())>.015}
dense=[sample(i*duration/(a.dense_count-1),i) for i in range(a.dense_count)];frames=[sample(i*duration/a.count,i) for i in range(a.count)]
# Diagnostic source render only. Source slot ownership follows real vertex groups.
materials={}
for side,color in [('r',(.03,.35,1,1)),('l',(1,.35,.02,1)),('other',(.5,.5,.5,1))]:
 m=bpy.data.materials.new('ground-guide.'+side);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=color;n.inputs['Roughness'].default_value=.85;materials[side]=m
meshes=[o for o in scene.objects if o.type=='MESH'];owners={}
for o in meshes:
 groups={g.name for g in o.vertex_groups};sides=[s for s in ['r','l'] if groups.intersection({n+'_'+s for n in ['thigh','calf','foot','ball','ball_leaf']})]
 if len(sides)>1:raise ValueError('Mixed source-side mesh')
 side=sides[0] if sides else 'other';owners[o.name]=side;o.data.materials.clear();o.data.materials.append(materials[side])
scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=False;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.use_nodes=False;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
for f in frames:
 sample(f['time_seconds'],f['key']);directory=a.output/f"{f['key']:02}";directory.mkdir()
 for mode in ['dressed','cutaway']:
  for o in meshes:o.hide_render=(o.get('slot')=='hair.auburn') if mode=='dressed' else owners[o.name]=='other'
  scene.render.filepath=str((directory/(mode+'.png')).resolve());bpy.ops.render.render(write_still=True)
  f[mode+'_path']=str(directory/(mode+'.png'));f[mode+'_sha256']=hashlib.sha256((directory/(mode+'.png')).read_bytes()).hexdigest()
report={'schema':'source-ground-walk-v1','blend_path':str(a.blend),'blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'motion_path':str(motion_path),'motion_sha256':hashlib.sha256(motion_path.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'facing':a.view,'canvas':[512,512],'duration_seconds':duration,'camera_matrix_world':[list(r) for r in cam.matrix_world],'camera_ortho_scale':cam.data.ortho_scale,'ground_world_z':0,'near_plane_tolerance_world':.004,'airborne_candidate_tolerance_world':.015,'source_pose_edited':False,'frames':frames,'dense_samples':dense,'summary':{'samples':len(dense),'exported_frames':len(frames),'both_feet_airborne_candidates':sum(f['both_feet_airborne_candidate'] for f in dense),'minimum_sole_z':min(s['minimum_mesh_z'] for f in dense for s in f['soles'].values()),'near_plane_coverage':sum(any(s['near_plane_candidate'] for s in f['soles'].values()) for f in dense)/len(dense)},'scope':'Actual evaluated sole vertices/floor projection at fractional source times. Height candidates do not establish support, balance, contact intervals or world-space foot-lock.'}
(a.output/'source-ground.json').write_text(json.dumps(report,indent=2)+'\n');print('GROUND_WALK',report['summary'])
