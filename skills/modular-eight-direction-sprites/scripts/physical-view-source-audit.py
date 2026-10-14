"""Reproject external source joints independently; never infer painted anatomy."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

def audit(original, current):
    checks = {}
    checks['same_external_asset'] = original['source_sha256'] == current['source_sha256']
    checks['same_clip'] = original['clip'] == current['clip']
    checks['same_named_skeleton'] = original['named_bones'] == current['named_bones']
    checks['eight_samples'] = len(original['frames']) == len(current['frames']) == 8
    checks['same_clock'] = [f['source_time_seconds'] for f in original['frames']] == [f['source_time_seconds'] for f in current['frames']]
    a = np.array(original['camera_world_matrix']); b = np.array(current['camera_world_matrix'])
    checks['different_physical_camera'] = not np.allclose(a, b)
    checks['valid_camera'] = bool(b.shape == (4, 4) and np.isclose(np.linalg.det(b[:3, :3]), 1))
    inv = np.linalg.inv(b); w, h = current['canvas']; factor = h/current['ortho_scale']
    errors=[]; world_errors=[]; depths=[]
    for before, after in zip(original['frames'], current['frames']):
        for name, p in after['points'].items():
            old = before['points'][name]
            world_errors.append(float(np.linalg.norm(np.array(old['world_xyz'])-p['world_xyz'])))
            local = inv @ np.array([*p['world_xyz'], 1])
            xy = np.array([w/2+factor*local[0], h/2-factor*local[1]])
            errors.append(float(np.linalg.norm(xy-p['xy'])))
            depths.append(dict(frame=after['index'], joint=name, depth=float(-local[2]), projected_xy=xy.tolist()))
    checks['world_motion_unchanged'] = max(world_errors) < 1e-6
    checks['same_landmark_bone_bindings'] = all(before['points'][name]['source_bone']==p['source_bone'] for before,after in zip(original['frames'],current['frames']) for name,p in after['points'].items())
    checks['independent_projection_matches'] = max(errors) < .001
    return dict(checks=checks, source_view_pass=all(checks.values()), max_world_error=max(world_errors),
                max_projection_error_px=max(errors), projected_joint_depths=depths,
                scope='External source bones/camera only. Depth is not visibility; no painted limb/neck/acting approval.',
                painted_anatomy_certified=False, production_pass=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--current',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    r=audit(json.loads(a.original.read_text()),json.loads(a.current.read_text()))
    current=json.loads(a.current.read_text());asset=Path(current['source_file'])
    r['checks']['actual_asset_hash']=asset.is_file() and hashlib.sha256(asset.read_bytes()).hexdigest()==current['source_sha256']
    r['checks']['actual_captured_png_hashes']=all(Path(f['path']).is_file() and hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256'] for f in current['frames'])
    r['source_view_pass']=all(r['checks'].values())
    r['inputs']=[dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in [a.original,a.current]]
    a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='projected_joint_depths'}));return 0 if r['source_view_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
