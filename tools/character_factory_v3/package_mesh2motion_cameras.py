"""Add exact per-view weapon metadata and eight fixed cameras to the baked scene."""
import argparse,copy,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--guide',required=True,type=Path);ap.add_argument('--views',required=True,type=Path);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
 source=json.loads((args.guide/'manifest.json').read_text());multi=json.loads((args.views/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str((args.guide/'overhead-B-source-rig.blend').resolve()));sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');cameras={}
 for obj in list(bpy.data.objects):
  if obj.type=='CAMERA':bpy.data.objects.remove(obj,do_unlink=True)
 for view in multi['views']:
  name=view['direction'];data=bpy.data.cameras.new('CAM_'+name);camera=bpy.data.objects.new(data.name,data);sc.collection.objects.link(camera);data.type='ORTHO';data.ortho_scale=multi['shared_ortho_scale'];camera.location=view['camera_location'];camera.rotation_euler=view['camera_rotation'];cameras[name]=camera;sc.camera=camera
  frames=[]
  for i,old in enumerate(source['frames']):
   sc.frame_set(i);bpy.context.view_layer.update();bones=rig.pose.bones
   def point(p):
    v=world_to_camera_view(sc,camera,p);return [round(v.x*multi['source_resolution'],4),round((1-v.y)*multi['source_resolution'],4)]
   record=copy.deepcopy(old);record['image']=f'{i:03d}.png';record['landmarks']={n:point(rig.matrix_world@bones[n].head) for n in list(old['landmarks'])+['root']}
   ix=rig.matrix_world@bones['index_01_r'].head;pink=rig.matrix_world@bones['pinky_01_r'].head;grip=(ix+pink)*.5;axis=(ix-pink).normalized();record['sword_grip']=point(grip);record['sword_tip']=point(grip+axis*.8);record['world_sword_grip']=list(grip);record['world_sword_tip']=list(grip+axis*.8);frames.append(record)
   view['frames'][i]['landmarks']=record['landmarks'];view['frames'][i]['sword_grip']=record['sword_grip'];view['frames'][i]['sword_tip']=record['sword_tip']
  manifest=copy.deepcopy(source);manifest['direction']=name;manifest['frames']=frames;manifest['camera']={'location':list(camera.location),'rotation':list(camera.rotation_euler),'type':'ORTHO','scale':data.ortho_scale,'fit':'one shared scale over all eight real views','initial_root_pixel':multi['initial_root_pixel']};manifest['source_raster']='authoritative eight-direction capture, not the earlier approximately-SE single-camera study';(args.views/name/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 sc.camera=cameras['SE'];sc.frame_set(0);sc.render.filepath=str((args.views/'manual-preview.png').resolve());bpy.ops.wm.save_as_mainfile(filepath=str((args.views/'source-rig-eight-view-ready.blend').resolve()),compress=True)
 (args.views/'manifest.json').write_text(json.dumps(multi,indent=2)+'\n')
 print('EIGHT_FIXED_CAMERAS_PACKAGED')

if __name__=='__main__':main()
