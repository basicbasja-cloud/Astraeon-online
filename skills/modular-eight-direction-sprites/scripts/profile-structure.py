"""Independent image comparison around an approved pelvis/thigh structure.

Finds structural deviations, not semantic leg identity. Never upgrades unknown
anatomy to PASS. Registration is one diagnostic similarity, never a pose repair.
Requires OpenCV 4.11 headless, NumPy, Pillow; run with the dependency path set.
"""
import argparse,json,math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
from image_leg_audit import sha,verify_user_acceptance,verify_profile_depth

def gray_image(path):
    arr=np.array(Image.open(path).convert('RGBA'));alpha=arr[:,:,3:4]/255
    rgb=np.rint(arr[:,:,:3]*alpha+39*(1-alpha)).astype(np.uint8)
    return arr,cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
def compare(reference,candidate,spec):
    a,ga=gray_image(reference);b,gb=gray_image(candidate)
    if a.shape!=b.shape:raise ValueError('Reference and candidate canvases differ; normalize by declared grid first')
    h,w=ga.shape;mask=np.zeros((h,w),np.uint8);x0,y0,x1,y1=spec['registration_roi'];mask[y0:y1,x0:x1]=255
    sift=cv2.SIFT_create(nfeatures=2500);ka,da=sift.detectAndCompute(ga,mask);kb,db=sift.detectAndCompute(gb,None)
    result={'method':'Torso SIFT/RANSAC similarity registration then symmetric edge-distance in declared pelvis/thigh ROIs',
        'status':'INCONCLUSIVE','semantic_leg_swap_detected':False,'anatomy_pass':False,'art_pixels_modified':False,'regions':[],
        'opencv':cv2.__version__,'thresholds':spec['thresholds'],'registration':None}
    if da is None or db is None:return result,None,None,None
    pairs=cv2.BFMatcher().knnMatch(db,da,k=2);good=[m for pair in pairs if len(pair)==2 for m,n in [pair] if m.distance<.72*n.distance]
    if len(good)<12:return result,None,None,None
    x=np.float32([kb[m.queryIdx].pt for m in good]);y=np.float32([ka[m.trainIdx].pt for m in good]);cv2.setRNGSeed(0)
    mat,inliers=cv2.estimateAffinePartial2D(x,y,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=4000,confidence=.999)
    if mat is None:return result,None,None,None
    valid=inliers[:,0].astype(bool);scale=math.hypot(mat[0,0],mat[1,0]);angle=math.degrees(math.atan2(mat[1,0],mat[0,0]));errors=np.linalg.norm(x@mat[:,:2].T+mat[:,2]-y,axis=1)
    result['registration']={'matrix':mat.tolist(),'matches':len(good),'inliers':int(valid.sum()),'inlier_fraction':float(valid.mean()),'median_inlier_error_px':float(np.median(errors[valid])),'scale':scale,'rotation_degrees':angle,'reflection_allowed':False,'leg_fit_used':False}
    if valid.sum()<12 or valid.mean()<.45 or np.median(errors[valid])>2.5 or not .85<=scale<=1.15 or abs(angle)>5 or np.linalg.det(mat[:,:2])<=0:return result,None,None,None
    registered=cv2.warpAffine(gb,mat,(w,h),borderValue=39);registered_alpha=cv2.warpAffine(b[:,:,3],mat,(w,h))
    ea=cv2.Canny(cv2.GaussianBlur(ga,(5,5),1),35,90);eb=cv2.Canny(cv2.GaussianBlur(registered,(5,5),1),35,90)
    dista=cv2.distanceTransform(255-ea,cv2.DIST_L2,5);distb=cv2.distanceTransform(255-eb,cv2.DIST_L2,5)
    for name,box in spec['structure_rois'].items():
        x0,y0,x1,y1=box;roi=np.zeros((h,w),bool);roi[y0:y1,x0:x1]=True
        comparable=roi&(a[:,:,3]>128)&(registered_alpha>128);expected=int((roi&(a[:,:,3]>128)).sum());coverage=float(comparable.sum()/expected) if expected else 0
        vals=np.r_[distb[(ea>0)&comparable],dista[(eb>0)&comparable]]
        if len(vals)<32 or coverage<.8:result['regions'].append({'name':name,'status':'INCONCLUSIVE','foreground_coverage':coverage});continue
        mean=float(vals.mean());p95=float(np.percentile(vals,95));fraction=float(np.mean(vals>spec['thresholds']['edge_radius_px']));t=spec['thresholds']
        changed=mean>t['mean_distance_px'] or p95>t['p95_distance_px'] or fraction>t['outside_radius_fraction']
        result['regions'].append({'name':name,'status':'STRUCTURAL_DIFFERENCE_REQUIRES_REVIEW' if changed else 'REFERENCE_STRUCTURE_MATCH_WITHIN_BUDGET','foreground_coverage':coverage,'sampled_edge_pixels':len(vals),'symmetric_mean_distance_px':mean,'symmetric_p95_distance_px':p95,'fraction_outside_declared_radius':fraction})
    result['status']='STRUCTURAL_DIFFERENCE_REQUIRES_REVIEW' if any(r['status']=='STRUCTURAL_DIFFERENCE_REQUIRES_REVIEW' for r in result['regions']) else 'INCONCLUSIVE' if any(r['status']=='INCONCLUSIVE' for r in result['regions']) else 'REFERENCE_STRUCTURE_MATCH_WITHIN_BUDGET'
    return result,registered,ea,eb
