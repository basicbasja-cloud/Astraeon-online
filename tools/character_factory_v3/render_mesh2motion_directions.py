"""Capture the baked source-rig attack in eight real views at one shared scale."""
import argparse,json,math,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image,ImageDraw

DIRECTIONS=[('S',0),('SW',-45),('W',-90),('NW',-135),('N',180),('NE',135),('E',90),('SE',45)]

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--scene',required=True);ap.add_argument('--output',required=True);ap.add_argument('--size',type=int,default=1024);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
 bpy.ops.wm.open_mainfile(filepath=str(Path(args.scene).resolve()));out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
 sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');camera=sc.camera
 sc.render.resolution_x=sc.render.resolution_y=args.size;sc.render.resolution_percentage=100
 sc.frame_set(sc.frame_start);bpy.context.view_layer.update();anchor=rig.matrix_world@rig.pose.bones['root'].head
 camera_frames=[]
 for name,yaw in DIRECTIONS:
  r=math.radians(yaw);offset=Vector((6*math.sin(r),-6*math.cos(r),3.1));rotation=(-offset).to_track_quat('-Z','Y').to_euler();right=rotation.to_matrix()@Vector((1,0,0));up=rotation.to_matrix()@Vector((0,1,0));camera_frames.append((name,offset,rotation,right,up))
 mins={n:[float('inf'),float('inf')] for n,*_ in camera_frames};maxs={n:[-float('inf'),-float('inf')] for n,*_ in camera_frames}
 for f in range(sc.frame_start,sc.frame_end+1):
  sc.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();cloud=[]
  for obj in bpy.data.objects:
   if obj.type!='MESH' or obj.hide_render:continue
   ev=obj.evaluated_get(deps);mesh=ev.to_mesh();coords=np.empty(len(mesh.vertices)*3,dtype=np.float64);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3);matrix=np.array(ev.matrix_world,dtype=float);cloud.append(coords@matrix[:3,:3].T+matrix[:3,3]);ev.to_mesh_clear()
  points=np.concatenate(cloud)-np.array(anchor)
  for name,_,_,right,up in camera_frames:
   xy=points@np.array([right,up]).T
   for axis in (0,1):mins[name][axis]=min(mins[name][axis],float(xy[:,axis].min()));maxs[name][axis]=max(maxs[name][axis],float(xy[:,axis].max()))
 # Root at 0.825 of cell height; keep 5% margins in every view and pose.
 scale=max(max(2*max(abs(mins[n][0]),abs(maxs[n][0]))/.9,maxs[n][1]/.775,-mins[n][1]/.125) for n,*_ in camera_frames)
 camera.data.ortho_scale=scale;views=[];all_thumbs={};count=sc.frame_end-sc.frame_start+1
 for name,offset,rotation,right,up in camera_frames:
  folder=out/name;folder.mkdir(exist_ok=True);camera.rotation_euler=rotation;camera.location=anchor+up*(.325*scale)+offset
  records=[];thumbs=[]
  for f in range(sc.frame_start,sc.frame_end+1):
   sc.frame_set(f);bpy.context.view_layer.update();path=folder/f'{f-sc.frame_start:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
   def project(point):
    p=world_to_camera_view(sc,camera,point);return [round(p.x*args.size,4),round((1-p.y)*args.size,4)]
   bones=rig.pose.bones
   records.append({'frame':f,'image':str(path.relative_to(out)),'landmarks':{b:project(rig.matrix_world@bones[b].head) for b in ['root','head','pelvis','hand_r','hand_l','foot_l','foot_r']}})
   im=Image.open(path).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS);bg=Image.new('RGBA',im.size,'#ececec');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
  durations=[round((i+1)*100/60)*10-round(i*100/60)*10 for i in range(count)];durations[-1]=300
  thumbs[0].save(out/f'{name}-one-shot.gif',save_all=True,append_images=thumbs[1:],duration=durations,disposal=2,optimize=False)
  sheet=Image.new('RGB',(1280,1920),'#ececec');d=ImageDraw.Draw(sheet)
  for n,f in enumerate([round(i*(count-1)/23) for i in range(24)]):
   x,y=n%4*320,n//4*320;sheet.paste(thumbs[f],(x,y));d.text((x+5,y+5),f'{name} / {f}',fill='black')
  sheet.save(out/f'{name}-contact.png');all_thumbs[name]=thumbs;views.append({'direction':name,'yaw_degrees':dict(DIRECTIONS)[name],'camera_location':list(camera.location),'camera_rotation':list(rotation),'frames':records})
  print('DIRECTION_COMPLETE',name,flush=True)
 combined=[]
 for f in range(count):
  im=Image.new('RGB',(1280,688),'#ececec');d=ImageDraw.Draw(im)
  for i,(name,_) in enumerate(DIRECTIONS):
   x,y=i%4*320,i//4*344;im.paste(all_thumbs[name][f],(x,y+24));d.text((x+5,y+5),name,fill='black')
  combined.append(im)
 combined[0].save(out/'eight-directions-one-shot.gif',save_all=True,append_images=combined[1:],duration=durations,disposal=2,optimize=False)
 manifest={'source_scene':str(Path(args.scene).resolve()),'frame_count':count,'fps':60,'view_order':[n for n,_ in DIRECTIONS],'mirroring':False,'shared_ortho_scale':scale,'source_resolution':args.size,'initial_root_pixel':[args.size*.5,args.size*.825],'root_motion':'original source displacement; no per-frame camera following','camera_fit':'union of evaluated mesh vertices over all frames and all eight angles, single shared scale','views':views}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
