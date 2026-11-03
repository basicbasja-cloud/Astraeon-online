"""Conservative NW005 visible scarf transfer; no hidden surface inference."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1';O=P/'research/swordsman-nw005-head-ownership-20261103';H=P/'research/swordsman-nw005-hidden-hair-20261103/HeadHair-underpaint.png';SRC=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW';ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 parts={}
 for role in ORDER:
  path=H if role=='HeadHair' else O/(role+'.png') if role in ('BodyCostume','Weapon') else SRC/role/'005.png';parts[role]=np.array(Image.open(path).convert('RGBA'))
 w=parts['Weapon'];body=parts['BodyCostume'];yy,xx=np.indices(w.shape[:2]);r,g,b=w[:,:,:3].astype(int).transpose(2,0,1);mask=(xx>=245)&(xx<=255)&(yy>=229)&(yy<=237)&(w[:,:,3]>0)&(r>g*1.2)&(g>b*1.2)&(r>90)
 if np.any(body[:,:,3][mask]>0):raise ValueError('body ownership overlaps transfer')
 body[mask]=w[mask];w[mask]=0;canvas=Image.new('RGBA',(512,512))
 for role in ORDER:canvas.alpha_composite(Image.fromarray(parts[role]))
 original=np.asarray(Image.open(SRC/'Master/005.png').convert('RGBA'));result=np.asarray(canvas);visible=(original[:,:,3]>0)|(result[:,:,3]>0)
 if not np.array_equal(original[visible],result[visible]) or not np.array_equal(original[:,:,3],result[:,:,3]):raise ValueError('master mismatch')
 out.mkdir(parents=True);Image.fromarray(body).save(out/'BodyCostume.png');Image.fromarray(w).save(out/'Weapon.png');Image.fromarray((mask*255).astype('uint8')).save(out/'scarf-transfer-mask.png');canvas.save(out/'recomposed.png');board=Image.new('RGB',(800,430),'#777');d=ImageDraw.Draw(board)
 for i,(name,bd) in enumerate((('previous body without weapon',np.array(Image.open(O/'BodyCostume.png').convert('RGBA'))),('proposed body without weapon',body))):
  x=Image.new('RGBA',(512,512));x.alpha_composite(Image.fromarray(bd));x.alpha_composite(Image.fromarray(parts['HeadHair']));x.alpha_composite(Image.fromarray(parts['WeaponHandOccluder']));bg=Image.new('RGBA',(512,512),'#777');bg.alpha_composite(x);board.paste(bg.crop((220,170,300,250)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(i*400,25));d.text((i*400+3,3),name,fill='white')
 board.save(out/'without-weapon-comparison.png');proof={'status':'NW005_SCARF_OWNERSHIP_NOT_APPROVED','body_sha256':sha(O/'BodyCostume.png'),'weapon_sha256':sha(O/'Weapon.png'),'underpaint_head_sha256':sha(H),'source_sha256':sha(SRC/'Master/005.png'),'script_sha256':sha(Path(__file__)),'transferred_pixels':int(mask.sum()),'rgba_mismatch':0,'limitations':['Conservative rectangle/color filter may include guard or omit scarf pixels; manual boundary review is necessary.', 'Hair and scarf behind opaque and semi-transparent blade edges remain incomplete.', 'One frame and view, no approved variants, animation or gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
