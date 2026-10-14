"""Audit declared 3D arm chains; never infer hidden anatomy from a sprite.

World-space angles catch a wrist which looks acceptable in one projection but
breaks in another. Image evidence and drawing acceptance are separate gates.
"""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np

def angle(a,b):
    a,b=np.asarray(a,float),np.asarray(b,float)
    if min(np.linalg.norm(a),np.linalg.norm(b))<1e-8:return None
    return math.degrees(math.acos(float(np.clip(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))

def audit(source,wrist_limit=60,elbow_limit=145):
    rows=[];errors=[]
    for f in source['frames']:
        row={'index':f['index'],'arms':{}}
        for side in ['left','right']:
            try:
                p={k:np.array(f['points'][side+'.'+k]['world_xyz'],float) for k in ['shoulder','elbow','wrist','palm']}
                u=p['elbow']-p['shoulder'];v=p['wrist']-p['elbow'];h=p['palm']-p['wrist']
                if not all(np.isfinite(q).all() for q in p.values()):raise ValueError('non-finite joint')
                bend=angle(u,v);wrist=angle(v,h)
                if bend is None or wrist is None:raise ValueError('degenerate arm/hand')
                row['arms'][side]=dict(elbow_flex_deg=bend,wrist_deviation_deg=wrist,lengths=[float(np.linalg.norm(x)) for x in [u,v,h]])
            except (KeyError,ValueError) as e:errors.append(dict(frame=f.get('index'),side=side,reason=str(e)))
        rows.append(row)
    complete=bool(rows) and not errors and all(set(r['arms'])=={'left','right'} for r in rows)
    max_wrist=max([a['wrist_deviation_deg'] for r in rows for a in r['arms'].values()],default=math.inf)
    max_elbow=max([a['elbow_flex_deg'] for r in rows for a in r['arms'].values()],default=math.inf)
    lengths={s:[float(np.ptp([r['arms'][s]['lengths'][j] for r in rows if s in r['arms']])) if any(s in r['arms'] for r in rows) else math.inf for j in range(3)] for s in ['left','right']}
    checks=dict(complete_nondegenerate_chains=complete,world_wrist_deviation=max_wrist<=wrist_limit,world_elbow_flex=max_elbow<=elbow_limit,constant_source_lengths=complete and max(v for x in lengths.values() for v in x)<1e-5)
    keys=['upperarm','forearm','hand'];declared=source.get('limb_lengths',{})
    checks['declared_lengths_match_vectors']=complete and all(k in declared for k in keys) and all(abs(a['lengths'][j]-declared[k])<1e-5 for r in rows for a in r['arms'].values() for j,k in enumerate(keys))
    # Explicitly bounded to this unrotated canonical world, never screen x sorting.
    checks['declared_canonical_owner_frame']=source.get('right_owner_world_negative_x') is True and complete and all(f['points']['right.shoulder']['world_xyz'][0]<f['points']['chest']['world_xyz'][0]<f['points']['left.shoulder']['world_xyz'][0] for f in source['frames'])
    safe=lambda v:float(v) if math.isfinite(v) else None
    return dict(checks=checks,source_arm_metrics_pass=all(checks.values()),frames=rows,errors=errors,max_wrist_deviation_deg=safe(max_wrist),max_elbow_flex_deg=safe(max_elbow),length_variation={k:[safe(v) for v in values] for k,values in lengths.items()},policy=dict(wrist_limit_deg=wrist_limit,elbow_limit_deg=elbow_limit,scope='Provisional project rejection thresholds, not universal medical/anatomical limits. CMU26_09 observed wrist-axis deviation19.50..42.48deg; a 60deg budget includes margin. Collinear hands can pass and still be badly drawn.'),painted_anatomy_status='UNKNOWN: requires current image-side shoulder/elbow/cuff/hand evidence and visual review',production_pass=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-source',action='store_true');p.add_argument('--require-production',action='store_true');a=p.parse_args();q=audit(json.loads(a.source.read_text()));q['source_sha256']=hashlib.sha256(a.source.read_bytes()).hexdigest();a.out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k] for k in ['checks','max_wrist_deviation_deg','max_elbow_flex_deg','source_arm_metrics_pass','production_pass']}));return int((a.require_source and not q['source_arm_metrics_pass']) or a.require_production)
if __name__=='__main__':raise SystemExit(main())
