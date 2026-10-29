"""Use one SAM2 head suggestion to relabel visible SW08 draft pixels.

The segmentation and source keyed alpha require human review. Exact recomposition
is a data invariant, not proof that head/collar semantics are correct.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-visible-cutout-v2-20261029'
ORDER=('BodyCostume','HeadHair','Weapon')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(mask_path,out,base=BASE):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 master=Image.open(base/'master.png').convert('RGBA');pixels=np.array(master);old=np.array(Image.open(base/'labels.png'))
 mask=Image.open(mask_path).convert('L')
 if mask.size!=(1254,1254):raise ValueError('Expected mask on original source canvas')
 tile=mask.resize((384,384),Image.Resampling.NEAREST);canvas=Image.new('L',(768,768));canvas.paste(tile,(192,257));selected=np.array(canvas)>127
 # Include nearby visible edge pixels from the previous head and pale or
 # partially transparent antialias fringes. This is still a proposal.
 edge=binary_dilation(selected,iterations=3)&~selected&(pixels[:,:,3]>0)
 selected |= edge & ((old==2)|(pixels[:,:,3]<200)|(np.min(pixels[:,:,:3],axis=2)>=225))
 labels=old.copy();labels[old==2]=1
 if np.any(selected&(old==3)):raise ValueError('Head proposal overlaps weapon ownership')
 labels[selected&(pixels[:,:,3]>0)]=2
 if not np.any(labels==2):raise ValueError('Empty head proposal')
 layers={}
 for index,role in enumerate(ORDER,1):
  a=np.zeros_like(pixels);a[labels==index]=pixels[labels==index];layers[role]=Image.fromarray(a,'RGBA')
 combined=Image.new('RGBA',(768,768))
 for role in ORDER:combined.alpha_composite(layers[role])
 if combined.tobytes()!=master.tobytes():raise ValueError('Same-frame composition changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(labels,'L').save(out/'labels.png')
 for role,image in layers.items():image.save(out/'layers'/f'{role}.png')
 original=Image.open(base/'layers/HeadHair.png').convert('RGBA');board=Image.new('RGB',(960,480),'#808080');draw=ImageDraw.Draw(board);crop=(400,430,496,518)
 for i,(title,img) in enumerate([('Manual head',original),('SAM proposal head',layers['HeadHair']),('SAM body + weapon',Image.alpha_composite(layers['BodyCostume'],layers['Weapon']))]):
  tile=Image.new('RGBA',(96,88),'#808080');tile.alpha_composite(img.crop(crop));board.paste(tile.convert('RGB').resize((320,440),Image.Resampling.NEAREST),(i*320,40));draw.text((i*320+4,6),title,fill='black')
 board.save(out/'head-comparison.png')
 proof={'status':'SAM2_HEAD_RELABEL_PROPOSAL_NOT_APPROVED','master_sha256':sha(base/'master.png'),'old_labels_sha256':sha(base/'labels.png'),'sam_mask_sha256':sha(mask_path),'manual_head_pixels':int(np.sum(old==2)),'sam_head_pixels':int(np.sum(labels==2)),'head_to_body_pixels':int(np.sum((old==2)&(labels==1))),'body_to_head_pixels':int(np.sum((old==1)&(labels==2))),'original_keyed_master_exact':True,'source_modified':False,'runtime_admitted':False,'limitations':['SAM may exclude ear, neck, hair edges or include scarf; inspect before use.','Existing white-key edge halos and sword/boot ownership remain.','Hidden surfaces, variants and other frames are not authored.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mask',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--base',type=Path,default=BASE);a=p.parse_args();print(json.dumps(build(a.mask,a.output,a.base)))
