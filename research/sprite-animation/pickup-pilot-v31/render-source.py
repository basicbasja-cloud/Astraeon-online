"""Fresh external CC0 KayKit PickUp source, fixed-camera poses and named joints.
No rejected own motion/rig inputs. Exports actual deformed meshes/owner colors.
"""
import bpy,math,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(exist_ok=True,parents=True)
source=Path('research/sprite-animation/joint-tracking-ro-v30/preset-source/Rig_Medium_General.glb');bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(source));rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=True
choices=[ac for ac in bpy.data.actions if ac.name in ('PickUp','PickUp_'+rig.name)];assert len(choices)==1;action=choices[0];rig.animation_data.action=action
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=384;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='Standard'
scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=3.5;cam.location=(6,-9,5.5);cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler()
for loc,energy in [((3,-5,8),800),((-4,1,5),350)]:
 light=bpy.data.lights.new('Light','AREA');light.energy=energy;light.size=4;o=bpy.data.objects.new('Light',light);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
# Preserve actual six external split meshes. Ownership names are source declarations.
meshes=[o for o in scene.objects if o.type=='MESH'];original={o.name:list(o.data.materials) for o in meshes}
for o in meshes:
 mat=bpy.data.materials.new('Owner_'+o.name);mat.diffuse_color=(.14,.52,1,1) if 'Right' in o.name else (1,.36,.03,1) if 'Left' in o.name else (.5,.53,.58,1);o.data.materials.clear();o.data.materials.append(mat)
JOINTS={'head':'head','chest':'chest','pelvis':'hips'}
for side,suffix in [('right','r'),('left','l')]:
 for label,bone in [('shoulder','upperarm'),('elbow','lowerarm'),('wrist','wrist'),('hip','upperleg'),('knee','lowerleg'),('ankle','foot'),('toe','toes')]:JOINTS[side+'.'+label]=bone+'.'+suffix
start,end=map(float,action.frame_range);frames=[]
# Uniform source intervals with terminal hold separately labelled. Not a loop.
for i in range(8):
 frame=start+(end-start)*i/7;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();file=a.out/f'{i:02}.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True);points={}
 for name,bone in JOINTS.items():
  world=rig.matrix_world@rig.pose.bones[bone].head;v=world_to_camera_view(scene,cam,world);points[name]={'xy':[v.x*384,(1-v.y)*512],'world_xyz':list(world),'source_bone':bone,'pixel_visibility':'unverified'}
 # Actual deformed mesh surfaces; support not inferred merely from minimum z.
 surfaces={}
 for o in meshes:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();vs=[ev.matrix_world@v.co for v in mesh.vertices];surfaces[o.name]={'min_z':min(v.z for v in vs),'max_z':max(v.z for v in vs)};ev.to_mesh_clear()
 frames.append({'index':i,'source_time_seconds':frame/30,'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'points':points,'mesh_z_extents':surfaces})
receipt={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'clip':'PickUp','source_action_range_frames':[start,end],'source_duration_ms':(end-start)/30*1000,'canvas':[384,512],'camera_world_matrix':[list(r) for r in cam.matrix_world],'ortho_scale':camdata.ortho_scale,'direction':'fixed front-three-quarter camera (semantic SE candidate, not approved game direction)','named_bones':{b.name:b.parent.name if b.parent else None for b in rig.data.bones},'mesh_owner_names':[o.name for o in meshes],'frames':frames,'loop':False,'old_own_rig_or_motion_used':False,'contact_approval':False,'production_pass':False};(a.out/'source.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SOURCE_RENDERED',len(frames))
