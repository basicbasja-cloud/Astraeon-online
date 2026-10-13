"""Single-reviewer visible SURFACE observations, not recovered bone centers."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;pack=json.loads((P/'packing.json').read_text());definitions={'surface.far_boot_toe':{'definition':'center of visible brown toe-cap front surface, screen-far boot; NOT joint or sole contact','anatomical_owner':'unknown','policy':'planted_surface_proxy'},'surface.near_boot_toe':{'definition':'center of visible brown toe-cap front surface, screen-near boot; NOT joint or sole contact','anatomical_owner':'unknown','policy':'planted_surface_proxy'},'surface.reaching_cuff':{'definition':'visible bracer/glove junction of reaching arm; NOT exposed wrist joint','anatomical_owner':'unknown','policy':'moving_surface'}}
far=[(112,465),(105,465),(112,467),(140,466),(160,465),(114,465),(108,467),(106,465)]
near=[(219,481),(214,483),(226,485),(249,485),(276,486),(225,486),(220,486),(217,486)]
cuff=[(118,291),(70,330),(66,394),(77,433),(104,413),(104,310),(105,315),(112,311)]
frames=[];seeds=[]
for i,f in enumerate(pack['frames']):
 observations={n:{'status':'visible','xy':list(p),'uncertainty_px':6 if 'cuff' in n else 3,'anatomical_owner':'unknown','reviewer':'agent single-reviewer; human correction pending'} for n,p in zip(definitions,(far[i],near[i],cuff[i]))}
 frames.append(dict(f,observations=observations))
 if i in (0,3,7):
  seeds += [{'frame':i,'joint':n,'xy':o['xy'],'image_sha256':f['sha256'],'kind':'manual_visible','uncertainty_px':o['uncertainty_px'],'owner_confirmed':False} for n,o in observations.items()]
source=P/'source/source.json'
case={'schema':'sprite-image-joint-tracks-v1','canvas':pack['canvas'],'frames':frames,'seeds':seeds,'surface_landmarks':definitions,'planted_budget_px':6,'source_sha256':json.loads(source.read_text())['source_sha256'],'reference_phase':{'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_joint':'right.wrist','marker':'surface.reaching_cuff','axis':1,'calibration_frames':[0,3],'warning_fraction':.25,'definition_gap':'clothed cuff surface vs source bone center; source-relative phase diagnostic only, not calibrated joint error'},'joint_owner_review':'unknown: cloth/armor occludes hip/knee/wrist bone centers; do not seed estimated anatomical points','old_own_attack_or_motion_used':False,'production_pass':False}
(P/'image-case.json').write_text(json.dumps(case,indent=2)+'\n')
