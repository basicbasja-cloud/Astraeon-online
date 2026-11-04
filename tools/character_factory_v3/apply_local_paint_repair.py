"""Apply an explicitly masked paint repair while preserving all outside pixels.

This is local texture repair, not animation generation or anatomical validation.
Never promote the output solely because the outside-mask comparison passes.
"""
import argparse,hashlib,json,io
from pathlib import Path
import numpy as np
from PIL import Image

def apply_repair(original,repaint,mask):
    original=original.convert('RGBA');repaint=repaint.convert('RGBA');mask=mask.convert('L')
    if original.size!=mask.size:raise ValueError('Mask must use the original canvas')
    if repaint.size!=original.size:
        if abs(repaint.width/repaint.height-original.width/original.height)>1e-6:raise ValueError('Repaint aspect ratio differs from original')
        repaint=repaint.convert('RGBa').resize(original.size,Image.Resampling.LANCZOS).convert('RGBA')
    weights=np.array(mask);before=np.array(original);after=np.array(Image.composite(repaint,original,mask))
    outside=weights==0
    if np.any(after[outside]!=before[outside]):raise ValueError('Protected pixels changed')
    if not np.any(weights):raise ValueError('Empty repair mask')
    return Image.fromarray(after),{'masked_pixels':int((weights>0).sum()),'changed_pixels':int(np.any(after!=before,axis=2).sum()),'protected_pixel_changes':0,'mask_bbox':mask.getbbox(),'global_body_warp':False,'semantic_quality_approved':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--repaint',type=Path,required=True);p.add_argument('--mask',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    receipt_path=a.output.with_suffix('.receipt.json')
    inputs=[('original',a.original),('repaint',a.repaint),('mask',a.mask)]
    if any(a.output.resolve()==path.resolve() or receipt_path.resolve()==path.resolve() for _,path in inputs):raise ValueError('Repair output cannot replace an input')
    if any(path.exists() or path.is_symlink() for path in (a.output,receipt_path)):raise ValueError('Choose a fresh repair output and receipt')
    snapshots={name:path.read_bytes() for name,path in inputs}
    pins={name:{'path':str(path),'sha256':hashlib.sha256(snapshots[name]).hexdigest()}for name,path in inputs}
    out,report=apply_repair(*(Image.open(io.BytesIO(snapshots[name]))for name,_ in inputs))
    if any(hashlib.sha256(path.read_bytes()).hexdigest()!=pins[name]['sha256']for name,path in inputs):raise ValueError('Repair input changed during processing')
    report.update({'status':'LOCAL_REPAIR_CANDIDATE_REQUIRES_BOUNDARY_REVIEW','inputs':pins,'owner_approved':False,'runtime_admitted':False})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation also catches a file appearing after the fresh-path
    # preflight. Never use this command to overwrite an earlier master study.
    with a.output.open('xb') as stream:out.save(stream,format='PNG')
    with receipt_path.open('x') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