def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    spec=json.loads(args.reference.read_text());case=json.loads(Path(spec['approved_case']).read_text());receipt=verify_user_acceptance(case)
    if receipt is None:raise ValueError('No exact-image user-approved reference')
    if spec['facing']!=case['facing'] or spec['source_index']!=case['frames'][spec['key']]['source_index']:raise ValueError('Reference pose/view mismatch')
    if not verify_profile_depth(case):raise ValueError('Missing bound metric profile source')
    ref=Path(case['frames'][spec['key']]['image'])
    if sha(ref)!=spec['reference_frame_sha256']:raise ValueError('Changed approved reference')
    result,registered,ea,eb=compare(ref,args.candidate,spec);args.out.mkdir(parents=True,exist_ok=True)
    result.update(reference_spec_sha256=sha(args.reference),reference_image_sha256=sha(ref),candidate_image_sha256=sha(args.candidate),scope='Same character, facing and source phase as approved reference; different costume/view/style needs a new reference. Edge disagreement is not proof of semantic swap.')
    (args.out/'structure-report.json').write_text(json.dumps(result,indent=2)+'\n')
    if registered is not None:
        board=Image.new('RGB',(1536,550),'#272727');draw=ImageDraw.Draw(board);refim=Image.open(ref).convert('RGBA');cand=Image.open(args.candidate).convert('RGBA')
        for column,im in enumerate([refim,cand]):bg=Image.new('RGBA',im.size,'#272727');bg.alpha_composite(im);board.paste(bg.convert('RGB'),(column*512,30))
        colors=np.dstack([np.where(ea>0,255,0),np.where(eb>0,255,0),np.where(eb>0,255,0)]).astype(np.uint8);board.paste(Image.fromarray(colors),(1024,30))
        for name,box in spec['structure_rois'].items():draw.rectangle((1024+box[0],30+box[1],1024+box[2],30+box[3]),outline='white');draw.text((1024+box[0],30+box[1]-12),name,fill='white')
        for x,label in [(8,'USER APPROVED REFERENCE'),(520,'CANDIDATE - UNCHANGED'),(1032,'REGISTERED EDGES: ref red / candidate cyan')]:draw.text((x,8),label,fill='white')
        board.save(args.out/'image-structure-comparison.png')
    print('PROFILE_STRUCTURE',result['status'])
if __name__=='__main__':main()
