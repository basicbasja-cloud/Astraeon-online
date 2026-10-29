"""Reassign a reviewed detached blade-edge fragment in the NW15 draft.

This is a single-frame proposal, not approval or a runtime import.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw15-underpaint-v3-proposal-20261028/layers'
ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
POINTS=((440,462),(441,462),(438,463),(439,463),(437,464))

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def compose(layers,weapon=True):
 image=Image.new('RGBA',(768,768))
 for role in ORDER:
  if role!='Weapon' or weapon:image.alpha_composite(Image.fromarray(layers[role]))
 return image

def build(output):
 if output.exists() or output.is_symlink():raise ValueError('Choose a fresh output')
 paths={r:SOURCE/(r+'.png') for r in ORDER};pins={r:digest(p) for r,p in paths.items()}
 layers={r:np.array(Image.open(p).convert('RGBA')) for r,p in paths.items()};original=compose(layers)
 for x,y in POINTS:
  if layers['BodyCostume'][y,x,3]==0 or layers['Weapon'][y,x,3]!=0:raise ValueError('Source ownership differs from reviewed fragment')
  layers['Weapon'][y,x]=layers['BodyCostume'][y,x];layers['BodyCostume'][y,x]=0
 if compose(layers).tobytes()!=original.tobytes():raise ValueError('Original sword-on composition changed')
 if any(digest(paths[r])!=pins[r] for r in ORDER):raise ValueError('Source changed during proposal')
 output.mkdir(parents=True);(output/'layers').mkdir()
 for role,arr in layers.items():Image.fromarray(arr).save(output/'layers'/(role+'.png'))
 compose(layers,False).save(output/'no-weapon-preview.png');original.save(output/'master.png')
 receipt={'status':'SINGLE_FRAME_OWNERSHIP_PROPOSAL_NOT_APPROVED','direction':'NW','frame':15,'transferred_author_pixels':[list(p) for p in POINTS],'transferred_count':len(POINTS),'original_composite_exact':True,'source_modified':False,'art_approved':False,'runtime_admitted':False,'source_sha256':pins,'limitations':['Only one isolated blade-edge fragment was reassigned.','Remaining cutout semantics, hidden surfaces, animation and gameplay are not certified.']}
 (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();print(json.dumps(build(args.output)))
