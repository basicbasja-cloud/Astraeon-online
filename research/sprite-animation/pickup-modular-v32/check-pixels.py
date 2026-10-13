"""Calibrate texture-only observer, then score actual image observations.
Rig coordinates are loaded only AFTER tracking, for held-out validation.
"""
import hashlib,json,importlib.util,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def load(name,file):
 s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
frames=json.loads((P/'frames.json').read_text());rows=frames['frames']
patches={
 'surface.far_boot_toe':dict(seed_xy=[118,465],half_extent=[10,8],search_box=[80,445,175,495],rotation_search_degrees=[0,0,1]),
 'surface.near_boot_toe':dict(seed_xy=[198,489],half_extent=[10,8],search_box=[165,465,280,512],rotation_search_degrees=[0,0,1]),
 'surface.reaching_cuff':dict(seed_xy=[118,291],half_extent=[24,24],search_box=[35,230,190,460],rotation_search_degrees=[-80,80,2],isolated_first_frame={'path':rel(P/'cuff-calibration-only.png'),'sha256':sha(P/'cuff-calibration-only.png')})}
for s in patches.values():s.update(ambiguity_radius_px=8,minimum_ncc=.95,minimum_margin=.015)
case={'canvas':[384,512],'frames':rows,'patches':patches,'calibration':'Frame0 visible toe texture patches and cuff junction inspected; fixed windows, no future pose predictions. Screen-near/far labels are not inferred anatomy.'}
(P/'observer-case.json').write_text(json.dumps(case,indent=2)+'\n')
observer=load('observer',ROOT/'skills/modular-eight-direction-sprites/scripts/rigged-surface-observer.py');observations=observer.observe(case,ROOT);observations['case_sha256']=sha(P/'observer-case.json')
(P/'pixel-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
source=P.parent/'pickup-pilot-v31/source/source.json';s=json.loads(source.read_text())
surface_case={**frames,'surface_landmarks':{n:{'definition':'visible painted '+n,'policy':'moving_surface' if n.endswith('cuff') else 'planted_surface_proxy','anatomical_owner':'unknown'} for n in patches},'planted_budget_px':6,'reference_phase':{'source_file':rel(source),'source_sha256':sha(source),'source_joint':'right.wrist','marker':'surface.reaching_cuff','axis':1,'calibration_frames':[0,3],'warning_fraction':.25,'definition_gap':'painted cuff surface versus actual source wrist bone; phase only'},'joint_owner_review':'proved by bound authoring parent/affine checks separately; hidden photo joints remain unknown'}
for i,row in enumerate(surface_case['frames']):row['observations']={name:{k:v for k,v in observations['tracks'][name][i].items() if k in ('status','xy','uncertainty_px','anatomical_owner','method')} for name in patches}
(P/'image-case.json').write_text(json.dumps(surface_case,indent=2)+'\n')
auditor=load('surface',ROOT/'skills/modular-eight-direction-sprites/scripts/planted-surface-review.py');report=auditor.audit(surface_case,ROOT)
(P/'surface-review.json').write_text(json.dumps(report,indent=2)+'\n')
# Numeric authoring truth only used after independently locating texture pixels.
poses=json.loads((P/'poses.json').read_text());errors=[]
for i,obs in enumerate(observations['tracks']['surface.reaching_cuff']):
 if obs['status']=='visible':errors.append({'frame':i,'calibration_frame':i==0,'error_px':math.dist(obs['xy'],poses[i]['joints']['right.wrist'])})
arrays=[np.array(Image.open(ROOT/r['path']).convert('RGBA')) for r in rows];stable={}
for name,spec in list(patches.items())[:2]:
 x,y=spec['seed_xy'];hx,hy=spec['half_extent'];roi=[x-hx,y-hy,x+hx+1,y+hy+1]
 blobs=[a[roi[1]:roi[3],roi[0]:roi[2]].tobytes() for a in arrays]
 stable[name]={'fixed_roi':roi,'all8_RGBA_patches_identical':len(set(blobs))==1,'patch_sha256':[hashlib.sha256(b).hexdigest() for b in blobs]}
summary={'surface_check_pass':report['numerical_surface_check_pass'],'planted_patch_pixels':stable,'cuff_after_detection_validation':errors,'held_out_cuff_max_error_px':max(r['error_px'] for r in errors if not r['calibration_frame']),'pixel_only_observer_no_later_pose_input':not observations['later_pose_coordinates_used'],'hidden_joint_detector_accuracy_claim':False,'full_canvas_first_last_identical':np.array_equal(arrays[0],arrays[-1])}
(P/'pixel-validation.json').write_text(json.dumps(summary,indent=2)+'\n')
board=Image.new('RGB',(1536,1024),(29,41,53))
for i,a in enumerate(arrays):
 im=Image.fromarray(a);d=ImageDraw.Draw(im)
 for n,track in observations['tracks'].items():
  p=track[i]
  if p['xy']:
   x,y=p['xy'];d.ellipse((x-4,y-4,x+4,y+4),outline=(64,255,150),width=1)
 board.paste(im,(i%4*384,i//4*512),im)
board.save(P/'pixel-tracks-review.png')
print(json.dumps({'issues':report['issues'],'cuff_max_held_out_error_px':summary['held_out_cuff_max_error_px'],'identical_planted_patches':all(s['all8_RGBA_patches_identical'] for s in stable.values())}))
