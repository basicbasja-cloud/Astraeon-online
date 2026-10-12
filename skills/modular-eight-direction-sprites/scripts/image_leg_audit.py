"""Generated-image pixel evidence plus mandatory source-occlusion ownership review.

No automatic semantic label detector: source IDs are true rendered geometry,
generated-art owner labels require independent image tracing, or remain blocked.
"""
import copy,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def proximal_defaults():
    return {s:{'kind':'unknown','review':'unconfirmed','pelvis_edge_xy':None,'trace':[],'notes':''} for s in ['r','l']}
def depth_defaults():return {'near_side':'unknown','cue':'unknown','cue_xy':None,'review':'unconfirmed','notes':''}
def verify_user_acceptance(case):
    if 'user_acceptance_path' not in case:return None
    p=Path(case['user_acceptance_path'])
    if sha(p)!=case['user_acceptance_sha256']:raise ValueError('Stale user acceptance receipt')
    m=json.loads(p.read_text())
    if m['authority']!='user' or m['scope']!='leg_readability_in_this_sheet' or m['facing']!=case['facing']:raise ValueError('Wrong user acceptance scope/view')
    if sha(m['raw_image'])!=m['raw_image_sha256']:raise ValueError('Changed user approved source image')
    if m['frame_sha256']!=[f['image_sha256'] for f in case['frames']]:raise ValueError('User acceptance does not apply to these painted frames')
    return m
def bind_profile_depth(case,path):
    m=json.loads(Path(path).read_text())
    if m['canvas']!=case['canvas'] or m['blend_sha256']!=case['source_blend_sha256'] or m['motion_sha256']!=case['source_motion_sha256']:raise ValueError('Wrong profile depth source')
    case['profile_depth_path']=str(path);case['profile_depth_sha256']=sha(path)
    for f in case['frames']:
        rows=[r for r in m['records'] if r['view']==case['facing'] and r['source_index']==f['source_index']]
        if len(rows)!=1:raise ValueError('Profile depth pose missing')
        f['profile_depth_record']=copy.deepcopy(rows[0])
def verify_profile_depth(case):
    if 'profile_depth_path' not in case:return False
    p=Path(case['profile_depth_path'])
    if sha(p)!=case['profile_depth_sha256']:raise ValueError('Stale profile depth index')
    m=json.loads(p.read_text())
    if m['canvas']!=case['canvas'] or m['blend_sha256']!=case['source_blend_sha256'] or m['motion_sha256']!=case['source_motion_sha256']:raise ValueError('Wrong profile depth source')
    for f in case['frames']:
        rows=[r for r in m['records'] if r['view']==case['facing'] and r['source_index']==f['source_index']]
        if len(rows)!=1 or f.get('profile_depth_record')!=rows[0]:raise ValueError('Modified profile depth pose')
        for name,path in rows[0]['paths'].items():
            if sha(path)!=rows[0]['sha256'][name]:raise ValueError('Stale profile depth pixels')
    return True
def bind_owners(case,path):
    m=json.loads(Path(path).read_text())
    if m['canvas']!=case['canvas']:raise ValueError('Owner mask and artwork canvas differ')
    if m['blend_sha256']!=case['source_blend_sha256'] or m['motion_sha256']!=case['source_motion_sha256']:raise ValueError('Owner masks belong to another rig/motion')
    case['source_occlusion_path']=str(path);case['source_occlusion_sha256']=sha(path)
    for f in case['frames']:
        records=[r for r in m['records'] if r['view']==case['facing'] and r['source_index']==f['source_index']]
        if len(records)!=1:raise ValueError('Missing/ambiguous source owner pose')
        r=records[0];f['owner_paths']=r['paths'].copy();f['occlusion_reviews']=copy.deepcopy(r['events']);f.setdefault('review_issues',[])
        for event in f['occlusion_reviews']:event.update(art_trace=[],trace_review='unconfirmed')
        f.setdefault('proximal_reviews',proximal_defaults());f.setdefault('depth_review',depth_defaults())
