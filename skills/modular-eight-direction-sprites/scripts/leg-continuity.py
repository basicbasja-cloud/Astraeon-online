"""Source-guided anatomical leg QA. Manual observations, not an image pose detector."""
import argparse,base64,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

JOINTS=[f'{part}_{side}' for side in ['r','l'] for part in ['hip','knee','ankle','toe']]
SOURCE={'hip':'thigh','knee':'calf','ankle':'foot','toe':'ball_leaf'}
COLORS={'r':'#3591ff','l':'#f59045'}
WEIGHTS={'observed':1.,'estimated':.25,'unknown':0.}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def other(n):return n[:-1]+('l' if n[-1]=='r' else 'r')
def project(p,size):
    x,y,z=p;angle=math.pi/4;el=math.atan2(2.92-.64,4);scale=size/1.58
    xx=x*math.cos(angle)-y*math.sin(angle);yy=x*math.sin(angle)+y*math.cos(angle)
    return [size/2+xx*scale,size/2-(yy*math.sin(el)+(z-.64)*math.cos(el))*scale]
def init_case(motion,frames,keys):
    m=json.loads(Path(motion).read_text());samples=[];canvas=None
    for k,index in enumerate(keys):
        path=Path(frames)/f'{k:02}.png'
        with Image.open(path) as im:size=im.size
        if size[0]!=size[1]:raise ValueError('Square master required')
        if canvas is not None and canvas!=size:raise ValueError('Mixed logical canvases')
        canvas=size;f=m['frames'][index]
        ref={n:project(f['in_place_joints'][SOURCE[n.rsplit('_',1)[0]]+'_'+n[-1]],size[0]) for n in JOINTS}
        samples.append({'key':k,'source_index':index,'time_seconds':f['time_seconds'],
            'image':str(path),'image_sha256':sha(path),'reference':ref,
            'source_ankle_z':{s:f['in_place_joints']['foot_'+s][2] for s in ['r','l']},
            'identity_review':'unconfirmed','notes':'',
            'points':{n:{'xy':None,'visibility':'unknown','uncertainty_px':0.} for n in JOINTS}})
    return {'schema':'anatomical-leg-review-v1','source_motion_path':str(motion),'source_motion_sha256':sha(motion),
        'source_joint_map':SOURCE.copy(),
        'source_blend_path':str(Path(motion).parent/'original-modular-walk.blend'),
        'source_blend_sha256':sha(Path(motion).parent/'original-modular-walk.blend'),
        'source_replay_path':str(Path(motion).parent/'saved-rig-check.json'),
        'source_replay_sha256':sha(Path(motion).parent/'saved-rig-check.json'),
        'source_glb_sha256':m['source_glb_sha256'],'source_capture_sha256':m['capture_sha256'],
        'canvas':list(canvas),'facing':'SE','duration_seconds':m['duration_seconds'],
        'coordinate_origin':'Top-left, master pixels; anatomical sides, never screen sides',
        'thresholds':{'pose_px':16.*canvas[0]/512,'swap_margin_px':8.*canvas[0]/512,'velocity_residual_px_per_s':60.*canvas[0]/512},
        'method':'Human-marked visible joints, explicit uncertainty, frozen global diagnostic scale and source trajectory comparison. Not a pretrained image detector.',
        'frames':samples,'release_ready':False}
