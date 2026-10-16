"""Isolated complete geometry is a drawing guide, not a segmentation/hidden-art proof."""
from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parent;parent=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(parent));sc=bpy.context.scene;sc.frame_set(1);gem=bpy.data.objects['collectible'];gem.animation_data_clear();gem.hide_render=True;sc.camera=bpy.data.objects['W'];sc.cycles.samples=4;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;meshes=[o for o in sc.objects if o.type=='MESH'];records=[]
def role(o):
 groups={g.name for g in o.vertex_groups};head=o.get('runtime_slot')=='complete_head';cape='cape' in o.name
 arms={s:bool(groups.intersection({s+'.'+b for b in ['upperarm','forearm','hand']})) for s in ['left','right']};legs={s:bool(groups.intersection({s+'.'+b for b in ['thigh','shin','foot']})) for s in ['left','right']};limb=any(arms.values()) or any(legs.values())
 return [head,not head and not limb,arms['left'],arms['right'],legs['left'],legs['right'],cape,not head and not limb and not cape]
for view in ['S','SW','NW','N','NE','E','SE']:
 sc.camera=bpy.data.objects[view]
 records=[]
 for i,name in enumerate(['complete_head','body_with_cape','left_arm','right_arm','left_leg','right_leg','cape','body_no_cape']):
  selected=[]
  for o in meshes:o.hide_render=o==gem or not role(o)[i];selected.extend([o.name] if not o.hide_render else [])
  f=P/'source'/f'{view}-{i:02}-{name}.png';sc.render.filepath=str(f);bpy.ops.render.render(write_still=True);records.append({'cell':i,'name':name,'objects':selected,'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 (P/'source'/f'{view}-rest-part-guide-receipt.json').write_text(json.dumps({'parent_blend_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'parts':records,'view':view+' physical camera','prop_hidden_and_action_cleared':True,'source_only':True,'not_final_art_or_inferred_hidden_anatomy':True},indent=2)+'\n')
