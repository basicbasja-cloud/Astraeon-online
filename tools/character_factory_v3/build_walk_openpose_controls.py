"""Project evaluated Blender joints into fixed-crop OpenPose-like controls."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from review_painted_source_skeleton import project
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1';GUIDE=P/'guides/4e519e1eadc69aaf28a2/manifest.json';SKEL=P/'research/swordsman-walk-sw-source-skeleton-20261104/skeleton.json';CROP=(420,520,1116,1216);SIZE=512
# COCO/OpenPose palette order; head bone is a head-center proxy, not a nose.
NAMES=('head','neck_01','upperarm_r','lowerarm_r','hand_r','upperarm_l','lowerarm_l','hand_l','thigh_r','calf_r','foot_r','thigh_l','calf_l','foot_l')
EDGES=((1,2),(2,3),(3,4),(1,5),(5,6),(6,7),(1,8),(8,9),(9,10),(1,11),(11,12),(12,13),(1,0))
COLORS=('#ff0000','#ff5500','#ffaa00','#ffff00','#aaff00','#55ff00','#00ff00','#00ff55','#00ffaa','#00ffff','#00aaff','#0055ff','#5500ff')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 manifest=json.loads(GUIDE.read_text());skeleton=json.loads(SKEL.read_text());view=manifest['views']['SW'];frames=skeleton['frames']
 if skeleton['source_manifest_sha256']!=sha(GUIDE) or len(frames)!=16 or len(view['frames'])!=16:raise ValueError('skeleton/guide provenance mismatch')
 out.mkdir(parents=True);records=[]
 for i,frame in enumerate(frames):
  if frame['index']!=i:raise ValueError('pose order mismatch')
  bones=frame['bones'];projected={n:project(bones[n]['head'],view['camera'],1536) for n in NAMES}
  errors={n:float(np.linalg.norm(projected[n]-np.asarray(view['frames'][i]['landmarks'][n]))) for n in ('head','hand_r','hand_l','foot_r','foot_l')}
  if max(errors.values())>.002:raise ValueError(f'projection mismatch frame {i}')
  xy={n:tuple((projected[n]-CROP[:2])*SIZE/(CROP[2]-CROP[0])) for n in NAMES}
  if any(not(0<=x<SIZE and 0<=y<SIZE) for x,y in xy.values()):raise ValueError(f'joint outside crop frame {i}')
  canvas=Image.new('RGB',(SIZE,SIZE),'black');draw=ImageDraw.Draw(canvas)
  for (a,b),color in zip(EDGES,COLORS):draw.line((xy[NAMES[a]],xy[NAMES[b]]),fill=color,width=6)
  for j,n in enumerate(NAMES):
   x,y=xy[n];draw.ellipse((x-4,y-4,x+4,y+4),fill=COLORS[min(j,len(COLORS)-1)])
  p=out/f'{i:03}.png';canvas.save(p);records.append({'frame':i,'source_frame':frame['source_frame'],'joints':xy,'projection_errors_source_px':errors,'image_sha256':sha(p)})
 (out/'receipt.json').write_text(json.dumps({'status':'OPENPOSE_LIKE_CONTROLS_NOT_PAINT_OR_APPROVED','guide_sha256':sha(GUIDE),'skeleton_sha256':sha(SKEL),'implementation_sha256':sha(Path(__file__)),'crop':CROP,'size':SIZE,'frames':records,'limitations':['Head joint is a proxy, not a detected nose; face, fingers and weapon are omitted.','Projected joints are not painted anatomy or ground-contact verification.','ControlNet conditioning is not a hard geometric or temporal guarantee.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