def validate_case(c,verify_images=False):
    if c.get('schema')!='anatomical-leg-review-v1':raise ValueError('Unknown schema')
    if c.get('source_joint_map')!=SOURCE:raise ValueError('Wrong anatomical source joint map')
    fs=c['frames'];w,h=c['canvas'];duration=c['duration_seconds']
    if c.get('facing')!='SE' or w!=h or not isinstance(w,int) or w<=0:raise ValueError('Unsupported facing/canvas')
    if len(fs)<2 or not math.isfinite(duration) or duration<=0:raise ValueError('Invalid clip')
    previous=-1
    for k,f in enumerate(fs):
        t=f['time_seconds']
        if f['key']!=k or not math.isfinite(t) or not previous<t<duration:raise ValueError('Invalid key/time')
        previous=t
        if f['identity_review'] not in ['unconfirmed','confirmed']:raise ValueError('Invalid identity state')
        if set(f['reference'])!=set(JOINTS) or set(f['points'])!=set(JOINTS):raise ValueError('Missing/extra anatomical joint names')
        for n in JOINTS:
            r=f['reference'][n]
            if len(r)!=2 or not all(math.isfinite(v) for v in r):raise ValueError('Invalid source reference')
            p=f['points'][n];v=p['visibility'];u=p['uncertainty_px']
            if v not in WEIGHTS or not math.isfinite(u) or u<0:raise ValueError('Invalid visibility/uncertainty')
            xy=p['xy']
            if xy is not None and (len(xy)!=2 or not all(math.isfinite(v) for v in xy) or not (0<=xy[0]<w and 0<=xy[1]<h)):
                raise ValueError('Joint outside master or nonfinite')
            if v!='unknown' and xy is None:raise ValueError('Visible/estimated point has no coordinate')
        if verify_images:
            p=Path(f['image'])
            with Image.open(p) as im:size=im.size
            if sha(p)!=f['image_sha256'] or list(size)!=c['canvas']:raise ValueError('Stale image hash/canvas')
    for v in c['thresholds'].values():
        if not math.isfinite(v) or v<=0:raise ValueError('Invalid threshold')
    if verify_images:
        path=Path(c['source_motion_path'])
        if sha(path)!=c['source_motion_sha256']:raise ValueError('Stale source bone/motion hash')
        m=json.loads(path.read_text())
        if sha(c['source_blend_path'])!=c['source_blend_sha256'] or sha(c['source_replay_path'])!=c['source_replay_sha256']:
            raise ValueError('Stale baked rig/replay hash')
        replay=json.loads(Path(c['source_replay_path']).read_text())
        if replay['blend_sha256']!=c['source_blend_sha256'] or not replay['gate_pose_replay'] or replay['max_saved_pose_replay_error']>2e-5:
            raise ValueError('Baked rig replay not verified')
        if m['duration_seconds']!=duration or m['source_glb_sha256']!=c['source_glb_sha256'] or m['capture_sha256']!=c['source_capture_sha256']:
            raise ValueError('Source provenance/clock mismatch')
        for f in fs:
            ref=m['frames'][f['source_index']]
            if abs(ref['time_seconds']-f['time_seconds'])>1e-9:raise ValueError('Wrong source pose time')
            for n in JOINTS:
                expected=project(ref['in_place_joints'][SOURCE[n.rsplit('_',1)[0]]+'_'+n[-1]],w)
                if not np.allclose(expected,f['reference'][n],rtol=0,atol=1e-8):raise ValueError('Modified bone reference projection')
            for s in ['r','l']:
                if f['source_ankle_z'][s]!=ref['in_place_joints']['foot_'+s][2]:raise ValueError('Modified source foot height')
def usable(p):return p['xy'] is not None and WEIGHTS[p['visibility']]>0
def center(f,actual):
    if not actual:return (np.array(f['reference']['hip_r'])+f['reference']['hip_l'])/2,0.
    ps=[f['points']['hip_'+s] for s in ['r','l']]
    if not all(usable(p) for p in ps):return None,None
    return np.mean([p['xy'] for p in ps],axis=0),sum(p['uncertainty_px'] for p in ps)/2
def diagnostic_scale(fs):
    ratios=[]
    for f in fs:
        sums=[0.,0.];count=0
        for s in ['r','l']:
            for a,b in [('hip','knee'),('knee','ankle'),('ankle','toe')]:
                a,b=a+'_'+s,b+'_'+s;p,q=f['points'][a],f['points'][b]
                if usable(p) and usable(q):
                    sums[0]+=np.linalg.norm(np.array(p['xy'])-q['xy'])
                    sums[1]+=np.linalg.norm(np.array(f['reference'][a])-f['reference'][b]);count+=1
        if count==6 and sums[1]>1:ratios.append(sums[0]/sums[1])
    return float(np.median(ratios)) if ratios else 1.,len(ratios)
def frame_cost(f,scale,swap=False):
    gc,unc=center(f,True);sc,_=center(f,False);res=[]
    if gc is None:return None,[]
    for n,p in f['points'].items():
        if not usable(p):continue
        sn=other(n) if swap else n
        raw=float(np.linalg.norm(np.array(p['xy'])-gc-scale*(np.array(f['reference'][sn])-sc)))
        adjusted=max(0.,raw-p['uncertainty_px']-unc)
        res.append({'joint':n,'raw_error_px':raw,'error_after_uncertainty_px':adjusted,'weight':WEIGHTS[p['visibility']]})
    if not res:return None,[]
    cost=math.sqrt(sum(x['weight']*x['error_after_uncertainty_px']**2 for x in res)/sum(x['weight'] for x in res))
    return cost,res
def raw_pose_cost(res):
    return math.sqrt(sum(x['weight']*x['raw_error_px']**2 for x in res)/sum(x['weight'] for x in res)) if res else None
