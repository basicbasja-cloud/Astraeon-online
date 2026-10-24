"""Audit source-frame transitions using the retained research continuity signals.

Loop seam distance is compared with observed internal steps, in runtime pixels.
Silhouette IoU is diagnostic only, especially for fast strikes. No art, anatomy,
held-weapon alignment or playable-package acceptance is inferred.
"""
import argparse,json,math
from pathlib import Path
from PIL import Image
from audit_sprite_candidate import _iou,RESEARCH_IOU_WARNING
from track_visible_cutouts import sha


def screen_points(record):
    result={k:list(v)for k,v in record['landmarks'].items()};prop=record.get('weapon_guide',{})
    result.update({'weapon_'+k:list(prop[k])for k in ['grip','tip','string_nock','arrow_tip']if k in prop})
    if any(len(v)!=2 or not all(math.isfinite(x)for x in v)for v in result.values()):raise ValueError('Invalid source screen point')
    return result


def step(a,b,factor):
    left=screen_points(a);right=screen_points(b)
    if set(left)!=set(right):raise ValueError('Source transition point set differs')
    values={key:math.dist(left[key],right[key])*factor for key in left}
    return {'maximum_runtime_px':max(values.values(),default=0),'points_runtime_px':values}


def temporal_view(rows,resolution,loop,runtime_size=240):
    if len(rows)<2:raise ValueError('At least two source samples required')
    if not math.isfinite(resolution)or resolution<=0 or not math.isfinite(runtime_size)or runtime_size<=0:raise ValueError('Invalid source or runtime resolution')
    factor=runtime_size/resolution;internal=[{'frames':[i,i+1],**step(a,b,factor)}for i,(a,b)in enumerate(zip(rows,rows[1:]))];seam=step(rows[-1],rows[0],factor);maximum=max(x['maximum_runtime_px']for x in internal);gap=seam['maximum_runtime_px'];suspect=bool(loop and gap>max(1.,1.5*maximum+.5))
    joins=[item for item in internal if rows[item['frames'][0]]['action']!=rows[item['frames'][1]]['action']]
    return {'internal_steps':internal,'maximum_internal_step_runtime_px':maximum,'loop_seam':seam if loop else None,'suspected_loop_reset':suspect,'segment_joins':joins,'first_to_last_for_nonloop_is_not_a_seam':not loop}


def audit(base,output,ledger_path=None):
    ledger_path=ledger_path or base/'ledger.json';ledger=json.loads(ledger_path.read_text());jobs=[];flags=[]
    for job in ledger['guide_jobs'].values():
        folder=base/'guides'/job['id'];path=folder/'manifest.json';manifest=json.loads(path.read_text())
        if {k:v for k,v in manifest['job'].items()if k!='uses'}!={k:v for k,v in job.items()if k!='uses'}:raise ValueError('Stale source guide geometry descriptor')
        views={}
        for direction,view in manifest['views'].items():
            rows=view['frames'];result=temporal_view(rows,job['resolution'],job['loop'])
            if job['loop']:
                first=Image.open(folder/direction/'000.png').convert('RGBA');last=Image.open(folder/direction/f'{len(rows)-1:03d}.png').convert('RGBA');result['first_last_silhouette_iou']=_iou(first,last)
            if result['suspected_loop_reset']:flags.append({'guide_job':job['id'],'direction':direction,'source_actions':job['source_actions'],'seam_runtime_px':result['loop_seam']['maximum_runtime_px'],'maximum_internal_step_runtime_px':result['maximum_internal_step_runtime_px']})
            views[direction]=result
        jobs.append({'guide_job':job['id'],'uses':job['uses'],'source_actions':job['source_actions'],'loop':job['loop'],'manifest_sha256':sha(path),'views':views})
    result={'status':'SOURCE_TEMPORAL_DIAGNOSTICS_NOT_ART_APPROVAL','implementation_sha256':sha(Path(__file__)),'research_continuity_implementation':'audit_sprite_candidate._iou','research_iou_warning':RESEARCH_IOU_WARNING,'runtime_size':240,'ledger_sha256':sha(ledger_path),'jobs_checked':len(jobs),'suspected_loop_resets':flags,'jobs':jobs,'runtime_admitted':False,'human_motion_or_grip_certified':False};output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ledger',type=Path);a=p.parse_args();r=audit(a.base,a.output,a.ledger);print(json.dumps({'jobs_checked':r['jobs_checked'],'suspected_loop_reset_views':len(r['suspected_loop_resets'])}))
