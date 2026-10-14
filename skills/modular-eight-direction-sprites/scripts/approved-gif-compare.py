"""Compare real decoded approved GIF exposures, never an invented mean FPS.

The reference is immutable. Metrics do not confer art or anatomical acceptance.
Actual source-guide fidelity and image-specific human review remain required.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageSequence


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decode(path):
    with Image.open(path) as im:
        frames = [f.convert('RGBA').copy() for f in ImageSequence.Iterator(im)]
        im.seek(0)
        durations = []
        for i in range(im.n_frames):
            im.seek(i)
            durations.append(int(im.info.get('duration', 0)))
    return frames, durations


def trajectory(points, contact_index):
    """Both axes stay in image pixels. Do not fit per-axis scale or peak."""
    a = np.asarray(points, float)
    if len(a) < 3 or a.ndim != 2 or a.shape[1] != 2:
        raise ValueError('Need ordered XY observations, not hidden joints')
    descent = np.diff(a[:contact_index+1, 1])
    ascent = np.diff(a[contact_index:, 1])
    return dict(step_xy=np.diff(a, axis=0).tolist(),
                pre_contact_upward_reversal_px=float(max(0, -descent.min())),
                recovery_downward_reversal_px=float(max(0, ascent.max())),
                terminal_gap_px=float(np.linalg.norm(a[-1]-a[0])))


def run(c, root, out):
    root, out = Path(root), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rf, rd = decode(root/c['reference']['path'])
    cf = [Image.open(root/f['path']).convert('RGBA') for f in c['candidate_frames']]
    cd = c['durations_ms']
    if len(rf) != len(cf) or len(cf) != len(cd):
        raise ValueError('Explicit exposure correspondence required')
    checks = {
        'approved_gif_hash': digest(root/c['reference']['path']) == c['reference']['sha256'],
        'all_candidate_hashes': all(digest(root/f['path']) == f['sha256'] for f in c['candidate_frames']),
        'exact_approved_clock': cd == rd,
        'fixed_candidate_canvas': len({f.size for f in cf}) == 1,
    }
    approval=c.get('approval_receipt')
    if approval:
        receipt=json.loads((root/approval['path']).read_text())
        checks['immutable_user_acceptance_binding']=digest(root/approval['path'])==approval['sha256'] and any(x['path']==c['reference']['path'] and x['sha256']==c['reference']['sha256'] for x in receipt['files'])
    else:
        checks['immutable_user_acceptance_binding']=False
    # Real decoded reference pixels and candidate pixels are displayed together.
    # Thumbnail scale is fixed for EACH BANK, never derived from each frame bbox.
    cell = (384, 512)
    def panel(im):
        bg = Image.new('RGBA', cell, '#344351')
        s = min(cell[0]/im.width, cell[1]/im.height)
        sz = (round(im.width*s), round(im.height*s))
        bg.alpha_composite(im.resize(sz, Image.Resampling.LANCZOS), ((cell[0]-sz[0])//2, (cell[1]-sz[1])//2))
        return bg.convert('RGB')
    pairs = []
    board = Image.new('RGB', (768*4, 540*2), '#1b2630')
    for i, (a,b) in enumerate(zip(rf,cf)):
        p = Image.new('RGB', (768,540), '#1b2630')
        p.paste(panel(a),(0,28)); p.paste(panel(b),(384,28))
        ImageDraw.Draw(p).text((8,7), f'Key {i+1}: APPROVED GIF | NEW VIEW / {rd[i]}ms', fill='white')
        pairs.append(p);board.paste(p,(i%4*768,i//4*540))
    board.save(out/'approved-vs-candidate-sheet.png')
    pairs[0].save(out/'approved-vs-candidate.gif', save_all=True, append_images=pairs[1:], duration=rd, loop=0, disposal=2)
    _, actual = decode(out/'approved-vs-candidate.gif')
    checks['comparison_gif_exact_clock'] = actual == rd
    observations = c.get('observations')
    metrics = {}
    required=c.get('required_support_tracks')
    checks['declared_planted_supports_observed']=bool(required and observations and set(required).issubset(observations.get('planted_surfaces',{})))
    if observations:
        checks['observations_bound_to_actual_pngs'] = observations['frame_sha256'] == [f['sha256'] for f in c['candidate_frames']]
        # Only explicitly visible landmarks can contribute. Null is abstention.
        for name, pts in observations.get('visible_tracks', {}).items():
            if len(pts) != len(cf) or any(x is None for x in pts):
                metrics[name] = dict(status='UNKNOWN', reason='Occluded or missing image observation')
                continue
            metrics[name] = trajectory(pts,c['contact_index'])
        for name, pts in observations.get('planted_surfaces', {}).items():
            if len(pts) != len(cf) or any(x is None for x in pts):
                checks['support_'+name] = False
                metrics['support_'+name] = dict(status='UNKNOWN')
            else:
                a=np.asarray(pts,float); spread=np.ptp(a,axis=0)
                metrics['support_'+name]=dict(range_xy_px=spread.tolist(),scope='Visible screen-labelled surface, not anatomical limb identity or force balance')
                checks['support_'+name]=bool(np.max(spread)<=c['support_budget_px'])
        review=observations.get('manual_action_review',{})
        # Review is recorded against exact pixels; this software cannot recover
        # a hidden shoulder or certify a hand by changing its metadata label.
        checks['current_exact_image_action_review']=review.get('pass') is True and review.get('frame_sha256') == [f['sha256'] for f in c['candidate_frames']]
    else:
        checks['current_exact_image_action_review']=False
    return dict(checks=checks, reference_durations_ms=rd, candidate_durations_ms=cd,
                reference_size=rf[0].size, candidate_size=cf[0].size,
                visible_metrics=metrics, comparison_checks_pass=bool(all(checks.values())),
                production_pass=False, user_new_art_approval=False,
                scope='Actual approved GIF pixels/clock and current bound image observations. Different-view absolute XY is not equated; phase resemblance cannot override failed source geometry, occlusion, anatomy or acting.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--require-checks',action='store_true');a=p.parse_args()
    r=run(json.loads(a.contract.read_text()),a.root,a.out_dir)
    (a.out_dir/'approved-gif-qa.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r['checks']))
    return int(a.require_checks and not r['comparison_checks_pass'])


if __name__=='__main__':raise SystemExit(main())