def transition(f,g,dt,scale,swap_next=False):
    fc,fu=center(f,True);gc,gu=center(g,True);fs,_=center(f,False);gs,_=center(g,False)
    if fc is None or gc is None:return None,0
    residuals=[]
    for n,p in f['points'].items():
        nxt=other(n) if swap_next else n;q=g['points'][nxt]
        if not usable(p) or not usable(q):continue
        actual=(np.array(q['xy'])-gc)-(np.array(p['xy'])-fc)
        expected=scale*((np.array(g['reference'][n])-gs)-(np.array(f['reference'][n])-fs))
        raw=float(np.linalg.norm(actual-expected))/dt
        error=max(0.,raw-(p['uncertainty_px']+q['uncertainty_px']+fu+gu)/dt)
        residuals.append((error,min(WEIGHTS[p['visibility']],WEIGHTS[q['visibility']]),raw))
    if not residuals:return None,0
    return (math.sqrt(sum(e*e*w for e,w,raw in residuals)/sum(w for e,w,raw in residuals)),len(residuals),
            math.sqrt(sum(raw*raw*w for e,w,raw in residuals)/sum(w for e,w,raw in residuals)))
def analyze(c):
    validate_case(c);fs=c['frames'];scale,scale_samples=diagnostic_scale(fs);limits=c['thresholds'];per=[];flags=[]
    observed=sum(p['visibility']=='observed' and usable(p) for f in fs for p in f['points'].values())
    measured=sum(usable(p) for f in fs for p in f['points'].values());point_pass=raw_pass=point_total=0
    for f in fs:
        own,res=frame_cost(f,scale);swapped,_=frame_cost(f,scale,True);raw=raw_pose_cost(res)
        visible={s:sum(f['points'][n]['visibility']=='observed' for n in JOINTS if n.endswith(s)) for s in ['r','l']}
        ambiguous=own is None or min(visible.values())<2 or f['identity_review']!='confirmed'
        local=[]
        if own is None:local.append('insufficient_pelvis_or_joint_observations')
        elif own>limits['pose_px']:local.append('source_pose_deviation')
        elif raw is not None and raw>limits['pose_px']:local.append('source_pose_difference_inside_annotation_uncertainty')
        if own is not None and swapped is not None and own-swapped>limits['swap_margin_px']:
            local.append('opposite_side_pose_fits_better_uncertain_identity' if ambiguous else 'possible_leg_label_or_pose_swap')
        if ambiguous:local.append('anatomical_identity_unconfirmed')
        for r in res:
            point_total+=1;point_pass+=r['error_after_uncertainty_px']<=limits['pose_px'];raw_pass+=r['raw_error_px']<=limits['pose_px']
        per.append({'key':f['key'],'identity_review':f['identity_review'],'observed_per_side':visible,
            'claimed_identity_rmse_px':own,'claimed_identity_raw_rmse_px':raw,'exchanged_identity_rmse_px':swapped,'point_errors':res,'flags':local})
        flags.extend({'key':f['key'],'type':x} for x in local)
    transitions=[]
    for k,f in enumerate(fs):
        g=fs[(k+1)%len(fs)];dt=(g['time_seconds']-f['time_seconds'])%c['duration_seconds']
        result=transition(f,g,dt,scale);exchanged=transition(f,g,dt,scale,True)
        error,count=result[:2];raw=result[2] if len(result)>2 else None;swapped=exchanged[0];local=[]
        if error is None:local.append('continuity_unmeasurable')
        elif error>limits['velocity_residual_px_per_s']:local.append('trajectory_residual_jump')
        elif raw is not None and raw>limits['velocity_residual_px_per_s']:local.append('trajectory_difference_inside_annotation_uncertainty')
        if error is not None and swapped is not None and (error-swapped)*dt>limits['swap_margin_px']:
            local.append('next_pose_side_exchange_fits_better')
        transitions.append({'from':k,'to':g['key'],'includes_loop_seam':k==len(fs)-1,'dt_seconds':dt,
            'measured_correspondences':count,'residual_px_per_s':error,'raw_residual_px_per_s':raw,'exchanged_next_residual_px_per_s':swapped,'flags':local})
        flags.extend({'transition':[k,g['key']],'type':x} for x in local)
    complete=measured==len(fs)*8 and observed==len(fs)*8 and all(f['identity_review']=='confirmed' for f in fs)
    return {'schema':'leg-continuity-report-v1','status':'REVIEW_REQUIRED' if flags or not complete else 'SCOPED_2D_MEASUREMENTS_WITHIN_BUDGET',
        'method':c['method'],'source_motion_sha256':c['source_motion_sha256'],
        'source_blend_sha256':c['source_blend_sha256'],'source_replay_sha256':c['source_replay_sha256'],
        'source_glb_sha256':c['source_glb_sha256'],'source_capture_sha256':c['source_capture_sha256'],
        'reference':'Measured 3D bones of the actual baked original rig projected with its fixed camera; no screenshot-estimated source skeleton',
        'thresholds':limits,'observed_coverage_percent':100*observed/(len(fs)*8),
        'measured_including_estimates_percent':100*measured/(len(fs)*8),
        'measured_points_within_declared_pose_budget_percent':100*point_pass/point_total if point_total else None,
        'unadjusted_measured_points_within_pose_budget_percent':100*raw_pass/point_total if point_total else None,
        'percentage_is_not_anatomy_accuracy':True,'diagnostic_global_positive_scale':scale,'scale_fit_complete_frame_count':scale_samples,
        'alignment_scope':'Pelvis-relative QA only; no rotation, reflection or per-pose scale. Artwork unchanged. Root registration and world contacts not validated.',
        'frames':per,'transitions':transitions,'flags':flags,'all_identity_confirmed':all(f['identity_review']=='confirmed' for f in fs),
        'foot_contact_verified':False,'hidden_anatomy_verified':False,'release_ready':False}
