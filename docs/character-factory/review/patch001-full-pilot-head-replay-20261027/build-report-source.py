from pathlib import Path
from PIL import Image,ImageDraw
import shutil,json,hashlib
b=Path('authoring/characters/factory-v3/patch-0.0.1');o=Path('docs/character-factory/review/patch001-full-pilot-head-replay-20261027');o.mkdir(exist_ok=True);archer=b/'review/archer-remaining-view-head-complete-proposals-v6-20261027';mage=b/'review/mage-female-target-gaze-sequence-heads-v3-20261027';joints=b/'review/mage-female-24-source-joints-20261027';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['normal.gif','slow.gif','joint-contact.jpg','receipt.json']:shutil.copy2(joints/name,o/('mage-source-'+name))
shutil.copy2(mage/'head-contact.jpg',o/'mage-24-head-cutouts.jpg')
for i in range(4):shutil.copy2(archer/f'head-contact-{i:02d}.jpg',o/f'archer-head-contact-{i:02d}.jpg')
for kind,path in [('archer',Path('/workspace/archer-96-head-fresh-replay-20261027')),('mage',Path('/workspace/mage-24-head-fresh-replay-20261027'))]:shutil.copy2(path/'replay-receipt.json',o/f'{kind}-fresh-replay.json')
frames=[]
for i in range(16):
 canvas=Image.new('RGBA',(1152,768),'#ddd')
 for col,view in enumerate(['SW','NE','SE']):
  for row,sex in enumerate(['male','female']):
   master=Image.open(b/'review/archer-coherent-recovery-masters-v2-20261026'/sex/view/'Master'/f'{i:03d}.png').convert('RGBA');tile=master.crop((96,64,480,448));canvas.alpha_composite(tile,(col*384,row*384));head=Image.open(archer/sex/view/f'{i:03d}.png').convert('RGBA');box=head.getbbox();cx=(box[0]+box[2])//2;cy=(box[1]+box[3])//2;headtile=head.crop((cx-60,cy-60,cx+60,cy+60)).resize((120,120),Image.Resampling.NEAREST);canvas.alpha_composite(headtile,(col*384+254,row*384+24));ImageDraw.Draw(canvas).text((col*384+5,row*384+5),f'{sex} {view} {i:02d} / OWNERSHIP DRAFT',fill='black')
 frames.append(canvas.convert('RGB'))
for name,factor in [('normal',1),('slow',3)]:frames[0].save(o/f'archer-six-view-head-{name}.gif',save_all=True,append_images=frames[1:],duration=[80*factor]*15+[240*factor],loop=0,disposal=2,optimize=False)
measure={'status':'PILOT_SOURCE_AND_PART_REPLAY_CHECKPOINT_NOT_PATCH_COMPLETION','coverage':{'logical_action_instances':114,'paint_jobs':96,'technically_imported_jobs':2,'new_complete_characters':0,'required_complete_characters':6},'archer_remaining_view_head_frames':96,'mage_sw_head_frames':24,'same_frame_visible_rgba_replayed_parts':240,'head_proposals_semantically_approved_as_full_variants':False,'bodyrest_still_contains_weapon':True,'source_skeleton_exported_bones_per_pose':66,'source_skeleton_replay_compared_recorded_joints_per_pose':7,'source_camera_projection_checked_joints_per_pose':6,'source_projection_max_error_author768':max(max(r['source_projection_error_author768'].values())for r in json.loads((joints/'receipt.json').read_text())['frames']),'mage_raw_paintings_available':24,'mage_raw_art_approved':False,'shared_head_preview_rejected_for_exposed_neck_and_old_head_residue':True,'production_gaze_fit_adopted':False,'runtime_admitted':False,'image_generation_model_and_seed_not_exposed':True,'reproduction_from_saved_raw_and_editable_ownership_labels':True,'gif_timing':{'mage':'24fps sample cadence quantized to GIF centiseconds, final200ms review hold; review restarts are not game transitions','archer':'80ms per recorded pose plus240ms terminal review hold; this is review timing, not gameplay timing'}}
(o/'measurements.json').write_text(json.dumps(measure,indent=2)+'\n');(o/'build-report-source.py').write_bytes(Path(__file__).read_bytes())
