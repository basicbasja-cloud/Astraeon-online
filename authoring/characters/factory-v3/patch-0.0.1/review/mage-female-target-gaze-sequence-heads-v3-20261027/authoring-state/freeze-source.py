from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
b=Path('authoring/characters/factory-v3/patch-0.0.1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for kind in ['archer','mage']:
 if kind=='archer':
  parts=b/'review/archer-remaining-view-head-complete-proposals-v6-20261027';a=json.loads((parts/'proposal-receipt.json').read_text());items=[(f"{r['sex']}/{r['view']}/{r['index']:03d}",b/'review/archer-coherent-recovery-masters-v2-20261026'/r['sex']/r['view']/'Master'/f"{r['index']:03d}.png",parts/r['sex']/r['view']/f"{r['index']:03d}.png",parts/r['sex']/r['view']/'BodyRest'/f"{r['index']:03d}.png")for r in a['frames']]
 else:
  parts=b/'review/mage-female-target-gaze-sequence-heads-v3-20261027';items=[(f'female/SW/{i:03d}',b/'review/mage-female-single-frame-trace-20261027/Master'/f'{i:03d}.png',parts/'HeadHair'/f'{i:03d}.png',parts/'BodyRest'/f'{i:03d}.png')for i in range(24)]
 out=parts/'authoring-state';out.mkdir(exist_ok=True);rows=[]
 for key,master,head,rest in items:
  rgba=np.array(Image.open(master).convert('RGBA'));h=np.array(Image.open(head).convert('RGBA'));r=np.array(Image.open(rest).convert('RGBA'));labels=np.where(h[:,:,3]>0,2,np.where(rgba[:,:,3]>0,1,0)).astype('uint8');path=out/'labels'/f'{key}.png';path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(labels).save(path);rows.append({'id':key,'master':str(master),'master_sha256':sha(master),'labels':str(path),'labels_sha256':sha(path),'part_rgba_sha256':{'HeadHair':hashlib.sha256(h.tobytes()).hexdigest(),'BodyRest':hashlib.sha256(r.tobytes()).hexdigest()}})
 (out/'recipe.json').write_text(json.dumps({'schema':'astraeon.visible-ownership-study.v1','role_ids':{'1':'BodyRest','2':'HeadHair'},'frames':rows,'semantic_boundaries_approved':False,'runtime_admitted':False,'BodyRest_contains_weapon':True,'masks_are_saved_editable_authoring_data':True},indent=2)+'\n');(out/'freeze-source.py').write_bytes(Path(__file__).read_bytes())
