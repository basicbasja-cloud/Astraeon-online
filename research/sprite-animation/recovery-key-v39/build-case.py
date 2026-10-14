"""Replace only one body drawing; preserve all other pose bindings exactly."""
import copy,hashlib,json,math
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];V=P.parent/'coherent-motion-v38'
bind=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
parent=json.loads((V/'motion-contract.json').read_text());before=copy.deepcopy(parent['variants']['review']);after=copy.deepcopy(before)
points=[[168,139],[195,123]]
def apply(m,p):return[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]
def mid(pair):return[(pair[0][k]+pair[1][k])/2 for k in [0,1]]
def angle(pair):a,b=pair;return math.atan2(b[1]-a[1],b[0]-a[0])
atlas=Image.new('RGBA',(1536,1024))
for i,row in enumerate(before):
    path=P/'body-key.png' if i==6 else ROOT/row['body']['path']
    im=Image.open(path).convert('RGBA');assert im.size==(384,512);atlas.paste(im,(i%4*384,i//4*512))
atlas.save(P/'packed-reference-atlas.png')
row=after[6];target=[apply(row['body_matrix'],p) for p in points];src=parent['head_insertion_points_native'];a=mid(src);b=mid(target);turn=angle(target)-angle(src);c=math.cos(turn)*.11;sn=math.sin(turn)*.11
v=[points[1][k]-points[0][k] for k in [0,1]];length=math.hypot(*v);u=[x/length for x in v];n=[-u[1],u[0]]
polygon=[[points[0][k]-u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3+n[k]*22 for k in [0,1]],[points[0][k]-u[k]*3+n[k]*22 for k in [0,1]]]
row.update(body=bind(P/'body-key.png'),raw_sheet=bind(P/'packed-reference-atlas.png'),raw_art_index=6,raw_sheet_kind='Locally packed, independently verified atlas; NOT native full-strip generation',generation_job='v39_single_existing_key_edit',body_collar_lip_points_native=points,observed_receiver_surface_xy=b,head_matrix=[c,sn,-sn,c,b[0]-c*a[0]+sn*a[1],b[1]-sn*a[0]-c*a[1]],head_turn_radians=turn,collar_foreground_polygon_native=polygon,observation='Manually reviewed visible outer collar lip on known-canvas-normalized native output; +/-3canonicalpx, not inferred joints')
contract=copy.deepcopy(parent);contract['variants']=dict(raw8=before,review=after)
contract['selected_pose_map']=[[2,7],[2,1],[2,2],[2,3],[2,4],[2,5],[39,0],[2,7]]
contract['selection_policy']='Only index6/display7 is replaced by one native edited existing-key output, normalized from its known source plate. Other seven complete records are byte-identical to v38 review. Packed atlas is bookkeeping, not native whole-strip art.'
contract['isolated_key_provenance']=dict(request=bind(P/'request.json'),normalization=bind(P/'normalization.json'),raw_native=bind(P/'repair-raw.png'),canonical_body=bind(P/'body-key.png'),bookkeeping_atlas=bind(P/'packed-reference-atlas.png'),protected_other_keys=bind(P/'protected-other-keys.json'))
(P/'motion-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
(P/'collar-observation.json').write_text(json.dumps(dict(visible_outer_lip_points=points,canonical_canvas=[384,512],uncertainty_px=3,method='Manual actual-pixel inspection of outer collar lip. Head scale/source insertion pair unchanged.',inspection=bind(P/'collar-inspection.png')),indent=2)+'\n')
