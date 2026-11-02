"""Compare a manually estimated painted wrist with the guide bone origin."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw000-arm-pose-20261102'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 im=Image.open(P/'raw.png').convert('RGB');t=json.loads((P/'source-targets.json').read_text())['projected_rig_bone_origins_authoring_px']['hand_l'];actual=(828,530);target=((t[0]-224)*1254/320,(t[1]-260)*1254/320);err=math.dist(actual,target)*320/1254*240/768
 if im.size!=(1254,1254):raise ValueError('unexpected canvas')
 out.mkdir(parents=True);d=ImageDraw.Draw(im)
 for p,c,name in ((actual,'red','estimated cuff'),(target,'cyan','guide hand origin')):
  x,y=p;d.ellipse((x-9,y-9,x+9,y+9),outline=c,width=3);d.text((x+12,y-12),name,fill=c)
 d.line((actual,target),fill='magenta',width=3);im.save(out/'marked.png');im.crop((720,450,950,700)).resize((690,750),Image.Resampling.NEAREST).save(out/'wrist-close.png');proof={'status':'MANUAL_WRIST_ESTIMATE_NOT_APPROVED','raw_sha256':sha(P/'raw.png'),'target_sha256':sha(P/'source-targets.json'),'script_sha256':sha(Path(__file__)),'manual_cuff_raw_px':actual,'manual_uncertainty_raw_px':12,'guide_hand_origin_raw_px':target,'distance_runtime_px':err,'uncertainty_runtime_px':12*320/1254*240/768,'limitations':['Cuff center is a manual visual proxy and is not the rig hand-bone origin; offsets are not a certified error.', 'Body fit and foreshortening differ, and the whole generated figure is not source-registered or approved.', 'Single frame, no cutouts, motion sequence, or gameplay.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
