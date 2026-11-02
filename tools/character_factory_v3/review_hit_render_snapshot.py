"""Review declared/native Hit render consistency; never certifies animation or art."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import patch001_factory as factory


def review(observed, guarded, output):
    if output.exists():raise ValueError('Choose fresh review directory')
    a=factory.read(observed/'manifest.json');b=factory.read(guarded/'manifest.json');job=b['job']
    if not factory.receipt_valid(job,guarded):raise ValueError('Invalid guarded source capture')
    if factory.receipt_valid(job,observed):raise ValueError('Observation must not pass guarded receipt')
    fields=('action','source_frame','segment_phase','source_root_world','actor_root_delta','landmarks','world_landmarks','weapon_guide')
    for direction in job['directions']:
        av=a['views'][direction];bv=b['views'][direction]
        assert av['camera']==bv['camera']
        for af,bf in zip(av['frames'],bv['frames']):
            assert all(af.get(k)==bf.get(k)for k in fields)
    assert a['render_snapshot']['source_fcurves_sha256_before_and_after']==b['render_snapshot']['source_fcurves_sha256_before_and_after']
    output.mkdir(parents=True)
    for name,m in [('observed',a),('guarded',b)]:
        (output/f'{name}-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    (output/'job.json').write_text(json.dumps(job,indent=2)+'\n')
    def panel(direction,index):
        board=Image.new('RGB',(512,284),'#eeeeee');draw=ImageDraw.Draw(board)
        for x,folder,label in [(0,observed,'before'),(256,guarded,'snapshot')]:
            with Image.open(folder/direction/f'{index:03d}.png')as image:
                rgba=image.convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
                board.paste(rgba,(x,28),rgba)
            draw.text((x+8,8),f'{direction} {index:03d} {label}',fill='black')
        return board
    for label,folder in [('before',observed),('snapshot',guarded)]:
        (output/f'SW005-{label}-native.png').write_bytes((folder/'SW/005.png').read_bytes())
    panel('SW',5).save(output/'SW005-before-after.png')
    frames=[]
    for index in range(job['frames']):
        board=Image.new('RGB',(1024,1136),'white')
        for n,direction in enumerate(job['directions']):board.paste(panel(direction,index),((n%2)*512,(n//2)*284))
        frames.append(board)
    frames[5].save(output/'eight-views-frame005.png')
    for name,duration in [('normal',100),('slow',300)]:
        frames[0].save(output/f'eight-views-{name}-one-shot.gif',save_all=True,append_images=frames[1:],duration=duration,disposal=2)
    def metrics(m):
        rows=m['render_snapshot']['frames']
        return {'poses':len(rows),'bones_per_pose':sorted({r['bones']for r in rows}),
                'max_world_matrix_error':max(r['max_after_render_matrix_component_error']for r in rows),
                'max_joint_render_displacement_runtime_px':max(j['distance_runtime_px']for r in rows for j in r['joints'].values())}
    baseline=factory.read(factory.ROOT/'docs/character-factory/review/restore-tall-swordsman-baseline-20261026/baseline-proof.json')['baseline_files']
    assert all(factory.filehash(factory.ROOT/p)==h for p,h in baseline.items())
    proof={'status':'SOURCE_RENDER_CONSISTENCY_ONLY_NOT_ART_APPROVAL','before':metrics(a),'after':metrics(b),
           'same_camera_declared_landmarks_weapon_and_samples':True,'source_fcurve_fingerprint_unchanged':True,
           'protected_baseline_hashes_matched':len(baseline),'sole_contact_or_motion_quality_approved':False,
           'all_twelve_samples_including_reset_tail_shown':True,'gif_loop_extension':False,
           'preview_duration_ms':{'normal':100,'slow':300},'preview_timing_is_diagnostic':True,
           'files_sha256':{str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(output.iterdir())}}
    (output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ('observed','guarded','output'):parser.add_argument('--'+flag,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(review(args.observed,args.guarded,args.output)))
