#!/usr/bin/env python3
"""Verify a single existing-key repair without promoting its art or anatomy."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):return np.array(Image.open(p).convert('RGBA'))

def audit(before,after,before_renders,after_renders,normalization,root,target=6):
    fields=['source','head','head_scale','clocks','body_uniform_rest_matrix','draw_order','logical_slots',
            'planted_surface_budget_px','receiver_endpoint_budget_px','recovery_overshoot_budget_px',
            'phase_warning_fraction','minimum_distinct_body_drawings','lateral_recovery_monotonic_expected']
    shared={f:before[f]==after[f] for f in fields}
    old=before['variants']['review'];new=after['variants']['review'];rows=[]
    for i,(a,b) in enumerate(zip(old,new)):
        if i==target:continue
        actual={mode:bool(np.array_equal(pixels(before_renders/mode/f'{i:02}.png'),pixels(after_renders/mode/f'{i:02}.png'))) for mode in ['full','body','head','collar']}
        rows.append(dict(index=i,record_identical=a==b,actual_pass_pixels_identical=actual))
    bindings=[r['body'] for r in old+new]+[after['head'],after['source']]
    hashes=all(sha(root/b['path'])==b['sha256'] for b in bindings)
    raw=root/normalization['source']['path'];native=Image.open(raw).convert('RGBA');w,h=native.size
    expected=[w/512,0,w/8,0,h/512,0]
    normalized=native.transform((384,512),Image.Transform.AFFINE,expected,Image.Resampling.BICUBIC)
    normalization_pass=bool(w==h and normalization['known_source_plate']==[1024,1024] and
        normalization['inverse_sampling_affine']==expected and not normalization['foreground_or_foot_fit_used'] and
        sha(raw)==normalization['source']['sha256'] and
        np.array_equal(np.array(normalized),pixels(root/new[target]['body']['path'])) and
        sha(root/normalization['output']['path'])==normalization['output']['sha256'])
    a=pixels(before_renders/'body'/f'{target:02}.png');b=pixels(after_renders/'body'/f'{target:02}.png')
    opaque=(a[:,:,3]>=240)|(b[:,:,3]>=240)
    changed=int((np.any(a!=b,axis=2)&opaque).sum())
    unchanged=all(r['record_identical'] and all(r['actual_pass_pixels_identical'].values()) for r in rows)
    return dict(shared_contract_fields_identical=shared,protected_keys=rows,input_hashes_match=hashes,
        known_canvas_normalization_pass=normalization_pass,other_seven_unchanged=unchanged,
        target_body_opaque_changed_pixels=changed,
        isolation_pass=bool(len(old)==len(new)==8 and all(shared.values()) and unchanged and hashes and normalization_pass and changed>0),
        scope='Exact unchanged-key/pixel/clock/scale and known-canvas provenance proof; changed pixels do not certify a correct pose or anatomy',production_pass=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['before-contract','after-contract','before-renders','after-renders','normalization','out']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args()
    r=audit(json.loads(a.before_contract.read_text()),json.loads(a.after_contract.read_text()),a.before_renders,a.after_renders,json.loads(a.normalization.read_text()),a.root)
    a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(isolation_pass=r['isolation_pass'],other_seven_unchanged=r['other_seven_unchanged'])))
    if not r['isolation_pass']:raise SystemExit(1)
