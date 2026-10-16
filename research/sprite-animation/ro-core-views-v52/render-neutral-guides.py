"""Eight physical cameras, one saved neutral pose; guide only."""
from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parent;blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.frame_set(1);bpy.data.objects['collectible'].hide_render=True;sc.cycles.samples=4;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;records=[]
for i,name in enumerate(['S','SW','W','NW','N','NE','E','SE']):
 sc.camera=bpy.data.objects[name];f=P/'source'/f'neutral-{name}.png';sc.render.filepath=str(f);bpy.ops.render.render(write_still=True);records.append({'index':i,'view':name,'camera_world':[list(r) for r in sc.camera.matrix_world],'ortho_scale':sc.camera.data.ortho_scale,'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'source/camera-receipts.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'external_motion_reference':False,'guide_only':True,'views':records},indent=2)+'\n')
