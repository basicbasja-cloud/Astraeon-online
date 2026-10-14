"""Exact whole-body crop selection, one shared transform, bound visible receivers."""
from pathlib import Path
import hashlib,json,math
from PIL import Image

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
bind=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
neck=json.loads((P.parent/'neck-motion-v36/neck-bind.json').read_text())
source_path=P.parent/'pickup-pilot-v31/source/source.json';source=json.loads(source_path.read_text())
observations=json.loads((P/'collar-observations.json').read_text())
selection=json.loads((P/'selection.json').read_text())
rest=json.loads((P/'attempt2-probe.json').read_text())['observations'][7]['skin_stub_surface_centroid']
# One rest-bank calibration, never a per-pose or per-generation fit.
scale=300/(488-rest[1]);body_matrix=[scale,0,0,scale,211-198*scale,480-488*scale]
out=P/'body-frames';out.mkdir(exist_ok=True)
for job in {j for j,i in selection['review']}|{2}:
    sheet=Image.open(P/f'attempt{job}-raw.png').convert('RGBA')
    assert sheet.size==(1536,1024)
    for i in range(8):sheet.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512)).save(out/f'job{job}-{i:02}.png')
def apply(m,p):return[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]
def mid(pair):return[(pair[0][k]+pair[1][k])/2 for k in [0,1]]
def angle(pair):a,b=pair;return math.atan2(b[1]-a[1],b[0]-a[0])
def record(index,job,art):
    points=observations[str(job)][str(art)]['visible_collar_lip_points_native']
    target=[apply(body_matrix,p) for p in points];src=neck['head_insertion_points_native'];a=mid(src);b=mid(target)
    turn=angle(target)-angle(src);c=math.cos(turn)*.11;sn=math.sin(turn)*.11
    matrix=[c,sn,-sn,c,b[0]-c*a[0]+sn*a[1],b[1]-sn*a[0]-c*a[1]]
    v=[points[1][k]-points[0][k] for k in [0,1]];length=math.hypot(*v);u=[v[0]/length,v[1]/length];n=[-u[1],u[0]]
    fg=[[points[0][k]-u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3 for k in [0,1]],[points[1][k]+u[k]*3+n[k]*22 for k in [0,1]],[points[0][k]-u[k]*3+n[k]*22 for k in [0,1]]]
    return dict(index=index,source_time_seconds=source['frames'][index]['source_time_seconds'],body=bind(out/f'job{job}-{art:02}.png'),raw_sheet=bind(P/f'attempt{job}-raw.png'),raw_art_index=art,generation_job=job,body_matrix=body_matrix,head_matrix=matrix,body_collar_lip_points_native=points,observed_receiver_surface_xy=b,collar_foreground_polygon_native=fg,head_turn_radians=turn,observation='Manually reviewed visible outer collar lip, +/-3rawpx; source bones and hidden painted joints are separate',hold=index in [0,7])
contract=dict(schema='coherent-outfit-neck-motion-v1',canvas=[384,512],source=bind(source_path),head=neck['head'],head_insertion_points_native=neck['head_insertion_points_native'],head_scale=.11,body_uniform_rest_matrix=body_matrix,
    bank_rest_calibration=dict(generation_job=2,raw_art_index=7,observed_cap_centroid=rest,observed_near_toe_sole_native=[198,488],target_near_toe_sole=[211,480],neck_to_sole_height=300,all_frames_share_one_transform=True,other_jobs_receive_no_individual_registration=True),
    variants=dict(raw8=[record(i,2,i) for i in range(8)],review=[record(i,*pair) for i,pair in enumerate(selection['review'])]),
    draw_order=['body_outfit','head','body_collar_foreground'],logical_slots=['body_outfit','head_style'],
    material_policy='Opaque intended interiors alpha>=240; source RGB/files and soft edges unchanged. No background-matte threshold rescue.',
    clocks=dict(source=[190,180,190,180,190,180,190,600],game=[100]*7+[600]),terminal_hold_ms=600,
    planted_surface_budget_px=6,receiver_endpoint_budget_px=3,recovery_overshoot_budget_px=2,phase_warning_fraction=.25,minimum_distinct_body_drawings=7,
    forefoot_observation_rois_native=dict(far=[100,435,175,479],near=[70,477,275,506]),
    lateral_recovery_monotonic_expected=True,
    lateral_recovery_policy='This authored crouch/reach returns steadily up/right to rest; a left reversal is unintended. Not a universal rule for RPG actions.',
    selected_pose_map=selection['review'],selection_policy=selection['policy'],anatomical_image_joint_detection=False,user_new_art_approved=False,full_factory_production_pass=False)
(P/'motion-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
print('EXACT_CROPS_BOUND_ONE_BODY_MATRIX_HEAD_SCALE_UNCHANGED')