def verify_owners(case):
    if 'source_occlusion_path' not in case:return False
    p=Path(case['source_occlusion_path'])
    if sha(p)!=case['source_occlusion_sha256']:raise ValueError('Stale owner-index hash')
    m=json.loads(p.read_text())
    if m['canvas']!=case['canvas']:raise ValueError('Owner mask and artwork canvas differ')
    if m['blend_sha256']!=case['source_blend_sha256'] or m['motion_sha256']!=case['source_motion_sha256']:raise ValueError('Wrong owner rig/motion')
    for f in case['frames']:
        records=[r for r in m['records'] if r['view']==case['facing'] and r['source_index']==f['source_index']]
        if len(records)!=1:raise ValueError('Wrong owner pose')
        r=records[0]
        if f['owner_paths']!=r['paths'] or len(f['occlusion_reviews'])!=len(r['events']):raise ValueError('Missing/changed crossing review')
        for name,path in r['paths'].items():
            if sha(path)!=r['sha256'][name]:raise ValueError('Stale source owner pixels')
        with Image.open(r['paths']['visible-id']) as im:ids=np.array(im)
        for event,base in zip(f['occlusion_reviews'],r['events']):
            for k in ['id','expected_foreground','source_xy','source_box','pixels']:
                if event[k]!=base[k]:raise ValueError('Modified source crossing ownership')
            x,y=event['source_xy']
            if int(ids[y,x])!=({'r':1,'l':2}[event['expected_foreground']]):raise ValueError('Source ID disagrees at crossing')
            if event['observed_foreground'] not in ['r','l','unknown'] or event['review'] not in ['confirmed','unconfirmed']:raise ValueError('Bad crossing review')
            if event.get('trace_review','unconfirmed') not in ['confirmed','unconfirmed']:raise ValueError('Bad image trace review')
    return True
def opaque(arr,xy):
    x,y=map(lambda v:int(round(v)),xy);h,w=arr.shape[:2]
    return int(arr[max(0,y-1):min(h,y+2),max(0,x-1):min(w,x+2),3].max(initial=0))
def point_valid(arr,xy):
    return isinstance(xy,list) and len(xy)==2 and all(isinstance(v,(int,float)) and np.isfinite(v) for v in xy) and 0<=xy[0]<arr.shape[1] and 0<=xy[1]<arr.shape[0]
def attachment_review(f,arr,canvas,has_depth,is_profile):
    flags=[];sides={};threshold=24*canvas[0]/512
    for side in ['r','l']:
        p=f.get('proximal_reviews',proximal_defaults())[side];trace=p['trace'];edge=p['pelvis_edge_xy'];knee=f['points']['knee_'+side]
        usable=len(trace)>=3 and all(point_valid(arr,xy) for xy in trace) and point_valid(arr,edge)
        support=None;connected=False
        if usable:
            pts=np.concatenate([np.linspace(a,b,32) for a,b in zip(trace,trace[1:])]);support=float(np.mean([opaque(arr,xy)>=64 for xy in pts]))
            connected=np.linalg.norm(np.array(trace[0])-edge)<=12*canvas[0]/512 and knee['visibility']!='unknown' and knee['xy'] is not None and np.linalg.norm(np.array(trace[-1])-knee['xy'])<=threshold
        valid=usable and connected and support>=.8 and p['kind'] in ['visible_junction','readable_occlusion'] and p['review']=='confirmed'
        sides[side]={'confirmed_visible_attachment_evidence':bool(valid),'kind':p['kind'],'pixel_support_fraction':support,'not_internal_hip_detection':True}
        if not valid:flags.append('pelvis_to_thigh_identity_requires_image_review:'+side)
    traces=f.get('proximal_reviews',proximal_defaults())
    if traces['r']['trace'] and traces['r']['trace']==traces['l']['trace']:flags.append('both_proximal_sides_use_identical_trace')
    d=f.get('depth_review',depth_defaults());cue=d['cue_xy']
    paired=d['review']=='confirmed' and d['near_side'] in ['r','l'] and d['cue'] in ['t_junction','contour_overlap'] and point_valid(arr,cue) and opaque(arr,cue)>=64
    mismatch=has_depth and paired and d['near_side']!=f['profile_depth_record']['hip_near_side']
    if is_profile and not has_depth:flags.append('profile_metric_depth_source_missing')
    if not paired:flags.append('paired_pelvis_depth_readability_requires_image_review')
    if mismatch:flags.append('proximal_near_side_disagrees_with_metric_source')
    complete=all(p['confirmed_visible_attachment_evidence'] for p in sides.values()) and paired and not mismatch and not (is_profile and not has_depth) and not flags
    return {'sides':sides,'depth_cue_review':d,'source_depth_verified':has_depth,'semantic_detection_automatic':False,'complete':complete,'mismatch':mismatch,'flags':flags}
