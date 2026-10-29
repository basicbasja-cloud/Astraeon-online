"""Compare candidate Hit recovery endpoint against the native Idle guide."""
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
IDLE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/8c4bf2dc1ce31390e383/manifest.json'
CANDIDATE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-floor-ik-20261029/manifest.json'
DIRS=('S','SW','W','NW','N','NE','E','SE')

def angle(a,b):
 na=math.sqrt(sum(v*v for v in a));nb=math.sqrt(sum(v*v for v in b))
 if na<1e-9 or nb<1e-9:raise ValueError('invalid quaternion')
 dot=min(1.,abs(sum(x*y for x,y in zip(a,b))/(na*nb)))
 return math.degrees(2*math.acos(dot))

def audit():
 idle=json.loads(IDLE.read_text());candidate=json.loads(CANDIDATE.read_text())
 if idle['job']['source_actions']!=['Idle_Sword'] or candidate['job']['source_actions']!=['Hit_Chest'] or not candidate['job'].get('floor_ik_experiment') or set(candidate['views'])!=set(DIRS):raise ValueError('unexpected source contract')
 if idle['job']['source_sha256']!=candidate['job']['source_sha256']:raise ValueError('different motion sources')
 ratio=candidate['job']['resolution']/idle['job']['resolution'];results={}
 for direction in DIRS:
  a=idle['views'][direction]['frames'][0];b=candidate['views'][direction]['frames'][-1]
  if a['action']!='Idle_Sword' or b['action']!='Idle_Sword' or b.get('transition_weight')!=1:raise ValueError('unexpected idle target')
  if set(a['landmarks'])!=set(b['landmarks']) or set(a['bone_rotations'])!=set(b['bone_rotations']):raise ValueError('landmark schema differs')
  pos={name:math.dist(a['world_landmarks'][name],b['world_landmarks'][name]) for name in a['world_landmarks']}
  projected={name:math.dist([v*ratio for v in a['landmarks'][name]],b['landmarks'][name]) for name in a['landmarks']}
  rot={name:angle(a['bone_rotations'][name],b['bone_rotations'][name]) for name in a['bone_rotations']}
  prop={name:math.dist([v*ratio for v in a['weapon_guide'][name]],b['weapon_guide'][name]) for name in ('grip','tip')}
  results[direction]={'world_landmark_max_m':max(pos.values()),'projected_landmark_max_authoring_px':max(projected.values()),'bone_rotation_max_degrees':max(rot.values()),'weapon_guide_max_authoring_px':max(prop.values())}
 return {'status':'RIG_ENDPOINT_COMPARISON_NOT_GAMEPLAY_APPROVAL','idle_manifest_sha256':hashlib.sha256(IDLE.read_bytes()).hexdigest(),'candidate_manifest_sha256':hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),'directions':results,
         'limitations':['Only recorded bones, landmarks and guide prop endpoints are compared; not every rig joint or mesh vertex.', 'A rig endpoint is not an installed or visually matched painted Idle and does not prove game transitions, contact, grip or motion quality.']}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists() or a.output.is_symlink():raise ValueError('choose fresh output')
 a.output.write_text(json.dumps(audit(),indent=2)+'\n')
