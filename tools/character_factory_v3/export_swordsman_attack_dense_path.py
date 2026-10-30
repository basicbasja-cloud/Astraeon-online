"""Export native Sword_Attack grip/tip samples 11..15 in four locked cameras."""
import argparse,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/c297971fcef09188ff60/manifest.json'
DENSE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/long-dragging-sword-trail-20261024/dense-manifest.json'
DIRS=('SW','NW','NE','SE')

def main():
 import bpy
 from mathutils import Matrix
 from bpy_extras.object_utils import world_to_camera_view
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists() or a.output.is_symlink():raise ValueError('choose fresh output')
 guide=json.loads(GUIDE.read_text());dense=json.loads(DENSE.read_text());job=guide['job'];source=ROOT/job['source_file'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
 if digest!=job['source_sha256'] or job['source_actions']!=['Sword_Attack'] or dense['job']['source_sha256']!=digest or job['resolution']!=1536:raise ValueError('unexpected source')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));sc=bpy.context.scene;rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
 if rig.parent is not None:raise ValueError('unexpected rig parent')
 for track in rig.animation_data.nla_tracks:track.mute=True
 action=bpy.data.actions.get('Sword_Attack_'+rig.name)
 if action is None:raise ValueError('missing action')
 rig.animation_data.action=action
 if hasattr(rig.animation_data,'action_slot') and action.slots:rig.animation_data.action_slot=action.slots[0]
 sc.render.resolution_x=sc.render.resolution_y=1536;sc.render.resolution_percentage=100
 camera_data=bpy.data.cameras.new('AttackStudyCamera');camera=bpy.data.objects.new('AttackStudyCamera',camera_data);sc.collection.objects.link(camera);sc.camera=camera;camera_data.type='ORTHO';views={};max_error=0.
 for direction in DIRS:
  reference=guide['views'][direction];dc=dense['views'][direction]
  if reference['camera']!=dc['camera']:raise ValueError('camera mismatch')
  camera.location=reference['camera']['location'];camera.rotation_euler=reference['camera']['rotation'];camera_data.ortho_scale=reference['camera']['ortho_scale'];bpy.context.view_layer.update();records=[]
  def project(v):
   q=world_to_camera_view(sc,camera,v);return [round(q.x*1536,4),round((1-q.y)*1536,4)]
  for i in range(65):
   t=11+i/16;sc.frame_set(math.floor(t),subframe=t%1);rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
   ix=rig.matrix_world@rig.pose.bones['index_01_r'].head;pk=rig.matrix_world@rig.pose.bones['pinky_01_r'].head;grip=(ix+pk)*.5;axis=(ix-pk).normalized();tip=grip+axis*.8;g=project(grip);h=project(tip)
   expected=dc['frames'][i]['weapon_guide'] if i<=32 else reference['frames'][8 if i==48 else 9]['weapon_guide'] if i in (48,64) else None
   if expected:
    error=max(math.dist(g,expected['grip']),math.dist(h,expected['tip']));max_error=max(max_error,error)
    if error>.01:raise ValueError(f'source projection mismatch {direction} {t}: {error}')
   records.append({'source_frame':t,'grip':g,'tip':h,'world_grip':list(grip),'world_tip':list(tip)})
  views[direction]=records
 result={'status':'DENSE_SOURCE_PATH_NOT_TRAIL_APPROVAL','source_sha256':digest,'guide_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),'prior_dense_sha256':hashlib.sha256(DENSE.read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sample_count_per_view':65,'max_checkpoint_projection_error_source_px':max_error,'views':views,
         'limitations':['Grip and tip use a finger-bone proxy, not verified blade geometry or artwork.', 'Camera projection and source sample positions do not prove trail timing, force, occlusion or visual correctness.', 'No 3D blade volume, source frame timing, gameplay or runtime approval.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('DENSE_ATTACK_PATH_EXPORTED',len(DIRS),'views',len(records),'samples',flush=True)
if __name__=='__main__':main()