def audit_images(case):
    owners=verify_owners(case);has_depth=verify_profile_depth(case);acceptance=verify_user_acceptance(case);frames=[];all_flags=[];rejected=False;teal_track=[]
    for f in case['frames']:
        path=Path(f['image'])
        if sha(path)!=f['image_sha256']:raise ValueError('Image audit has stale artwork')
        with Image.open(path) as im:arr=np.array(im.convert('RGBA'))
        attachment=attachment_review(f,arr,case['canvas'],has_depth,case['facing'] in ['E','W'])
        flags=attachment['flags'].copy();rejected|=attachment['mismatch'];landmarks=[];segments=[];crossings=[]
        rgb=arr[:,:,:3].astype(float);rr,gg,bb=np.moveaxis(rgb,-1,0)
        yy=np.arange(arr.shape[0])[:,None]
        teal=(gg>rr*1.18)&(bb>rr*1.05)&(gg>=bb*.65)&(np.maximum.reduce([rr,gg,bb])>35)&(arr[:,:,3]>128)&(yy>arr.shape[0]*.38)&(yy<arr.shape[0]*.86)
        ty,tx=np.nonzero(teal);anchor=None
        if len(tx)>=32:
            ps=[f['points'].get('hip_'+s,{}) for s in ['r','l']]
            center_x=np.mean([p['xy'][0] for p in ps]) if all(p.get('xy') is not None and p.get('visibility')!='unknown' for p in ps) else arr.shape[1]/2
            anchor={'pixels':len(tx),'centroid':[float(tx.mean()),float(ty.mean())],'relative_x_to_pelvis_or_cell_root':float(tx.mean()-center_x),
                'method':'Teal-like lower-body palette pixels; heuristic appearance anchor, not an anatomical detector'}
            teal_track.append((f['key'],anchor['relative_x_to_pelvis_or_cell_root']))
        for n,p in f['points'].items():
            if p['xy'] is None or p['visibility']=='unknown':continue
            alpha=opaque(arr,p['xy']);landmarks.append({'joint':n,'alpha_3x3_max':alpha,'visibility':p['visibility']})
            if p['visibility']=='observed' and alpha<64:flags.append('observed_landmark_not_supported_by_image:'+n)
        for side in ['r','l']:
            for a,b in [('hip','knee'),('knee','ankle'),('ankle','toe')]:
                a,b=a+'_'+side,b+'_'+side;p,q=f['points'][a],f['points'][b]
                if not all(v['xy'] is not None and v['visibility']!='unknown' for v in [p,q]):continue
                pts=np.array(p['xy'])[None,:]+np.linspace(.08,.92,48)[:,None]*(np.array(q['xy'])-p['xy'])[None,:]
                support=[opaque(arr,xy)>=64 for xy in pts];coverage=float(np.mean(support))
                segments.append({'chain':[a,b],'raster_foreground_fraction':coverage,'semantic_identity_verified':False})
                if coverage<.6 and p['visibility']==q['visibility']=='observed':flags.append('drawn_chain_leaves_character_silhouette:'+a+'>'+b)
        if not owners:flags.append('source_occlusion_owner_proof_missing')
        for event in f.get('occlusion_reviews',[]):
            confirmed=event['review']=='confirmed' and event['observed_foreground']!='unknown';xy=event['art_xy']
            valid=xy is not None and len(xy)==2 and all(np.isfinite(v) for v in xy) and 0<=xy[0]<arr.shape[1] and 0<=xy[1]<arr.shape[0]
            supported=valid and opaque(arr,xy)>=64
            trace=event.get('art_trace',[])
            trace_valid=len(trace)>=3 and all(isinstance(p,list) and len(p)==2 and all(np.isfinite(v) for v in p) and 0<=p[0]<arr.shape[1] and 0<=p[1]<arr.shape[0] for p in trace)
            trace_support=None;cross_distance=None
            if trace_valid:
                pts=np.concatenate([np.linspace(a,b,32) for a,b in zip(trace,trace[1:])]);trace_support=float(np.mean([opaque(arr,p)>=64 for p in pts]))
                cross_distance=float(np.linalg.norm(pts-np.array(xy),axis=1).min()) if valid else None
            traced=trace_valid and event.get('trace_review')=='confirmed' and trace_support>=.8 and cross_distance is not None and cross_distance<=16*case['canvas'][0]/512
            state='unresolved'
            if not confirmed or not supported:flags.append('overlap_owner_requires_image_review:'+event['id'])
            elif event['observed_foreground']!=event['expected_foreground']:
                state='mismatch';flags.append('overlap_foreground_owner_mismatch:'+event['id']);rejected=True
            elif not traced:flags.append('overlap_chain_trace_requires_image_review:'+event['id'])
            elif not attachment['complete'] or f.get('identity_review')!='confirmed':
                state='foreground_order_only';flags.append('local_trace_does_not_establish_pelvis_identity:'+event['id'])
            else:state='reviewed_match'
            crossings.append({**event,'art_pixel_supported':bool(supported),'trace_foreground_support_fraction':trace_support,'crossing_distance_to_trace_px':cross_distance,'semantic_trace_is_manual':True,'result':state})
        for issue in f.get('review_issues',[]):
            if issue.get('image_sha256')!=f['image_sha256']:raise ValueError('Reviewer issue bound to different pixels')
            if issue.get('confirmed'):
                flags.append('confirmed_image_review_error:'+issue['code']);rejected=True
        frames.append({'key':f['key'],'landmarks':landmarks,'segments':segments,'crossings':crossings,'proximal_attachment_review':attachment,'teal_palette_anchor':anchor,'flags':flags})
        all_flags.extend({'key':f['key'],'type':flag} for flag in flags)
    margin=12*case.get('canvas',[512,512])[0]/512
    if teal_track and min(v for k,v in teal_track)<-margin and max(v for k,v in teal_track)>margin:
        all_flags.append({'type':'teal_palette_anchor_changes_body_side','scope':'clip','requires_visual_confirmation':True})
    return {'schema':'generated-leg-image-audit-v1','status':'REJECTED' if rejected else 'REVIEW_REQUIRED' if all_flags else 'SCOPED_IMAGE_REVIEW_COMPLETE',
        'visual_status':'REJECTED' if rejected else 'USER_ACCEPTED_LEG_READABILITY' if acceptance else 'USER_ACCEPTANCE_PENDING',
        'user_acceptance':acceptance,'acceptance_is_not_hidden_joint_measurement':True,
        'source_visible_and_amodal_owner_pixels_verified':owners,'semantic_detector_used':False,
        'method':'Actual generated RGBA evidence, silhouette support and independently reviewed foreground ownership at true source crossings. No inferred pass on occluded legs.',
        'frames':frames,'flags':all_flags,'release_ready':False}
