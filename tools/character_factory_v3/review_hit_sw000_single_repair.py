"""Compare manually marked single-frame sword tip with frozen source guide."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw000-single-repair-20261102'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 raw=P/'raw.png';targetfile=P/'source-targets.json';im=Image.open(raw).convert('RGB')
 if im.size!=(1254,1254):raise ValueError('unexpected generated dimensions')
 t=json.loads(targetfile.read_text())['weapon_targets_authoring_px']['tip'];actual=(771,493);target=((t[0]-224)*1254/320,(t[1]-260)*1254/320);dist=math.dist(actual,target);runtime=dist*320/1254*240/768
 marked=im.copy();d=ImageDraw.Draw(marked)
 for point,color,name in ((actual,'red','marked painted tip'),(target,'cyan','guide tip')):
  x,y=point;d.ellipse((x-9,y-9,x+9,y+9),outline=color,width=4);d.text((x+12,y-12),name,fill=color)
 d.line((actual,target),fill='magenta',width=3);out.mkdir(parents=True);marked.save(out/'marked.png');marked.crop((620,350,850,610)).resize((690,780),Image.Resampling.NEAREST).save(out/'tip-close.png')
 proof={'status':'SINGLE_FRAME_WEAPON_TARGET_NOT_APPROVED','raw_sha256':sha(raw),'target_sha256':sha(targetfile),'script_sha256':sha(Path(__file__)),'manual_tip_raw_px':actual,'manual_uncertainty_raw_px':4,'target_tip_raw_px':target,'tip_error_runtime_px':runtime,'uncertainty_runtime_px':4*320/1254*240/768,'limitations':['Tip was manually estimated; guide point is a finger-derived sword proxy, not a validated blade socket.', 'Single image generation did not enforce exact pixel or body pose constraints.', 'No registered master, complete animation, cutouts, variants or game test.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
