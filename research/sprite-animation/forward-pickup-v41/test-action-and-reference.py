"""Real-source negative cases and actual GIF timing/binding regressions."""
import copy
import importlib.util
import json
import tempfile
from pathlib import Path
from PIL import Image

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
action=module('pickup-source-action');gif=module('approved-gif-compare');floor=module('visible-floor-surfaces')
data=json.loads((P/'source/source.json').read_text());checks=[]
def check(name,ok):
    assert ok,name
    checks.append(dict(name=name,pass_=True))
check('real source and actual capture hashes pass',action.audit(data,P)['source_action_pass'])
for title,mutate,key in [
    ('floating crystal',lambda x:x['frames'][0]['object_center'].__setitem__(2,.15),'object_rests_on_ground_before_contact'),
    ('ground prop teleport',lambda x:x['frames'][2]['object_center'].__setitem__(0,.2),'ground_object_does_not_teleport'),
    ('wrong picking wrist',lambda x:x['frames'][3]['points'].__setitem__('right.grip',copy.deepcopy(x['frames'][3]['points']['left.palm'])),'right_grip_socket_contact'),
    ('free hand falsely touches prop',lambda x:x['frames'][3]['points']['left.palm'].__setitem__('world_xyz',list(x['frames'][3]['grasp_socket_world'])),'free_left_hand_is_not_grasping'),
    ('carried item detaches',lambda x:x['frames'][5]['object_center'].__setitem__(1,-.2),'item_follows_same_grip_after_contact'),
    ('planted toe slides',lambda x:x['frames'][4]['points']['right.toe']['world_xyz'].__setitem__(0,-.4),'planted_source_feet'),
    ('projection tampering',lambda x:x['frames'][4]['points']['head']['xy']['rear'].__setitem__(0,100),'independent_projection'),
    ('changed capture binding',lambda x:x['frames'][4]['views']['rear'].__setitem__('sha256','0'*64),'actual_capture_hashes'),
    ('changed ownership capture binding',lambda x:x['frames'][4]['owner_pass'].__setitem__('sha256','0'*64),'actual_capture_hashes'),
    ('misparented right hand',lambda x:x['bone_definitions'][[b[0] for b in x['bone_definitions']].index('right.hand')].__setitem__(3,'left.lowerarm'),'right_hand_reaches_forward'),
    ('wrist mistaken for grip',lambda x:x.__setitem__('palm_to_grip_world',[0,0,0]),'wrist_palm_and_grip_not_confused'),
]:
    d=copy.deepcopy(data);mutate(d);check(title+' rejected',not action.audit(d,P)['checks'][key])
c=json.loads((P/'attempt3-comparison-contract.json').read_text())
with tempfile.TemporaryDirectory() as td:
    r=gif.run(c,ROOT,td)
    check('actual approved GIF clock decoded, including terminal600ms',r['reference_durations_ms']==[190,180,190,180,190,180,190,600])
    check('clock pass does not promote unreviewed painting',not r['comparison_checks_pass'])
    d=copy.deepcopy(c);d['durations_ms']=[100]*8
    check('same mean FPS cannot replace approved exposures',not gif.run(d,ROOT,td)['checks']['exact_approved_clock'])
    d=copy.deepcopy(c);d['reference']['sha256']='0'*64
    check('different reference binding rejected',not gif.run(d,ROOT,td)['checks']['approved_gif_hash'])
    d=copy.deepcopy(c);d['approval_receipt']['sha256']='0'*64
    check('unbound acceptance receipt rejected',not gif.run(d,ROOT,td)['checks']['immutable_user_acceptance_binding'])
    d=copy.deepcopy(c);d['candidate_frames'][2]['sha256']='0'*64
    check('changed PNG binding rejected',not gif.run(d,ROOT,td)['checks']['all_candidate_hashes'])
    d=copy.deepcopy(c);d['observations']=dict(frame_sha256=[x['sha256'] for x in c['candidate_frames']],planted_surfaces={'near':[[0,0],[0,0],None,[0,0],[0,0],[0,0],[0,0],[0,0]]})
    check('occluded image foot abstains instead of approving',not gif.run(d,ROOT,td)['checks']['support_near'])
    d['observations']['planted_surfaces']['near']=[[0,0],[0,0],[0,0],[0,0],[7,0],[0,0],[0,0],[0,0]]
    check('7px foot shift fails unchanged6px limit',not gif.run(d,ROOT,td)['checks']['support_near'])
    d['observations']['manual_action_review']={'pass':True,'frame_sha256':['bad']*8}
    check('manual review cannot transfer to other pixels',not gif.run(d,ROOT,td)['checks']['current_exact_image_action_review'])
    d['required_support_tracks']=['near','far'];d['observations']['manual_action_review']={'pass':True,'frame_sha256':[f['sha256'] for f in c['candidate_frames']]}
    check('manual pass cannot omit required planted surfaces',not gif.run(d,ROOT,td)['checks']['declared_planted_supports_observed'])
check('recovery bob is reported from actual XY rather than fitted away',gif.trajectory([[0,0],[0,3],[0,9],[0,10],[0,7],[0,8],[0,2],[0,0]],3)['recovery_downward_reversal_px']==1)
im=Image.open(P/'attempt6-review/native-00.png').convert('RGBA');windows=dict(near=dict(roi=[65,455,235,510],edge='min'),far=dict(roi=[245,440,330,510],edge='max'))
check('frozen feet alone are not a production approval',floor.run([im]*8,windows)['surface_checks_pass'] and not floor.run([im]*8,windows)['production_pass'])
shift=im.transform(im.size,Image.Transform.AFFINE,(1,0,-7,0,1,0),Image.Resampling.NEAREST)
check('actual shifted boot pixels fail6px at1to1',not floor.run([im,shift]+[im]*6,windows)['surface_checks_pass'])
check('missing actual material abstains',not floor.observe(Image.new('RGBA',im.size),windows['near']['roi'],'min')['known'])
check('clipped contour abstains',not floor.observe(im,[110,455,235,510],'min')['known'])
images=[Image.open(P/f'attempt6-review/native-{i:02}.png') for i in range(8)]
check('real native6 feet fail unchanged budget',not floor.run(images,windows,6,.87)['surface_checks_pass'])
(P/'test-receipt.json').write_text(json.dumps(dict(checks=checks,production_pass=False),indent=2)+'\n')
print(f'{len(checks)} actual-source/reference negative checks passed')
