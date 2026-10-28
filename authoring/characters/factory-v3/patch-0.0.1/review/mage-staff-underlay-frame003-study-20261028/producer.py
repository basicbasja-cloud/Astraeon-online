from pathlib import Path
from PIL import Image
import hashlib, json, numpy as np
b=Path('authoring/characters/factory-v3/patch-0.0.1')
p=b/'painted-candidates/mage-staff-body-underlay-frame003-20261028'
o=b/'review/mage-staff-underlay-frame003-study-20261028'
o.mkdir(exist_ok=True)
source=b/'review/mage-female-single-frame-trace-20261027/Master/003.png'
base=Image.open(source).convert('RGBA')
raw=Image.open(p/'raw.png').convert('RGBA').convert('RGBa').resize((288,288),Image.Resampling.LANCZOS).convert('RGBA')
paint=Image.new('RGBA',(768,768));paint.alpha_composite(raw,(288,288))
mask=Image.open(p/'full-mask.png').convert('L')
result=Image.composite(paint,base,mask);result.save(o/'underpaint.png')
a=np.asarray(base);r=np.asarray(result);changed=np.any(a!=r,axis=2);m=np.asarray(mask)>0
assert not np.any(changed&~m)
canvas=Image.new('RGBA',(1152,576),'#ddd')
for j,im in enumerate([base,result]):canvas.alpha_composite(im.crop((288,288,576,576)).resize((576,576),Image.Resampling.NEAREST),(j*576,0))
canvas.convert('RGB').save(o/'comparison.jpg',quality=96)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
(o/'receipt.json').write_text(json.dumps({'status':'STAFF_UNDERPAINT_PROPOSAL_NOT_APPROVED','source_sha256':sha(source),'raw_sha256':sha(p/'raw.png'),'full_mask_sha256':sha(p/'full-mask.png'),'changed_pixels':int(changed.sum()),'changed_outside_mask':0,'weapon_and_grip_semantics_validated':False,'other_frames_completed':False,'runtime_admitted':False},indent=2)+'\n')
