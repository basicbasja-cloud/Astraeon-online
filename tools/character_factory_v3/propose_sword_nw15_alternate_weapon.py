"""Single-frame isolated sword swap study; never imports or certifies variants."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_sword_nw15_underpaint_v3 as underpaint
from propose_sword_nw15_underpaint_v3 import ORDER,compose
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
BODY=BASE/'review/swordsman-nw15-underpaint-v3-proposal-20261028'
INPUT=BASE/'painted-candidates/swordsman-nw15-alternate-sword-20261028'
SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/annotations.generated.json'
CANONICAL=BASE/'review/preserved-swordsman-canonical-cutouts-20261023/receipt.json'
CROP=(320,430,470,580)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def place_sword(donor):
 if donor.width!=donor.height:raise ValueError('Donor must retain the square reference crop')
 tile=donor.convert('RGBA').resize((150,150),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(768,768));out.paste(tile,CROP[:2]);return out

def build(out):
 if out.exists():raise ValueError('Choose a fresh output')
 paths=[BODY/'layers'/f'{r}.png' for r in ORDER]+[BODY/'master.png',BODY/'receipt.json',INPUT/'donor.png',INPUT/'reference.png',INPUT/'prompt.txt',SOURCE,CANONICAL,Path(underpaint.__file__).resolve(),Path(__file__).resolve()]
 pins={str(p.relative_to(ROOT)):sha(p) for p in paths}
 under=json.loads((BODY/'receipt.json').read_text())
 if under.get('art_approved') or under.get('runtime_admitted') or not under.get('previous_master_byte_exact'):raise ValueError('Unexpected underpaint source')
 original={r:np.array(Image.open(BODY/'layers'/f'{r}.png').convert('RGBA')) for r in ORDER}
 if compose(original).tobytes()!=Image.open(BODY/'master.png').convert('RGBA').tobytes():raise ValueError('Original candidate does not recompose')
 expected_ref=Image.fromarray(original['Weapon']).crop(CROP).resize((900,900),Image.Resampling.NEAREST)
 with Image.open(INPUT/'reference.png') as ref:
  if ref.convert('RGBA').tobytes()!=expected_ref.tobytes():raise ValueError('Reference crop differs from source weapon')
 with Image.open(INPUT/'donor.png') as donor:
  donor_size=list(donor.size);alternate=place_sword(donor)
 changed={r:a.copy() for r,a in original.items()};changed['Weapon']=np.array(alternate)
 records=json.loads(CANONICAL.read_text())['frames'];mapping=next(r for r in records if r['action']=='BasicAttack' and r['direction']=='NW')['frames'][15]
 annotation=json.loads(SOURCE.read_text())['frames'][15]
 points={n:[float(annotation[n][i])*mapping['camera_scale']+mapping['canvas_translation'][i] for i in (0,1)] for n in ('weapon_grip','weapon_guard','weapon_tip')}
 def pixel(im,point):return im.getpixel((round(point[0]),round(point[1])))[3]
 grip=points['weapon_grip'];alt_grip=pixel(alternate,grip);hand_grip=pixel(Image.fromarray(original['WeaponHandOccluder']),grip);tip_alpha=pixel(alternate,points['weapon_tip'])
 if min(alt_grip,hand_grip)<240:raise ValueError('Guide grip is not covered by both alternate sword and occluding hand')
 if tip_alpha<10:raise ValueError('Alternate sword does not reach the annotated tip')
 if any(not np.array_equal(changed[r],original[r]) for r in ORDER if r!='Weapon'):raise ValueError('Non-weapon layer changed')
 new=compose(changed);old=compose(original);without=compose(original,False)
 out.mkdir(parents=True);alternate.save(out/'alternate-weapon.png');new.save(out/'master-with-alternate.png')
 crop=(300,330,500,570);board=Image.new('RGB',(1200,510),'#ddd');draw=ImageDraw.Draw(board);toggles=[]
 for col,(name,img) in enumerate([('Original weapon',old),('Alternate weapon',new),('No weapon / underpaint',without)]):
  tile=Image.new('RGBA',(200,240),'#ddd');tile.alpha_composite(img.crop(crop));scaled=tile.convert('RGB').resize((400,480),Image.Resampling.NEAREST);board.paste(scaled,(col*400,30));draw.text((col*400+5,5),name,fill='black')
  frame=Image.new('RGB',(400,510),'#ddd');frame.paste(scaled,(0,30));ImageDraw.Draw(frame).text((5,5),name+' / single-frame toggle',fill='black');toggles.append(frame)
 board.save(out/'weapon-swap-comparison.png')
 toggles[0].save(out/'weapon-swap-toggle.gif',save_all=True,append_images=toggles[1:],duration=[900,900,900],loop=0,disposal=2)
 for p,digest in pins.items():
  if sha(ROOT/p)!=digest:raise ValueError('Pinned input changed')
 proof={'status':'SINGLE_FRAME_ALTERNATE_WEAPON_PROPOSAL_NOT_APPROVED','character':'swordsman-male','direction':'NW','frame':15,'source_crop_author_px':list(CROP),'generated_resolution':donor_size,'mapping':'full 1254-square crop uniformly resampled into the recorded 150-square authoring crop; no per-frame bbox fitting','source_points_author_px':points,'alternate_alpha_at_grip':alt_grip,'hand_alpha_at_grip':hand_grip,'alternate_alpha_at_original_tip':tip_alpha,'non_weapon_layers_byte_identical':True,'source_modified':False,'pose_or_canvas_changed':False,'art_approved':False,'runtime_admitted':False,'model_and_seed':'not exposed','preview':'three-state single-frame asset toggle, not an animation loop','source_sha256':pins,'limitations':['Coverage at a point is not proof of correct grip anatomy or occlusion.','Underpaint, ownership, alpha edges and the generated sword require visual review.','One frame/view only: no coherent weapon animation, 4-direction set, actual game test or reusable variant is established.','Trail alignment for the alternate weapon is not verified.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return {k:v for k,v in proof.items() if k!='source_sha256'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