def overlay(c,out):
    out.mkdir(parents=True,exist_ok=True);scale,_=diagnostic_scale(c['frames']);s=c['canvas'][0]
    board=Image.new('RGB',(s*len(c['frames']),s+30),'#25282d')
    for f in c['frames']:
        im=Image.open(f['image']).convert('RGBA');bg=Image.new('RGBA',im.size,'#25282d');bg.alpha_composite(im);d=ImageDraw.Draw(bg)
        gc,_=center(f,True);sc,_=center(f,False)
        for side,color in COLORS.items():
            for a,b in [('hip','knee'),('knee','ankle'),('ankle','toe')]:
                a,b=a+'_'+side,b+'_'+side;p,q=f['points'][a],f['points'][b]
                if usable(p) and usable(q):d.line([tuple(p['xy']),tuple(q['xy'])],fill=color,width=3)
                if gc is not None:
                    pts=[tuple(gc+scale*(np.array(f['reference'][n])-sc)) for n in [a,b]]
                    d.line(pts,fill='#92a294',width=1)
            for n,p in f['points'].items():
                if n[-1]!=side or not usable(p):continue
                x,y=p['xy'];u=p['uncertainty_px']
                if u:d.ellipse((x-u,y-u,x+u,y+u),outline=color,width=1)
                d.ellipse((x-4,y-4,x+4,y+4),fill=color);d.text((x+7,y-8),n,fill=color)
        bg.convert('RGB').save(out/f'{f["key"]:02}-legs.png');board.paste(bg.convert('RGB'),(s*f['key'],30))
    ImageDraw.Draw(board).text((10,8),'BLUE anatomical right / ORANGE anatomical left / muted green source guide; circles = declared uncertainty',fill='#eeeeee')
    board.save(out/'leg-review-board.png')
def build_html(c,report,path):
    template=Path(__file__).with_name('leg-review.html').read_text()
    images=['data:image/png;base64,'+base64.b64encode(Path(f['image']).read_bytes()).decode() for f in c['frames']]
    payload={'case':c,'report':report,'images':images}
    path.write_text(template.replace('/*__PAYLOAD__*/',json.dumps(payload).replace('<','\\u003c')))
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('init');q.add_argument('--motion',type=Path,required=True);q.add_argument('--frames',type=Path,required=True);q.add_argument('--keys',required=True);q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('check');q.add_argument('--case',type=Path,required=True);q.add_argument('--out',type=Path,required=True);q.add_argument('--html',type=Path)
    a=p.parse_args()
    if a.cmd=='init':
        if a.out.exists():raise ValueError('Do not overwrite existing annotations')
        a.out.write_text(json.dumps(init_case(a.motion,a.frames,[int(x) for x in a.keys.split(',')]),indent=2)+'\n');return
    c=json.loads(a.case.read_text());validate_case(c,True);r=analyze(c);a.out.mkdir(parents=True,exist_ok=True)
    r['source_blend_replay_and_image_hashes_verified']=True
    (a.out/'continuity-report.json').write_text(json.dumps(r,indent=2)+'\n');overlay(c,a.out)
    if a.html:build_html(c,r,a.html)
    print('LEG_QA',r['status'],'observed coverage',r['observed_coverage_percent'],'flags',len(r['flags']))
if __name__=='__main__':main()
