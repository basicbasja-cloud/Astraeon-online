#!/usr/bin/env python3
"""Recovery-key and timing diagnostics; never automatic anatomy/acting approval."""
import argparse
import json
import hashlib
from pathlib import Path
import numpy as np


def audit_sequence(rows, source, support, tolerance_px=2, lateral_monotonic_expected=False):
    times=np.array([f['source_time_seconds'] for f in source['frames']])
    sy=np.array([f['points']['head']['xy'][1] for f in source['frames']])
    xy=np.array([r['observed_receiver_surface_xy'] for r in rows])
    peak=int(np.argmax(sy))
    active_range=xy[peak,1]-xy[0,1]
    if active_range<=tolerance_px or np.any(np.diff(times)<=0):
        raise ValueError('No measurable body action or invalid source time')
    expected=(sy-sy[0])/(sy[peak]-sy[0])
    observed=(xy[:,1]-xy[0,1])/active_range
    dt=np.diff(times)
    velocity=np.diff(observed)/dt
    source_velocity=np.diff(expected)/dt
    # Hash independence plus a visible surface strictly between adjacent poses.
    # This catches the disclosed early-rest replacement, not all near-duplicates.
    k=len(rows)-2
    key_distinct=rows[k]['body']['sha256'] not in [rows[k-1]['body']['sha256'],rows[k+1]['body']['sha256']]
    surface_between=bool(xy[k+1,1]+tolerance_px<xy[k,1]<xy[k-1,1]-tolerance_px)
    monotonic=bool(all(xy[i+1,1]-xy[i,1]<=tolerance_px for i in range(peak,len(rows)-1)))
    direction=float(np.sign(xy[-1,0]-xy[peak,0]))
    lateral_steps=direction*np.diff(xy[peak:,0])
    backtrack=float(max(0,-min(lateral_steps)))
    lateral_pass=bool(backtrack<=tolerance_px) if lateral_monotonic_expected else None
    return dict(peak_index=peak,source_times_seconds=times.tolist(),source_normalized_phase=expected.tolist(),
                observed_normalized_phase=observed.tolist(),observed_receiver_surface_xy=xy.tolist(),
                source_velocity_phase_per_second=source_velocity.tolist(),
                observed_velocity_phase_per_second=velocity.tolist(),
                velocity_discrepancy_diagnostic=(velocity-source_velocity).tolist(),
                velocity_discrepancy_is_approval_gate=False,
                penultimate_body_drawing_distinct=key_distinct,
                penultimate_surface_strictly_between=surface_between,
                recovery_monotonic_with_tolerance=monotonic,
                lateral_recovery_monotonic_expected=lateral_monotonic_expected,
                lateral_recovery_steps_px=lateral_steps.tolist(),
                maximum_lateral_backtrack_px=backtrack,lateral_recovery_pass=lateral_pass,
                contact_pass=all(s['pass_'] for s in support.values()),
                recovery_key_pass=bool(key_distinct and surface_between and monotonic and lateral_pass is not False),
                observation_scope='Manually reviewed visible collar surface on bound body drawings; not detected hidden bones',
                production_pass=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--motion-report',type=Path,required=True)
    p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--require-motion',action='store_true')
    a=p.parse_args()
    d=json.loads(a.contract.read_text());s=json.loads((a.root/d['source']['path']).read_text())
    report=json.loads(a.motion_report.read_text())
    bindings=[d['source'],d['head']]+[r['body'] for rows in d['variants'].values() for r in rows]
    for b in bindings:
        if hashlib.sha256((a.root/b['path']).read_bytes()).hexdigest()!=b['sha256']:
            raise ValueError('Stale source/body/head binding')
    if not all(report['integrity_checks'].values()):
        raise ValueError('Parent motion integrity did not pass')
    out={v:audit_sequence(rows,s,report['variants'][v]['support'],d['recovery_overshoot_budget_px'],d.get('lateral_recovery_monotonic_expected',False)) for v,rows in d['variants'].items()}
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({v:dict(recovery_key_pass=r['recovery_key_pass'],production_pass=False) for v,r in out.items()}))
    if a.require_motion and not (report['variants']['review']['motion_metrics_pass'] and out['review']['recovery_key_pass']):
        raise SystemExit(1)
