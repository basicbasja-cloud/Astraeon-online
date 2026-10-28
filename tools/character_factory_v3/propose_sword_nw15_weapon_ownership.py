"""Bounded same-frame semantic ownership proposal for an existing sword.

A hand-drawn, deliberately conservative mask transfers visible pixels only.
It is not a production cutout, hidden-surface repair, or variant approval.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
BINDING=BASE/'cutouts/f163f5e0b852f2767596/bindings.json'
INDEX=BASE/'cutout-store/index.json'
ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
MASKS={
 'BodyCostume':[(368,468),(371,468),(374,473),(374,477),(378,478),(378,482),(375,483),(375,493),(373,496),(369,493),(368,481),(367,475)],
 'WeaponHandOccluder':[(337,489),(344,485),(353,485),(354,493),(349,496),(344,498),(337,496)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists():raise ValueError('Choose a fresh output')
 records=json.loads(BINDING.read_text())['frames'];matches=[r for r in records if r['direction']=='NW' and r['index']==15]
 if len(matches)!=1:raise ValueError('Missing or duplicate target frame')
 frame=matches[0];store=json.loads(INDEX.read_text());original={};pins={str(p.relative_to(ROOT)):sha(p) for p in (BINDING,INDEX,Path(__file__).resolve())}
 for role in ORDER:
  asset=store['assets'][frame['assets'][role]]
  if asset['role']!=role or asset['pose_id']!=frame['pose_id'] or asset['camera_id']!=frame['camera_id']:raise ValueError('Role or pose mismatch')
  oid=asset['object'];path=(ROOT/store['objects'][oid]['file']).resolve()
  if not path.is_relative_to(ROOT):raise ValueError('Object outside repository')
  image=Image.open(path).convert('RGBA')
  if image.size!=(768,768) or hashlib.sha256(image.tobytes()).hexdigest()!=oid:raise ValueError('Source object mismatch')
  pins[str(path.relative_to(ROOT))]=sha(path);original[role]=np.array(image)
 changed={r:a.copy() for r,a in original.items()};counts={}
 for role,polygon in MASKS.items():
  mask=Image.new('1',(768,768));ImageDraw.Draw(mask).polygon(polygon,fill=1)
  selected=np.array(mask,dtype=bool)&(changed[role][:,:,3]>0)
  if np.any(selected&(changed['Weapon'][:,:,3]>0)):raise ValueError('Target ownership overlaps existing weapon')
  counts[role]=int(selected.sum());changed['Weapon'][selected]=changed[role][selected];changed[role][selected]=0
 if not all(counts.values()):raise ValueError('No pixels transferred from a selected source')
 def compose(parts,include_weapon=True):
  im=Image.new('RGBA',(768,768))
  for role in ORDER:
   if role=='Weapon' and not include_weapon:continue
   im.alpha_composite(Image.fromarray(parts[role]))
  return im
 old=compose(original);new=compose(changed)
 if old.tobytes()!=new.tobytes():raise ValueError('Proposal changed visible recomposition')
 if not np.array_equal(original['HeadHair'],changed['HeadHair']):raise ValueError('Head pixels changed')
 out.mkdir(parents=True);(out/'layers').mkdir()
 for role in ORDER:Image.fromarray(changed[role]).save(out/'layers'/f'{role}.png')
 new.save(out/'master.png')
 # Fixed common crop; background is only for inspection, not a sprite asset.
 crop=(310,400,470,530);board=Image.new('RGB',(160*4*3,130*3+50),'#ddd');draw=ImageDraw.Draw(board)
 for col,(title,img) in enumerate([('Original / sword',old),('Proposed / sword',new),('Original / no sword',compose(original,False)),('Proposed / no sword',compose(changed,False))]):
  tile=Image.new('RGBA',(160,130),'#ddd');tile.alpha_composite(img.crop(crop));board.paste(tile.convert('RGB').resize((480,390),Image.Resampling.NEAREST),(col*480,50));draw.text((col*480+6,10),title,fill='black')
 board.save(out/'ownership-comparison.png')
 for path,digest in pins.items():
  if sha(ROOT/path)!=digest:raise ValueError('Pinned source changed during proposal')
 proof={'status':'PROPOSED_MANUAL_OWNERSHIP_NOT_SEMANTICALLY_APPROVED','direction':'NW','frame':15,'mask_polygons_author_px':MASKS,'transferred_pixels_by_prior_role':counts,'master_rgba_exact':True,'source_modified':False,'frame_pose_or_scale_changed':False,'newly_exposed_hidden_surfaces_authored':False,'contact_verified':False,'art_approved':False,'runtime_admitted':False,'source_sha256':pins,'limitations':['Masks are provisional and need native-size semantic review; dark outline or glove pixels may be assigned incorrectly.','Hidden anatomy beneath original sword is not reconstructed.','One frame and direction only; not a working interchangeable weapon set.','No animation, ready transition, foot contact, other views or gameplay approval.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return {k:v for k,v in proof.items() if k not in ('source_sha256','mask_polygons_author_px')}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
