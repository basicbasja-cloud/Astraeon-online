"""Audit cyclic visible landmark spacing, separately from limb identity.

SHA-bound manual observations are measurements with uncertainty, not inferred
hidden bones. Image hashes, all durations and the last->first edge are mandatory.
No image alignment, resampling, pose interpolation or art modification occurs.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cyclic_differences(points, durations_ms):
    """Per-exposure forward velocity, plus cyclic nonuniform second differences."""
    p = np.asarray(points, dtype=float)
    dt = np.asarray(durations_ms, dtype=float) / 1000
    if len(p) < 3 or len(p) != len(dt) or not np.isfinite(p).all() or not np.isfinite(dt).all() or np.any(dt <= 0):
        raise ValueError('At least three finite samples and positive exposure durations required')
    delta = np.roll(p, -1, axis=0) - p
    velocity = delta / dt.reshape((-1,) + (1,) * (p.ndim - 1))
    centers = (dt + np.roll(dt, 1)) / 2
    acceleration = (velocity - np.roll(velocity, 1, axis=0)) / centers.reshape((-1,) + (1,) * (p.ndim - 1))
    return delta, velocity, acceleration


def image_patch_tracking(spec):
    """Independent pixel-feature diagnostic on one declared coherent surface ROI.

    Similarities are measurements only: never warp/repair any output image. A
    face turn, pattern change or low match count is inconclusive, not a pass.
    """
    try:
        import cv2
    except ImportError:
        return {'status': 'DEPENDENCY_MISSING', 'required': 'opencv-python-headless 4.11.0.86'}
    x0,y0,x1,y1 = spec['texture_roi']
    width,height = spec['canvas']
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError('Invalid texture ROI')
    mask = np.zeros((height,width), np.uint8)
    mask[y0:y1,x0:x1] = 255
    def gray(f):
        with Image.open(f['image']) as image:
            a = np.array(image.convert('RGBA'))
        rgb = np.rint(a[:,:,:3]*a[:,:,3:4]/255+39*(1-a[:,:,3:4]/255)).astype(np.uint8)
        return cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    sift = cv2.SIFT_create(nfeatures=1800)
    ka,da = sift.detectAndCompute(gray(spec['frames'][0]),mask)
    center = np.array([[(x0+x1)/2,(y0+y1)/2,1]],float)
    rows = []
    for i,f in enumerate(spec['frames']):
        row = {'key':i,'status':'INCONCLUSIVE'}
        kb,db = sift.detectAndCompute(gray(f),mask)
        if da is None or db is None:
            rows.append(row);continue
        pairs = cv2.BFMatcher().knnMatch(da,db,k=2)
        good = [pair[0] for pair in pairs if len(pair)==2 and pair[0].distance<.72*pair[1].distance]
        if len(good)<8:
            rows.append(row);continue
        a=np.float32([ka[g.queryIdx].pt for g in good]);b=np.float32([kb[g.trainIdx].pt for g in good])
        cv2.setRNGSeed(0)
        mat,inliers=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=4000,confidence=.999)
        if mat is None:
            rows.append(row);continue
        valid=inliers[:,0].astype(bool)
        errors=np.linalg.norm(a@mat[:,:2].T+mat[:,2]-b,axis=1)
        if valid.sum()<8 or valid.mean()<.5 or np.median(errors[valid])>1.5 or np.linalg.det(mat[:,:2])<=0:
            row.update(matches=len(good),inliers=int(valid.sum()));rows.append(row);continue
        import math
        row.update(status='SCOPED_PIXEL_FEATURE_MATCH',matches=len(good),inliers=int(valid.sum()),
                   median_inlier_error_px=float(np.median(errors[valid])),
                   reference_patch_center_in_frame_px=(center@mat.T)[0].tolist(),
                   scale=math.hypot(mat[0,0],mat[1,0]),rotation_degrees=math.degrees(math.atan2(mat[1,0],mat[0,0])),
                   matrix=mat.tolist())
        rows.append(row)
    result={'method':'Fixed-ROI SIFT/RANSAC reference-to-frame similarities; no image warp',
            'roi':[x0,y0,x1,y1],'opencv':cv2.__version__,'frames':rows,
            'art_modified':False,'anatomy_pass':False,
            'status':'SCOPED_PIXEL_FEATURE_TRACKING' if all(r['status']=='SCOPED_PIXEL_FEATURE_MATCH' for r in rows) else 'INCONCLUSIVE'}
    if result['status']=='SCOPED_PIXEL_FEATURE_TRACKING':
        p=[r['reference_patch_center_in_frame_px'] for r in rows]
        delta,_,_=cyclic_differences(p,[f['duration_ms'] for f in spec['frames']])
        result['center_step_px']=np.linalg.norm(delta,axis=1).tolist()
        result['max_center_step_px']=max(result['center_step_px'])
        result['last_to_first_center_step_px']=result['center_step_px'][-1]
        result['scale_range']=[min(r['scale'] for r in rows),max(r['scale'] for r in rows)]
    return result


def palette_patch_probe(spec):
    """Character-specific surface-region occupancy, not a semantic head/leg model."""
    try:
        import cv2
    except ImportError:
        return {'status':'DEPENDENCY_MISSING'}
    contract=spec['palette_patch_probe'];x0,y0,x1,y1=contract['roi']
    width,height=spec['canvas']
    if not(0<=x0<x1<=width and 0<=y0<y1<=height):raise ValueError('Invalid palette ROI')
    rows=[]
    for i,f in enumerate(spec['frames']):
        with Image.open(f['image']) as image:
            a=np.array(image.convert('RGBA'))
        rgb=a[:,:,:3].astype(float)
        hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2HSV)
        keep=(a[:,:,3]>128)&(hsv[:,:,1]<=contract['max_hsv_saturation_255'])&(hsv[:,:,2]>=contract['min_hsv_value_255'])
        keep&=(rgb[:,:,2]>=rgb[:,:,1]*contract['min_blue_green_ratio'])&(rgb[:,:,0]>=rgb[:,:,1]*contract['min_red_green_ratio'])
        roi=np.zeros((height,width),bool);roi[y0:y1,x0:x1]=True;keep&=roi
        closed=cv2.morphologyEx(keep.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        n,labels,stats,centers=cv2.connectedComponentsWithStats(closed)
        if n<2:
            rows.append({'key':i,'status':'INCONCLUSIVE'});continue
        largest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));component=labels==largest
        original=component&keep;ys,xs=np.where(original)
        if len(xs)<contract['minimum_pixels']:
            rows.append({'key':i,'status':'INCONCLUSIVE'});continue
        rows.append({'key':i,'status':'DECLARED_PALETTE_REGION_MEASURED','pixels':len(xs),
            'centroid_px':[float(xs.mean()),float(ys.mean())],
            'bounds_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
    result={'status':'DECLARED_PALETTE_REGION_MEASURED' if all(r['status']=='DECLARED_PALETTE_REGION_MEASURED' for r in rows) else 'INCONCLUSIVE',
            'contract':contract,'frames':rows,'art_modified':False,'anatomy_pass':False,
            'scope':'Palette-region centroid/occupancy only. Costume, palette, lighting, turn or occlusion changes invalidate interpretation; recalibrate for each character. Not recovered head or bone position.'}
    if result['status']=='DECLARED_PALETTE_REGION_MEASURED':
        delta,_,_=cyclic_differences([r['centroid_px'] for r in rows],[f['duration_ms'] for f in spec['frames']])
        result['centroid_step_px']=np.linalg.norm(delta,axis=1).tolist();result['max_centroid_step_px']=max(result['centroid_step_px']);result['last_to_first_centroid_step_px']=result['centroid_step_px'][-1]
        if 'max_step_px' in contract:
            result['declared_budget_px']=contract['max_step_px']
            result['edges_over_declared_budget']=[{'from':i,'to':(i+1)%len(rows),'step_px':v} for i,v in enumerate(result['centroid_step_px']) if v>contract['max_step_px']]
            result['registration_warning']=bool(result['edges_over_declared_budget'])
    return result


def audit(spec):
    frames = spec['frames']
    duration = [f['duration_ms'] for f in frames]
    cyclic_differences(np.zeros((len(frames), 2)), duration)
    for f in frames:
        if sha(f['image']) != f['sha256']:
            raise ValueError('Changed artwork: observations must be remeasured')
        with Image.open(f['image']) as image:
            width,height=image.size
        if [width,height] != spec['canvas']:
            raise ValueError('Canvas differs from declared fixed registration')
        for item in f['landmarks'].values():
            if item is None:
                continue
            x, y = item['xy']
            if not (0 <= x < width and 0 <= y < height) or not np.isfinite(item['uncertainty_px']) or item['uncertainty_px'] < 0:
                raise ValueError('Invalid visible landmark observation')
    report = {'schema': 'walk-visible-continuity-report-v1', 'label': spec['label'],
              'frame_count': len(frames), 'cycle_ms': sum(duration),
              'art_pixels_modified': False, 'semantic_leg_identity_checked': False,
              'hidden_bones_inferred': False, 'contact_lock_checked': False,
              'ground_root_pixel_registration': 'UNRESOLVED_REQUIRES_AUTHORITATIVE_ANCHOR_AND_OBSERVATIONS',
              'status': 'DIAGNOSTIC_REQUIRES_VISUAL_REVIEW', 'landmarks': {}, 'edges': []}
    names = sorted(set().union(*(f['landmarks'] for f in frames)))
    for name in names:
        observed = [f['landmarks'].get(name) for f in frames]
        if any(o is None for o in observed):
            report['landmarks'][name] = {'status': 'INCOMPLETE_OBSERVATIONS'}
            continue
        p = np.array([o['xy'] for o in observed], float)
        u = np.array([o['uncertainty_px'] for o in observed], float)
        if name not in spec.get('tracked_landmarks', []):
            report['landmarks'][name] = {'status': 'UNTRACKED_VISIBLE_SAMPLES',
                'positions_px': p.tolist(), 'uncertainty_px': u.tolist(),
                'trajectory_computed': False}
            continue
        delta, velocity, acceleration = cyclic_differences(p, duration)
        lengths = np.linalg.norm(delta, axis=1)
        # Worst-case bound for two independently uncertain visible observations.
        adjusted = np.maximum(0, lengths - u - np.roll(u, -1))
        report['landmarks'][name] = {'status': 'MEASURED_VISIBLE_POINTS', 'positions_px': p.tolist(),
            'uncertainty_px': u.tolist(), 'step_px': lengths.tolist(),
            'uncertainty_adjusted_step_px': adjusted.tolist(), 'velocity_px_per_s': velocity.tolist(),
            'acceleration_px_per_s2': acceleration.tolist(), 'max_step_px': float(lengths.max()),
            'rms_step_px': float(np.sqrt(np.mean(lengths ** 2))),
            'last_to_first_step_px': float(lengths[-1]),
            'max_cyclic_second_difference_px': float(np.max(np.linalg.norm(
                np.roll(p,-1,axis=0)-2*p+np.roll(p,1,axis=0),axis=1)))}
        if spec.get('reference_body_height_px'):
            if spec['reference_body_height_px'] <= 0:
                raise ValueError('Reference body height must be positive')
            report['landmarks'][name]['max_step_as_reference_height_fraction'] = float(lengths.max()/spec['reference_body_height_px'])
    for i, f in enumerate(frames):
        j = (i + 1) % len(frames)
        report['edges'].append({'from': i, 'to': j, 'duration_ms': duration[i],
            'loop_seam': j == 0, 'generation_batch_changed': f.get('batch') != frames[j].get('batch')})
    if all(f['landmarks'].get('ankle_a') and f['landmarks'].get('ankle_b') for f in frames):
        # UNORDERED span: cannot be used as proof of right/left ownership.
        span = np.array([abs(f['landmarks']['ankle_a']['xy'][0] - f['landmarks']['ankle_b']['xy'][0]) for f in frames])
        report['unordered_ankle_span_px'] = span.tolist()
        report['unordered_ankle_span_normalized_to_own_max'] = (span / max(1, span.max())).tolist()
        if spec.get('source_depth_index'):
            source_path = Path(spec['source_depth_index'])
            if sha(source_path) != spec['source_depth_index_sha256']:
                raise ValueError('Changed source index')
            index = json.loads(source_path.read_text())
            records = {(r['view'], r['source_index']): r for r in index['records']}
            source = []
            for f in frames:
                r = records[(spec['facing'], f['source_index'])]
                source.append(abs(r['bones']['foot_r']['xy'][0]-r['bones']['foot_l']['xy'][0]))
            normalized = np.array(source)/max(source)
            report['source_unordered_ankle_span_px'] = source
            report['source_unordered_ankle_span_normalized_to_own_max'] = normalized.tolist()
            report['normalized_span_absolute_difference'] = abs(span/max(1,span.max())-normalized).tolist()
            report['source_comparison_scope'] = 'Unsigned ankle spacing profile only, normalized once per entire clip. Different limb proportions/acting need review. Not source-pose or anatomical PASS.'
            if spec.get('span_profile_budget') is not None:
                budget=spec['span_profile_budget']
                if budget<0:raise ValueError('Invalid span profile budget')
                report['span_profile_budget']=budget
                report['span_profile_warning_frames']=[i for i,v in enumerate(report['normalized_span_absolute_difference']) if v>budget]
    if spec.get('texture_roi'):
        report['image_patch_tracking'] = image_patch_tracking(spec)
    if spec.get('palette_patch_probe'):
        report['palette_patch_probe'] = palette_patch_probe(spec)
    return report


def main():
    parser = argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--observations', type=Path)
    mode.add_argument('--init-from-frames', type=Path)
    parser.add_argument('--frame-ms',type=float,default=75)
    parser.add_argument('--label',default='new-character-unreviewed')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.init_from_frames:
        files=sorted(args.init_from_frames.glob('*.png'))
        if len(files)<3 or args.frame_ms<=0:raise ValueError('Need at least three fixed-canvas frames and positive explicit duration')
        if args.out.exists():raise ValueError('Refuse overwriting an existing review contract')
        sizes=[]
        for p in files:
            with Image.open(p) as image:sizes.append(list(image.size))
        if any(s!=sizes[0] for s in sizes):raise ValueError('Normalize the fixed canvas first')
        spec={'schema':'walk-visible-observations-v1','label':args.label,'canvas':sizes[0],
              'registration':'Declare actual logical root/camera; do not infer from changing sprite bounds',
              'tracked_landmarks':['eye','belt','root'],
              'landmark_semantics':{'eye':'Same visible pupil throughout the facing; unknown when occluded',
                  'belt':'Same visible buckle/waist feature, not an arbitrary garment centroid',
                  'root':'Authoritative logical ground anchor; do not substitute belly, head or lowest alpha pixel',
                  'ankle_a_and_b':'Unordered visible band centers for span only; not anatomical side tracks'},
              'scope':'New character template: all measurements unknown. Calibrate ROIs, timing, uncertainty and surface semantics before use.',
              'frames':[{'image':str(p),'sha256':sha(p),'duration_ms':args.frame_ms,
                         'landmarks':{n:None for n in ['eye','belt','root','ankle_a','ankle_b']}} for p in files]}
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(spec,indent=2)+'\n')
        print('Created unknown-observation contract for',len(files),'frames');return
    spec = json.loads(args.observations.read_text())
    result = audit(spec)
    result['observation_sha256'] = sha(args.observations)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['label'], result['frame_count'], 'frames; visual review required')


if __name__ == '__main__':
    main()
