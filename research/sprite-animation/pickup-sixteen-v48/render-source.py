"""Read unchanged saved v45 rig at new times; never rerun historical builders."""
import bpy,json,hashlib,math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
blend=P/'source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend))
sc=bpy.context.scene;sc.camera=bpy.data.objects['N'];sc.cycles.samples=8
sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True
rig=bpy.data.objects['Astraeon_Free_Local'];gem=bpy.data.objects['collectible']
SAMPLES=[.5,1.5,2.5,3.5,4.5,5.5,6+1/3,6+2/3]
def points(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();p=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return p
sc.frame_set(1);feet={o.name:points(o) for o in sc.objects if o.type=='MESH' and o.name.endswith(('.sole','.boot','.boot_seam'))}
records=[]
for i,key in enumerate(SAMPLES):
 t=key/7;tick=1+39*t;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));bpy.context.view_layer.update()
 data={}
 for side in ['left','right']:
  for part,a,b in [('upperarm','shoulder','elbow'),('forearm','elbow','wrist'),('hand','wrist','palm'),('thigh','hip','knee'),('shin','knee','ankle'),('foot','ankle','toe')]:
   bone=rig.pose.bones[side+'.'+part]
   for label,point in [(a,rig.matrix_world@bone.head),(b,rig.matrix_world@bone.tail)]:
    q=world_to_camera_view(sc,sc.camera,point);data[side+'.'+label]={'world':list(point),'projected_raw':[q.x*384,(1-q.y)*512]}
 drift=max((a-b).length for name,base in feet.items() for a,b in zip(points(bpy.data.objects[name]),base))
 folder=P/'source/raw-midpoints';folder.mkdir(parents=True,exist_ok=True);path=folder/f'{i:02}.png'
 sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 records.append({'index':i,'source_key_fraction':key,'phase':t,'scene_frame':tick,'source_bones':data,'actual_foot_vertex_max_world_drift':drift,'gem_world':list(gem.location),'gem_visible':not gem.hide_render,'image':str(path.relative_to(P)),'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(P/'source/receipt.json').write_text(json.dumps({'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'camera_matrix':[list(r) for r in sc.camera.matrix_world],'ortho_scale':sc.camera.data.ortho_scale,'frames':records,'production_pass':False,'scope':'Actual new subframe evaluations of saved source, not interpolated paintings or painted joints'},indent=2)+'\n')
print('V48_SOURCE_RENDERED',len(records))
