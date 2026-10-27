from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'review/archer-remaining-view-head-complete-proposals-v6-20261027';a=json.load(open(p/'proposal-receipt.json'));old=b/'review/archer-remaining-view-head-semantic-pilots-20261027';checked=[];bad=[];missing=[]
for r in a['frames']:
 path=p/r['sex']/r['view']/f"{r['index']:03d}.png"
 if not path.exists():missing.append({k:r[k]for k in ['sex','view','index']});continue
 if r['index']in[0,8,15]:
  prior=old/r['sex']/r['view']/f"{r['index']:03d}-HeadHair.png";same=np.array_equal(np.array(Image.open(path)),np.array(Image.open(prior)));row={k:r[k]for k in ['sex','view','index']};row['same_rgba_as_reviewed_key']=same;checked.append(row)
  if not same:bad.append(row)
for page in range(4):
 contact=Image.new('RGBA',(1440,960),'#ddd')
 for vi,view in enumerate(['SW','NE','SE']):
  for si,sex in enumerate(['male','female']):
   col=vi*2+si
   for row,i in enumerate(range(page*4,page*4+4)):
    rec=next(r for r in a['frames']if(r['sex'],r['view'],r['index'])==(sex,view,i));x0,y0,x1,y1=rec['crop'];cx=(x0+x1)//2;cy=(y0+y1)//2;path=p/sex/view/f'{i:03d}.png'
    if path.exists():
     im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);contact.alpha_composite(bg.crop((cx-75,cy-75,cx+75,cy+75)).resize((240,240),Image.Resampling.NEAREST),(col*240,row*240))
    else:ImageDraw.Draw(contact).rectangle((col*240,row*240,col*240+239,row*240+239),fill='#f99')
    ImageDraw.Draw(contact).text((col*240+3,row*240+3),f'{sex} {view} {i}',fill='black')
 contact.convert('RGB').save(p/f'head-contact-{page:02d}.jpg',quality=98)
proof={'status':'COMPLETE_HEAD_PROPOSAL_TIMELINES_NOT_SEMANTIC_ACCEPTANCE','records':len(a['frames']),'successful_head_outputs':len(a['frames'])-len(missing),'missing':missing,'reviewed_key_reproduction':checked,'reviewed_key_rgba_mismatches':bad,'full96_visual_approval':False,'runtime_admitted':False};(p/'key-reproduction-and-completeness.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copy2(__file__,p/'review-source.py');print(json.dumps({'records':len(a['frames']),'missing':missing,'reproduced_reviewed_keys':len(checked)-len(bad),'key_mismatches':bad}))
