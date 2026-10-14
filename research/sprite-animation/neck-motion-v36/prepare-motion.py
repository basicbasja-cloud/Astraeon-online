"""Bound coherent outfit drawings and explicit sparse-key selection. No frame fitting."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
raw=P/'motion-attempt2-raw.png';head=P/'head-skin-raw.png';source=P.parent/'pickup-pilot-v31/source/source.json';s=json.loads(source.read_text());neck=json.loads((P/'neck-bind.json').read_text())
# Source observations reviewed against enlarged actual collar/skin boundaries.
lip=[[[177,136],[206,125]],[[161,176],[183,159]],[[145,217],[168,196]],[[146,254],[165,234]],[[145,219],[166,204]],[[161,170],[184,153]],[[170,127],[196,114]],[[175,136],[199,125]]]
cap=json.loads((P/'neck-cap-observations.json').read_text());rest=cap[7]['centroid'];scale=300/(485-rest[1]);body_matrix=[scale,0,0,scale,192-scale*rest[0],180-scale*rest[1]]
def apply(m,p):return[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]
def midpoint(points):return[sum(p[k] for p in points)/len(points) for k in [0,1]]
def angle(points):a,b=points;return math.atan2(b[1]-a[1],b[0]-a[0])
def record(index,art):
 points=lip[art];target=[apply(body_matrix,p) for p in points];src=neck['head_insertion_points_native'];a=midpoint(src);b=midpoint(target);turn=angle(target)-angle(src);c=math.cos(turn)*.11;sn=math.sin(turn)*.11;m=[c,sn,-sn,c,b[0]-c*a[0]+sn*a[1],b[1]-sn*a[0]-c*a[1]]
 v=[points[1][k]-points[0][k] for k in [0,1]];L=math.hypot(*v);u=[v[0]/L,v[1]/L];n=[-u[1],u[0]]
 fg=[[points[0][k]-u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3+n[k]*22 for k in [0,1]],[points[0][k]-u[k]*3+n[k]*22 for k in [0,1]]]
 return dict(index=index,source_time_seconds=s['frames'][index]['source_time_seconds'],body=bind(P/f'body-frames/{art:02}.png'),raw_sheet=bind(raw),raw_art_index=art,body_matrix=body_matrix,head_matrix=m,body_collar_lip_points_native=points,observed_receiver_surface_xy=b,collar_foreground_polygon_native=fg,head_turn_radians=turn,observation='Manual visible painted collar/skin edge, +/-3 raw px; hidden joints unknown',hold=art==7 and index in [0,6,7])
selected=[7,1,2,3,4,5,7,7]
data=dict(schema='coherent-outfit-neck-motion-v1',canvas=[384,512],source=bind(source),head=bind(head),head_insertion_points_native=neck['head_insertion_points_native'],head_scale=.11,body_uniform_rest_matrix=body_matrix,bank_rest_calibration=dict(raw_art_index=7,observed_cap_centroid=rest,observed_near_sole_y=485,target_cap_centroid=[192,180],target_near_sole_y=480,all_frames_share_one_transform=True),variants=dict(raw8=[record(i,i) for i in range(8)],review=[record(i,art) for i,art in enumerate(selected)]),draw_order=['body_outfit','head','body_collar_foreground'],logical_slots=['body_outfit','head_style'],material_policy='Opaque intended body/head interiors: decoded alpha>=240 becomes255; original RGB/files and soft outer edges retained.',clocks=dict(source=[190,180,190,180,190,180,190,600],game=[100]*7+[600]),terminal_hold_ms=600,planted_surface_budget_px=6,receiver_endpoint_budget_px=3,recovery_overshoot_budget_px=2,phase_warning_fraction=.25,minimum_distinct_body_drawings=6,selected_pose_map=selected,selection_policy='Source0 and7 are same rest state. Use drawn7 for both; replace rejected overshoot key6 with an explicit early rest hold at1.114s. Six unique body drawings/eight logical exposures; no per-frame translations, warps or interpolated frames.',rejected_or_unselected=['attempt1: clipping/phase','attempt2 raw key6: recovery overshoot','repair sheet: changes unrelated art and row placement; retained, not selected'],anatomical_image_joint_detection=False,user_new_art_approved=False,full_factory_production_pass=False)
data['forefoot_observation_rois_native']={'far':[100,435,175,479],'near':[70,477,275,506]}
data['support_observation_scope']='Fixed visible forefoot bands, not complete shoe segmentation or inferred anatomical joints; compare both native extrema at display scale and actual raster extrema.'
(P/'motion-contract.json').write_text(json.dumps(data,indent=2)+'\n');print('PREPARED_BOUND_SOURCE8_AND_SPARSE_REVIEW6')
