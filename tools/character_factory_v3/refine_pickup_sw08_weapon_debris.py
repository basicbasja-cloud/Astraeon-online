"""Transfer small detached hilt-area components to Weapon in a SW08 draft.

This is a localized semantic proposal, not a replacement or runtime approval.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-sam-weapon-20261029'
ORDER=('BodyCostume','HeadHair','Weapon');ROI=(370,545,401,578)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 master=Image.open(BASE/'master.png').convert('RGBA');pixels=np.array(master);old=np.array(Image.open(BASE/'labels.png'));components,count=label(old==1,np.ones((3,3)));move=np.zeros(old.shape,bool);selected=[]
 for index,box in enumerate(find_objects(components),1):
  if not box:continue
  y,x=box;area=int(np.sum(components[box]==index))
  if area<=4 and x.start>=ROI[0] and x.stop<=ROI[2] and y.start>=ROI[1] and y.stop<=ROI[3]:
   move[box]|=(components[box]==index);selected.append({'pixels':area,'bbox':[x.start,y.start,x.stop,y.stop]})
 if not selected:raise ValueError('Expected detached components are absent')
 labels=old.copy();labels[move]=3;layers={}
 for i,role in enumerate(ORDER,1):
  arr=np.zeros_like(pixels);arr[labels==i]=pixels[labels==i];layers[role]=Image.fromarray(arr,'RGBA')
 combined=Image.new('RGBA',(768,768))
 for role in ORDER:combined.alpha_composite(layers[role])
 if combined.tobytes()!=master.tobytes():raise ValueError('Same-frame master changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(labels,'L').save(out/'labels.png')
 for role,im in layers.items():im.save(out/'layers'/f'{role}.png')
 before=Image.open(BASE/'layers/BodyCostume.png').convert('RGBA');board=Image.new('RGB',(960,350),'#808080');draw=ImageDraw.Draw(board);crop=(350,525,465,605)
 for col,(name,im) in enumerate([('old body no weapon',before),('candidate body no weapon',layers['BodyCostume']),('candidate weapon',layers['Weapon'])]):
  bg=Image.new('RGBA',(115,80),'#808080');bg.alpha_composite(im.crop(crop));board.paste(bg.convert('RGB').resize((320,300),Image.Resampling.NEAREST),(col*320,40));draw.text((col*320+4,6),name,fill='black')
 board.save(out/'debris-comparison.png');proof={'status':'HILT_DEBRIS_TRANSFER_PROPOSAL_NOT_APPROVED','source_master_sha256':sha(BASE/'master.png'),'source_labels_sha256':sha(BASE/'labels.png'),'region_px':ROI,'components':selected,'transferred_pixels':int(move.sum()),'same_frame_master_exact':True,'source_modified':False,'runtime_admitted':False,'limitations':['Detached components near a hilt may belong to glove or other antialiased edges; inspect semantics.','Visible underlay and hidden handle remain missing.','Head, matte, all other frames and variants are unapproved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
