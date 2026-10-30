"""Compare explicit BasicAttack source samples plus idle-transition experiment."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
G=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides'
ATTACK=G/'c297971fcef09188ff60/manifest.json';IDLE=G/'8c4bf2dc1ce31390e383/manifest.json'
DIRS=('SW','NW','NE','SE')

def quat_angle(a,b):
 na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(x*x for x in b))
 if min(na,nb)<1e-9:raise ValueError('invalid quaternion')
 dot=min(1.,abs(sum(x*y for x,y in zip(a,b))/(na*nb)))
 return math.degrees(2*math.acos(dot))

def build(source,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 baseline=json.loads(ATTACK.read_text());idle=json.loads(IDLE.read_text());candidate=json.loads((source/'manifest.json').read_text())
 if candidate.get('experimental_status')!='EXPLICIT_BASICATTACK_IDLE_STUDY_NOT_APPROVED' or set(candidate['views'])!=set(DIRS) or candidate['frame_count']!=20:raise ValueError('unexpected study')
 if baseline['job']['source_sha256']!=candidate['job']['source_sha256'] or idle['job']['source_sha256']!=candidate['job']['source_sha256']:raise ValueError('source mismatch')
 out.mkdir(parents=True);metrics={};panels=[]
 for direction in DIRS:
  old=baseline['views'][direction]['frames'];new=candidate['views'][direction]['frames'];target=idle['views'][direction]['frames'][0]
  if any(old[i]['source_frame']!=new[i]['source_frame'] or old[i]['action']!=new[i]['action'] for i in range(16)):raise ValueError('attack sampling differs')
  world=max(math.dist(old[i]['world_landmarks'][k],new[i]['world_landmarks'][k]) for i in range(16) for k in old[i]['world_landmarks'])
  rot=max(quat_angle(old[i]['bone_rotations'][k],new[i]['bone_rotations'][k]) for i in range(16) for k in old[i]['bone_rotations'])
  endpoint=max(math.dist(target['world_landmarks'][k],new[-1]['world_landmarks'][k]) for k in target['world_landmarks'])
  tip=max(math.dist(new[i-1]['weapon_guide']['tip'],new[i]['weapon_guide']['tip'])*240/768 for i in range(16,20))
  metrics[direction]={'attack_16_max_world_landmark_error_m':world,'attack_16_max_rotation_error_deg':rot,'endpoint_idle_max_world_landmark_error_m':endpoint,'blend_tip_max_step_runtime_px':tip}
 for i in range(20):
  board=Image.new('RGB',(992,240),'white');draw=ImageDraw.Draw(board)
  for j,direction in enumerate(DIRS):
   with Image.open(source/direction/f'{i:03}.png') as im:
    if im.size!=(768,768):raise ValueError('unexpected guide size')
    im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);tile=bg.crop((136,210,632,632)).resize((248,211),Image.Resampling.LANCZOS).convert('RGB');board.paste(tile,(j*248,29))
   draw.text((j*248+4,6),f'{direction} {i:02} '+('idle blend' if i>=16 else 'attack'),fill='black')
  panels.append(board)
 for name,ms in (('normal.gif',80),('slow.gif',160)):
  panels[0].save(out/name,save_all=True,append_images=panels[1:],duration=[ms]*19+[ms*4],loop=0,optimize=False)
 for i in (0,7,15,16,19):panels[i].save(out/f'frame{i:02}.png')
 result={'status':'RIG_TRANSITION_STUDY_NOT_APPROVED','attack_manifest_sha256':hashlib.sha256(ATTACK.read_bytes()).hexdigest(),'idle_manifest_sha256':hashlib.sha256(IDLE.read_bytes()).hexdigest(),'candidate_manifest_sha256':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),'directions':metrics,
         'limitations':['Recorded landmarks and selected bone rotations are not every mesh vertex or a painted master.', 'Joint blend, contact, grip, timing, trail and actual runtime transition are unapproved.', 'Review GIF repeats a one-shot at illustrative timing.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.source,a.output)))
