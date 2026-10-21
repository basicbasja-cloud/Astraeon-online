"""Inspect source geometry and joins; diagnostics never confer art approval."""
import json,math
from pathlib import Path
from statistics import median
from patch001_factory import BASE,read,write,receipt_valid


def audit():
    ledger=read(BASE/'ledger.json');results=[]
    for job in ledger['guide_jobs'].values():
        if not receipt_valid(job):
            results.append({'job':job['id'],'uses':job['uses'],'status':'CAPTURE_MISSING_OR_STALE'});continue
        manifest=read(BASE/'guides'/job['id']/'manifest.json');views=manifest['views'];frames=next(iter(views.values()))['frames'];names=list(frames[0]['world_landmarks'])
        def delta(a,b,n):return math.dist(a['world_landmarks'][n],b['world_landmarks'][n])
        steps={n:[delta(a,b,n)for a,b in zip(frames,frames[1:])]for n in names}
        seam={n:delta(frames[0],frames[-1],n)for n in names}
        mismatch=0.;offscreen=[]
        for direction,view in views.items():
            for i,f in enumerate(view['frames']):
                mismatch=max(mismatch,max(delta(f,frames[i],n)for n in names))
                for n,p in {**f['landmarks'],**{k:v for k,v in f['weapon_guide'].items()if isinstance(v,list)}}.items():
                    if any(not math.isfinite(v)for v in p)or not(0<=p[0]<job['resolution']and 0<=p[1]<job['resolution']):offscreen.append({'direction':direction,'frame':i,'point':n})
        joins=[]
        for i,(a,b)in enumerate(zip(frames,frames[1:])):
            if a['action']!=b['action']or ('transition_weight'in a)!=('transition_weight'in b):joins.append({'frames':[i,i+1],'actions':[a['action'],b['action']],'steps_m':{n:round(delta(a,b,n),6)for n in names}})
        result={'job':job['id'],'uses':job['uses'],'status':'GEOMETRY_DIAGNOSTIC_REQUIRES_VISUAL_REVIEW','cross_camera_world_pose_difference_m':mismatch,'offscreen_points':offscreen,'endpoint_distance_m':seam,'source_segment_joins':joins,'steps':{n:{'max_m':max(v,default=0),'median_m':median(v)if v else 0,'max_step_frames':[v.index(max(v)),v.index(max(v))+1]if v else None}for n,v in steps.items()},'loop':job['loop'],'owner_approved':False,'notes':['Loop last-to-first distance represents one sample interval, not necessarily a discontinuity.','Large attack steps can be valid fast strikes; no blanket velocity threshold passes or fails human motion.','Foot bone height is not a sole-contact or weight-bearing proof.']}
        results.append(result)
    report={'status':'DIAGNOSTIC_ONLY_NOT_RELEASE_APPROVAL','jobs':results,'captured':sum(r['status']!='CAPTURE_MISSING_OR_STALE'for r in results),'missing_or_stale':sum(r['status']=='CAPTURE_MISSING_OR_STALE'for r in results),'world_pose_inconsistencies':[r['job']for r in results if r.get('cross_camera_world_pose_difference_m',0)>1e-5],'jobs_with_offscreen_points':[r['job']for r in results if r.get('offscreen_points')]}
    write(BASE/'source-geometry-audit.json',report)
    print(json.dumps({k:v for k,v in report.items()if k!='jobs'},indent=2))


if __name__=='__main__':audit()
