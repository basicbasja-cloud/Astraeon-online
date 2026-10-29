"""Relabel one frame with a SAM2 weapon suggestion; semantic review required."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
ORDER=('BodyCostume','HeadHair','Weapon')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(mask_path,base,out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 master=Image.open(base/'master.png').convert('RGBA');pixels=np.array(master);old=np.array(Image.open(base/'labels.png'));mask=Image.open(mask_path).convert('L')
 if mask.size!=(1254,1254):raise ValueError('Expected original-canvas mask')
 tile=mask.resize((384,384),Image.Resampling.NEAREST);canvas=Image.new('L',(768,768));canvas.paste(tile,(192,257));selected=np.array(canvas)>127
 edge=binary_dilation(selected,iterations=2)&~selected&(pixels[:,:,3]>0)
 selected |= edge & ((pixels[:,:,3]<200)|(np.min(pixels[:,:,:3],axis=2)>=235))
 if np.any(selected&(old==2)):raise ValueError('Weapon proposal overlaps head')
 labels=old.copy();labels[old==3]=1;labels[selected&(pixels[:,:,3]>0)]=3
 if not np.any(labels==3):raise ValueError('Empty weapon proposal')
 layers={}
 for index,role in enumerate(ORDER,1):
  a=np.zeros_like(pixels);a[labels==index]=pixels[labels==index];layers[role]=Image.fromarray(a,'RGBA')
 combined=Image.new('RGBA',(768,768))
 for role in ORDER:combined.alpha_composite(layers[role])
 if combined.tobytes()!=master.tobytes():raise ValueError('Same-frame composition changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(labels,'L').save(out/'labels.png')
 for role,im in layers.items():im.save(out/'layers'/f'{role}.png')
 old_weapon=Image.open(base/'layers/Weapon.png').convert('RGBA');body_head=Image.alpha_composite(layers['BodyCostume'],layers['HeadHair']);board=Image.new('RGB',(960,300),'#808080');draw=ImageDraw.Draw(board);crop=(345,510,465,600)
 for i,(title,im) in enumerate([('Previous weapon',old_weapon),('SAM weapon proposal',layers['Weapon']),('Without weapon',body_head)]):
  tile=Image.new('RGBA',(120,90),'#808080');tile.alpha_composite(im.crop(crop));board.paste(tile.convert('RGB').resize((320,240),Image.Resampling.NEAREST),(320*i,40));draw.text((320*i+4,5),title,fill='black')
 board.save(out/'weapon-comparison.png');proof={'status':'SAM2_WEAPON_RELABEL_PROPOSAL_NOT_APPROVED','master_sha256':sha(base/'master.png'),'old_labels_sha256':sha(base/'labels.png'),'sam_mask_sha256':sha(mask_path),'old_weapon_pixels':int(np.sum(old==3)),'new_weapon_pixels':int(np.sum(labels==3)),'weapon_to_body_pixels':int(np.sum((old==3)&(labels==1))),'body_to_weapon_pixels':int(np.sum((old==1)&(labels==3))),'same_frame_master_exact':True,'source_modified':False,'runtime_admitted':False,'limitations':['SAM and fringe rules may omit hilt edges or include boot/hand pixels.','Underlying body and handle hidden by the weapon are not authored.','Head and alpha remain provisional; no other frames, variants or gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mask',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.mask,a.base,a.output)))
