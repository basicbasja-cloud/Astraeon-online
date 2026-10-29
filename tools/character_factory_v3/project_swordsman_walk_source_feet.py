"""Project previously sampled source foot-skin vertices into the locked SW guide."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'
FEET=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-source-feet-20261029/receipt.json'

def main():
 import bpy
 from mathutils import Vector
 from bpy_extras.object_utils import world_to_camera_view
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists() or a.output.is_symlink():raise ValueError('choose fresh output')
 guide=json.loads(GUIDE.read_text());feet=json.loads(FEET.read_text());view=guide['views']['SW'];size=guide['job']['resolution']
 if feet['guide_sha256']!=hashlib.sha256(GUIDE.read_bytes()).hexdigest() or len(feet['frames'])!=len(view['frames']) or size!=1536:raise ValueError('mismatched source')
 bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=size;scene.render.resolution_percentage=100
 data=bpy.data.cameras.new('SourceCamera');cam=bpy.data.objects.new('SourceCamera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=view['camera']['ortho_scale'];cam.location=view['camera']['location'];cam.rotation_euler=view['camera']['rotation'];bpy.context.view_layer.update()
 def project(v):
  q=world_to_camera_view(scene,cam,Vector(v));return [q.x*size,(1-q.y)*size]
 records=[]
 for foot,frame in zip(feet['frames'],view['frames']):
  if foot['frame']!=frame['frame'] or abs(foot['source_frame']-frame['source_frame'])>1e-5:raise ValueError('frame mismatch')
  for s in ('l','r'):
   p0=project(frame['world_landmarks']['foot_'+s]);p1=frame['landmarks']['foot_'+s]
   if max(abs(x-y) for x,y in zip(p0,p1))>.001:raise ValueError('camera projection mismatch')
  records.append({'frame':foot['frame'],'source_frame':foot['source_frame'],'feet':{s:{'vertex':foot['feet'][s]['lowest_vertex'],'source_guide_xy':project(foot['feet'][s]['world_xyz']),'world_xyz':foot['feet'][s]['world_xyz']} for s in ('l','r')}})
 result={'status':'SOURCE_SKIN_POINT_PROJECTION_NOT_CONTACT_APPROVAL','guide_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),'feet_sha256':hashlib.sha256(FEET.read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':records,
         'limitations':['The lowest weighted vertex may change between frames; projected point is not a proven painted contact landmark.', 'No automatic inference of sole, contact phase, game velocity, terrain or image acceptance.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('WALK_SOURCE_FEET_PROJECTED',len(records),'frames',flush=True)
if __name__=='__main__':main()
