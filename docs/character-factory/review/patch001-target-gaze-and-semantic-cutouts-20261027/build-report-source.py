from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math,numpy as np,shutil
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'research/target-facing-mage-gaze-20261027';c=p/'four-view-capture';m=json.load(open(c/'manifest.json'));a=json.load(open(c/'target-gaze-proof.json'));o=Path('docs/character-factory/review/patch001-target-gaze-and-semantic-cutouts-20261027');o.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
target=np.array(a['profile']['reference_head_world_quaternion']);families=[]
for direction,v in m['views'].items():
 first=np.array(v['frames'][0]['landmarks']['head'])*.5;members=[]
 for f in v['frames']:
  q=np.array(f['bone_rotations']['head']);q/=np.linalg.norm(q);err=min(np.linalg.norm(q-target),np.linalg.norm(q+target))
  if err>3e-6:raise ValueError('Actual captured head orientation differs')
  anchor=np.array(f['landmarks']['head'])*.5;delta=anchor-first;rounded=np.rint(delta);members.append({'index':f['frame'],'source_action':f['action'],'source_frame':f['source_frame'],'head_anchor_author768':anchor.tolist(),'head_asset_translation_from_pose0_author_px':delta.tolist(),'proposed_integer_bake_translation':rounded.tolist(),'proposed_bake_anchor_error_author_px':float(np.linalg.norm(rounded-delta)),'world_quaternion_error':float(err),'image_sha256':sha(c/f['image'])})
 families.append({'direction':direction,'camera':v['camera'],'head_asset_reference_pose':0,'reference_anchor_author768':first.tolist(),'members':members})
proof={'status':'MEASURED_HEAD_ORIENTATION_FAMILIES_NOT_APPROVED_PAINTED_HEAD_REUSE','source_manifest_sha256':sha(c/'manifest.json'),'gaze_proof_sha256':sha(c/'target-gaze-proof.json'),'source_glb_sha256':m['job']['source_sha256'],'character_fit':m['job']['hero_fit_study'],'target_world_head_quaternion':target.tolist(),'source_pose_views':sum(len(x['members'])for x in families),'gaze_applications_including_prepass':len(a['applications']),'max_neck_counter_rotation_degrees':max(x['correction_degrees']for x in a['applications']),'max_protected_body_matrix_error':max(x['maximum_protected_body_matrix_error']for x in a['applications']),'protected_body_bones_per_application':min(x['protected_bone_count']for x in a['applications']),'max_head_position_error_m':max(x['head_position_error_m']for x in a['applications']),'max_actual_render_matrix_error_all66_bones':max(x['max_world_matrix_component_error']for f in m['render_pose_freeze']['rendered_frames']for x in f['actors']),'families':families,'painted_asset_reuse_requires':['same approved fit and actual camera','head/hair asset matching the recorded orientation','complete body/neck underpainting and seam review in every master','same-frame weapon/hand occlusion retained'],'source_animation_adapted':True,'source_glb_modified':False,'production_profile_adopted':False,'runtime_admitted':False};(p/'head-pose-family-study.json').write_text(json.dumps(proof,indent=2)+'\n');(o/'measurements.json').write_text(json.dumps({k:v for k,v in proof.items()if k!='families'},indent=2)+'\n')
# Preserve actual sample cadence from the earlier same-sample source review.
oldgif=Image.open('docs/character-factory/review/patch001-reference-preflight-20261027/guide-fit-normal.gif');durations=[]
for i in range(oldgif.n_frames):oldgif.seek(i);durations.append(oldgif.info['duration'])
frames=[];before=b/'research/tall-guide-proportion-pilot-20261027/mage130-capture'
for i in range(24):
 frame=Image.new('RGBA',(1024,560),'#ddd');draw=ImageDraw.Draw(frame);draw.text((12,10),f'Source head motion / {i:02d}',fill='black');draw.text((524,10),'Target-facing gaze STUDY / same body motion',fill='black')
 for k,path in enumerate([before/'SW'/f'{i:03d}.png',p/'capture/SW'/f'{i:03d}.png']):frame.alpha_composite(Image.open(path).crop((224,224,576,576)).resize((512,512),Image.Resampling.LANCZOS),(k*512,40))
 frames.append(frame.convert('RGB'))
montage=Image.new('RGB',(1024*4,560*6))
for i,im in enumerate(frames):montage.paste(im,((i%4)*1024,(i//4)*560))
palette=montage.quantize(colors=255);indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in frames]
for filename,times in [('gaze-source-normal.gif',durations),('gaze-source-slow.gif',[x*3 for x in durations])]:indexed[0].save(o/filename,save_all=True,append_images=indexed[1:],duration=times,loop=0,disposal=2,optimize=False)
(o/'preview-timing.json').write_text(json.dumps({'fps_of_blender_source':24,'durations_ms':durations,'last_frame_review_hold_ms':200,'gif_restarts_for_review_only':True,'source_job_loop':False,'runtime_event_or_transition_acceptance':False},indent=2)+'\n')
contact=Image.new('RGBA',(1536,1536),'#ddd')
for row,direction in enumerate(['SW','NW','NE','SE']):
 for col,i in enumerate([0,8,22,23]):
  im=Image.open(c/direction/f'{i:03d}.png').crop((448,480,1152,1184)).resize((384,384),Image.Resampling.LANCZOS);contact.alpha_composite(im,(col*384,row*384));ImageDraw.Draw(contact).text((col*384+5,row*384+5),f'{direction} / {i}',fill='black')
contact.convert('RGB').save(o/'four-real-camera-guide-contact.jpg',quality=97)
paint=b/'review/mage-female-single-frame-trace-20261027';shutil.copy2(paint/'head-collar-contact.jpg',o/'painted-key-head-collar-review.jpg');shutil.copy2(paint/'receipt.json',o/'painted-key-fixed-fit-proof.json');shutil.copy2(b/'review/archer-remaining-view-head-semantic-pilots-20261027/pilot-heads.jpg',o/'archer-18-key-head-ownership.jpg');shutil.copy2(b/'review/archer-remaining-view-head-semantic-pilots-20261027/receipt.json',o/'archer-18-key-ownership-proof.json');shutil.copy2(__file__,o/'build-report-source.py');print(json.dumps({k:proof[k]for k in ['source_pose_views','max_neck_counter_rotation_degrees','max_protected_body_matrix_error','max_actual_render_matrix_error_all66_bones']}))
