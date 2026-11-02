"""Review alpha bounds and approximate tip in an unapproved full-canvas donor."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw000-transparent-20261102'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 source=Image.open(P/'draft.png').convert('RGBA');donor=Image.open(P/'raw.png').convert('RGBA');t=json.loads((P/'source-targets.json').read_text())['weapon_targets_authoring_px']['tip'];
 if source.size!=(768,768) or donor.size!=(1254,1254):raise ValueError('unexpected canvas')
 bounds=lambda im:im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
 source_bbox=bounds(source);donor_bbox=bounds(donor);scaled=[v*768/1254 for v in donor_bbox];target=(t[0]*1254/768,t[1]*1254/768);actual=(691,615);error=math.dist(actual,target)*240/1254
 bg=Image.new('RGBA',donor.size,'#777');bg.alpha_composite(donor);d=ImageDraw.Draw(bg)
 for pt,c in ((actual,'red'),(target,'cyan')):
  x,y=pt;d.ellipse((x-7,y-7,x+7,y+7),outline=c,width=3)
 d.line((actual,target),fill='magenta',width=2);out.mkdir(parents=True);bg.crop((560,550,770,760)).resize((840,840),Image.Resampling.NEAREST).save(out/'tip-review.png')
 proof={'status':'TRANSPARENT_FULL_CANVAS_DONOR_NOT_APPROVED','source_sha256':sha(P/'draft.png'),'donor_sha256':sha(P/'raw.png'),'target_sha256':sha(P/'source-targets.json'),'script_sha256':sha(Path(__file__)),'source_alpha128_bbox':source_bbox,'donor_alpha128_bbox':donor_bbox,'donor_bbox_in_authoring_px':scaled,'manual_tip_raw_px':actual,'uncertainty_raw_px':4,'guide_tip_raw_px':target,'tip_error_runtime_px':error,'uncertainty_runtime_px':4*240/1254,'limitations':['Alpha bounding box includes weapon and is not a calibrated body or foot measurement.', 'Tip is a manual estimate compared against a finger-derived proxy, not a verified socket.', 'Generated donor changes character pixels and lacks approved anatomy, all frames, cutouts and gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
