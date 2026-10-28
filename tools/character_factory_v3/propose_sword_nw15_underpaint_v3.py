"""Propose masked same-frame underpaint without changing the sword-on master.

Only opaque weapon-covered pixels in a bounded manual weapon-overlap polygon are filled.
Generated pixels are a draft, not evidence of correct hidden anatomy or a swap.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
V2=BASE/'review/swordsman-nw15-weapon-ownership-v3-proposal-20261028'
INPUT=BASE/'painted-candidates/swordsman-nw15-underpaint-20261028'
ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
CROP=(310,430,430,530)
POLYGON=[(350,465),(390,465),(405,482),(405,510),(350,510)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def select_underpaint(body,weapon,hand,donor,mask):
 return mask&(body[:,:,3]==0)&(weapon[:,:,3]==255)&(hand[:,:,3]==0)&(donor[:,:,3]>=240)
def compose(layers,include_weapon=True):
 out=Image.new('RGBA',(768,768))
 for r in ORDER:
  if r=='Weapon' and not include_weapon:continue
  out.alpha_composite(Image.fromarray(layers[r]))
 return out

def build(out):
 if out.exists():raise ValueError('Choose a fresh output')
 paths=[V2/'layers'/f'{r}.png' for r in ORDER]+[V2/'master.png',V2/'receipt.json',INPUT/'donor.png',INPUT/'with-sword-reference.png',INPUT/'without-sword-reference.png',INPUT/'prompt.txt',Path(__file__).resolve()]
 pins={str(p.relative_to(ROOT)):sha(p) for p in paths}
 previous=json.loads((V2/'receipt.json').read_text())
 if not previous.get('master_rgba_exact') or previous.get('runtime_admitted'):raise ValueError('Unexpected source ownership proposal')
 original={r:np.array(Image.open(V2/'layers'/f'{r}.png').convert('RGBA')) for r in ORDER}
 source_master=Image.open(V2/'master.png').convert('RGBA')
 if compose(original).tobytes()!=source_master.tobytes():raise ValueError('Source candidate does not recompose')
 with Image.open(INPUT/'donor.png') as source:donor=source.convert('RGBA')
 donor_resolution=list(donor.size)
 width,height=CROP[2]-CROP[0],CROP[3]-CROP[1]
 if donor.width*height!=donor.height*width:raise ValueError('Generated crop aspect ratio differs')
 donor=donor.resize((width,height),Image.Resampling.LANCZOS)
 placed=Image.new('RGBA',(768,768));placed.paste(donor,CROP[:2]);donor_array=np.array(placed)
 polygon=Image.new('1',(768,768));ImageDraw.Draw(polygon).polygon(POLYGON,fill=1)
 selected=select_underpaint(original['BodyCostume'],original['Weapon'],original['WeaponHandOccluder'],donor_array,np.array(polygon,dtype=bool))
 if not selected.any():raise ValueError('No opaque protected underpaint pixels')
 updated={r:a.copy() for r,a in original.items()};updated['BodyCostume'][selected]=donor_array[selected]
 sword_on=compose(updated)
 if sword_on.tobytes()!=source_master.tobytes():raise ValueError('Underpaint changed sword-on visible master')
 out.mkdir(parents=True);(out/'layers').mkdir()
 for role in ORDER:Image.fromarray(updated[role]).save(out/'layers'/f'{role}.png')
 sword_on.save(out/'master.png');compose(updated,False).save(out/'no-weapon-preview.png')
 marker=Image.new('RGBA',(768,768));marker_array=np.array(marker);marker_array[selected]=(255,0,180,180);marked=compose(updated,False);marked.alpha_composite(Image.fromarray(marker_array))
 crop=(330,460,390,510);board=Image.new('RGB',(1440,430),'#ddd');draw=ImageDraw.Draw(board)
 for col,(title,img) in enumerate([('V3 source: no sword',compose(original,False)),('Proposed underpaint',compose(updated,False)),('Inserted pixels marked',marked)]):
  tile=Image.new('RGBA',(60,50),'#ddd');tile.alpha_composite(img.crop(crop));board.paste(tile.convert('RGB').resize((480,400),Image.Resampling.NEAREST),(col*480,30));draw.text((col*480+5,5),title,fill='black')
 board.save(out/'underpaint-comparison.png')
 for p,digest in pins.items():
  if sha(ROOT/p)!=digest:raise ValueError('Pinned input changed during proposal')
 proof={'status':'PROPOSED_V3_MASKED_GENERATED_UNDERPAINT_NOT_APPROVED','direction':'NW','frame':15,'generated_source_resolution':donor_resolution,'source_crop_author_px':list(CROP),'guard_polygon_author_px':POLYGON,'underpaint_pixels':int(selected.sum()),'only_opaque_weapon_covered_pixels':True,'minimum_donor_alpha':240,'previous_master_byte_exact':True,'source_modified':False,'pose_or_canvas_changed':False,'painted_foot_contact_verified':False,'semantic_boundary_reviewed':False,'art_approved':False,'runtime_admitted':False,'model_and_seed':'not exposed','donor_reference':'Generated from V2 ownership preview; V3 changes a bounded guard-edge ownership region.','source_sha256':pins,'limitations':['Generated cloth content may be anatomically or semantically wrong; mask/edge inspection is required.','Only opaque weapon-covered pixels in one local region are filled; other hidden areas and semitransparent edges remain missing.','One frame/view does not provide a swappable weapon, animation or game acceptance.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
 return {k:v for k,v in proof.items() if k not in ('source_sha256','guard_polygon_author_px')}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
