"""Correct whole-frame packing translation using explicit observed head proxies.

No scaling, body warping, figure bounding-box fitting or camera adjustment.
A hair centroid is a packing proxy, not an independently verified bone socket.
Prop/feet registration and anatomy still require separate acceptance.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from build_occluded_underlays import sha
from render_segmented_mage_action import remove_distant_faint_alpha


def translate_frame(image,delta):
    if len(delta)!=2 or any(not np.isfinite(v)or int(v)!=v for v in delta):raise ValueError('Finite integer packing translation required')
    out=Image.new('RGBA',image.size);out.paste(image,tuple(int(v)for v in delta))
    if np.array(out.getchannel('A')).sum()!=np.array(image.getchannel('A')).sum():raise ValueError('Packing translation clips source alpha')
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['masters','annotations','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh registered study')
    observed=json.loads(a.annotations.read_text());base=np.array(observed['fixed_reference_offset']);frozen={str(a.annotations):sha(a.annotations)};implementation=sha(__file__)
    a.output.mkdir(parents=True);folder=a.output/'Master';folder.mkdir();records=[];preview=[]
    for row in observed['frames']:
        i=row['index'];path=a.masters/f'{i:03}.png';digest=sha(path)
        if digest!=row['source_sha256']:raise ValueError('Annotated painted source changed')
        frozen[str(path)]=digest
        image,noise=remove_distant_faint_alpha(Image.open(path).convert('RGBA'))
        delta=np.rint(np.array(row['native_head'])+base-row['observed_auburn_core']).astype(int)
        if np.linalg.norm(delta)>80:raise ValueError('Packing proxy is too far from the native pose')
        registered=translate_frame(image,delta);out=folder/f'{i:03}.png';registered.save(out)
        error=float(np.linalg.norm(np.array(row['observed_auburn_core'])+delta-row['native_head']-base))
        records.append({'index':i,'translation':delta.tolist(),'faint_detached_pixels_removed':noise,'proxy_rounding_error_px':error,'sha256':sha(out)})
        bg=Image.new('RGBA',registered.size,'#aaa');bg.alpha_composite(registered);preview.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    preview[0].save(a.output/'registered-walk-study.gif',save_all=True,append_images=preview[1:],duration=80,loop=0)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Packing registration inputs or implementation changed')
    report={'status':'HEAD_PROXY_PACKING_CORRECTION_NOT_POSE_APPROVAL','frames':records,'input_sha256':frozen,'implementation_sha256':implementation,'source_proxy':'observed auburn hair core; not a ground-truth bone socket','pixel_transform':'whole-frame integer translation only','per_frame_scale':False,'body_warp':False,'camera_changed':False,'feet_and_prop_approved':False,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['register_observed_head_sequence.py','render_segmented_mage_action.py','build_occluded_underlays.py','derive_bounded_hold_parts.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(records),'maximum_proxy_rounding_error':max(r['proxy_rounding_error_px']for r in records),'runtime_admitted':False}))


if __name__=='__main__':main()