def evidence(case,audit,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for f,report in zip(case['frames'],audit['frames']):
        with Image.open(f['image']) as im:art=im.convert('RGBA')
        source=Image.open(f['owner_paths']['visible-color']).convert('RGBA') if 'owner_paths' in f else None
        for i,event in enumerate(report['crossings']):
            sx,sy=event['source_xy'];ax,ay=event['art_xy'] if event['art_xy'] is not None else [sx,sy]
            size=160;card=Image.new('RGB',(320,190),'#292c31');d=ImageDraw.Draw(card)
            for column,(im,x,y) in enumerate([(source,sx,sy),(art,ax,ay)]):
                if im is None:continue
                crop=im.crop((int(x)-80,int(y)-80,int(x)+80,int(y)+80));bg=Image.new('RGBA',(size,size),'#292c31');bg.alpha_composite(crop);card.paste(bg.convert('RGB'),(column*160,30))
            d.text((5,3),'Source '+event['expected_foreground']+' / art '+event['observed_foreground'],fill='#ece8df')
            d.text((5,15),'Art crop: marked pixels' if event['art_xy'] is not None else 'Art crop: source coordinates, UNCALIBRATED',fill='#deb76b')
            if len(event.get('art_trace',[]))>=2:d.line([(160+int(x-ax)+80,30+int(y-ay)+80) for x,y in event['art_trace']],fill='#fff',width=2)
            card.save(out/f'{f["key"]:02}-crossing-{i:02}.png')
