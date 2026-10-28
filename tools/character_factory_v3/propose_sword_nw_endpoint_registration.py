"""Propose one bounded whole-frame registration; never alter or approve source.

Mask centroids and the low body component are visual proposals, not certified
anatomical landmarks or planted contacts. All layers receive the same integer
translation; no pose, individual limb, asset layer or scale is independently fit.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
BINDING=BASE/'cutouts/f163f5e0b852f2767596/bindings.json'
INDEX=BASE/'cutout-store/index.json'
GUIDE=BASE/'guides/c297971fcef09188ff60/manifest.json'
TIMING=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/assembly-audit.json'
ROLES=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def alpha_centroid(im):
    mask=np.asarray(im.getchannel('A'))>127;y,x=np.nonzero(mask)
    if not len(x):raise ValueError('Empty alpha')
    return np.array([x.mean(),y.mean()])
def lower_component(im):
    mask=np.asarray(im.getchannel('A'))>127;mask[:530,:]=False
    labels,count=label(mask,np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0
    if not count or sizes.max()<100:raise ValueError('No identifiable lower-body component')
    y,x=np.nonzero(labels==sizes.argmax());return np.array([x.mean(),y.mean()])
def move(im,dx):
    alpha=im.getchannel('A').getbbox()
    if alpha and (alpha[0]+dx<0 or alpha[2]+dx>im.width):raise ValueError('Translation clips visible source')
    out=Image.new('RGBA',im.size);out.alpha_composite(im,(dx,0));return out

def build(output):
    if output.exists():raise ValueError('Choose a new candidate output')
    g=json.loads(GUIDE.read_text())['views']['NW']['frames'];timings=json.loads(TIMING.read_text())['durations_ms']
    bindings=json.loads(BINDING.read_text());store=json.loads(INDEX.read_text())
    records={row['index']:row for row in bindings['frames'] if row['direction']=='NW'}
    if set(records)!=set(range(16)):raise ValueError('Unexpected imported sequence')
    originals={}; pins={str(p.relative_to(ROOT)):sha(p) for p in (GUIDE,TIMING,BINDING,INDEX,Path(__file__).resolve())}
    for i in range(16):
        originals[i]={};record=records[i]
        for role in ROLES:
            a=store['assets'][record['assets'][role]]
            if a['role']!=role or a['pose_id']!=record['pose_id'] or a['camera_id']!=record['camera_id']:raise ValueError('Layer pose differs')
            oid=a['object'];p=(ROOT/store['objects'][oid]['file']).resolve()
            if not p.is_relative_to(ROOT):raise ValueError('Object outside repository')
            pins[str(p.relative_to(ROOT))]=sha(p);im=Image.open(p).convert('RGBA')
            if hashlib.sha256(im.tobytes()).hexdigest()!=oid:raise ValueError('Object pixels changed')
            originals[i][role]=im
    head_before=alpha_centroid(originals[14]['HeadHair']);head_after=alpha_centroid(originals[15]['HeadHair'])
    guide_head_delta=(np.array(g[15]['landmarks']['head'])-np.array(g[14]['landmarks']['head']))*.5
    dx=int(round(guide_head_delta[0]-(head_after-head_before)[0]))
    if not -16<=dx<=16:raise ValueError('Proposed shift exceeds bounded authoring limit')
    near_before=lower_component(originals[14]['BodyCostume']);near_after=lower_component(originals[15]['BodyCostume'])
    guide_foot_delta=(np.array(g[15]['landmarks']['foot_r'])-np.array(g[14]['landmarks']['foot_r']))*.5
    proposed_parts={r:move(originals[15][r],dx) for r in ROLES}
    output.mkdir(parents=True);(output/'frame15').mkdir()
    for role,im in proposed_parts.items():im.save(output/'frame15'/f'{role}.png')
    def compose(parts):
        im=Image.new('RGBA',(768,768))
        for role in ROLES:im.alpha_composite(parts[role])
        return im
    old_master=compose(originals[15]);new_master=compose(proposed_parts)
    if new_master.tobytes()!=move(old_master,dx).tobytes():raise ValueError('Common translation did not commute with recomposition')
    new_master.save(output/'frame15'/'Master.png')
    before=[];after=[]
    for i in range(16):
        old=compose(originals[i]);new=new_master if i==15 else old
        board=Image.new('RGB',(680,344),'#e6e6e6');draw=ImageDraw.Draw(board)
        for col,(label_text,img) in enumerate((('Original',old),('Registration candidate',new))):
            draw.text((col*340+6,4),f'{label_text} / {i:02}',fill='black');tile=img.crop((220,290,560,610));board.paste(tile,(col*340,24),tile)
        before.append(board)
    before[0].save(output/'comparison.gif',save_all=True,append_images=before[1:],duration=timings,loop=0,disposal=2)
    before[0].save(output/'comparison-slow.gif',save_all=True,append_images=before[1:],duration=[d*3 for d in timings],loop=0,disposal=2)
    before[15].resize((1360,688),Image.Resampling.NEAREST).save(output/'frame15-comparison-2x.png')
    factor=240/768
    measure=lambda p,q:round(float(p-q)*factor,4)
    raw_head=(head_after-head_before)[0];raw_foot=(near_after-near_before)[0]
    proof={'status':'PROPOSED_ONLY_NOT_APPROVED_OR_IMPORTED','view':'NW','frame':15,'previous_frame':14,'dx_author_pixels':dx,'dy_author_pixels':0,
        'scale_changed':False,'all_layers_same_transform':True,'source_modified':False,'pixel_clipping':False,'input':'actual imported Swordsman BasicAttack layers including selected long trail',
        'guide_head_dx_author':round(float(guide_head_delta[0]),4),'hair_centroid_dx_author_before':round(float(raw_head),4),'hair_centroid_dx_author_after':round(float(raw_head+dx),4),
        'hair_motion_residual_runtime_before':measure(raw_head,guide_head_delta[0]),'hair_motion_residual_runtime_after':measure(raw_head+dx,guide_head_delta[0]),
        'guide_foot_r_dx_author':round(float(guide_foot_delta[0]),4),'lower_component_dx_author_before':round(float(raw_foot),4),'lower_component_dx_author_after':round(float(raw_foot+dx),4),
        'lower_component_motion_residual_runtime_before':measure(raw_foot,guide_foot_delta[0]),'lower_component_motion_residual_runtime_after':measure(raw_foot+dx,guide_foot_delta[0]),
        'limitations':['Alpha centroid is not a verified head joint; hair shape can vary.','Lower-body component association to foot_r is provisional and requires visual landmark review.','Only one frame in one view; no proof of contact, other transitions, game rendering or ready pose.','GIF repeats a one-shot for comparison and is not seamless-loop validation.'],
        'source_hashes':pins,'contact_verified':False,'art_approved':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
    return {k:v for k,v in proof.items() if k!='source_hashes'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
