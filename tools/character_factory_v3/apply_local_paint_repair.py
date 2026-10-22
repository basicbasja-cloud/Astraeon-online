"""Apply an explicitly masked paint repair while preserving all outside pixels.

This is local texture repair, not animation generation or anatomical validation.
Never promote the output solely because the outside-mask comparison passes.
"""
import argparse,hashlib,json
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
    out,report=apply_repair(Image.open(a.original),Image.open(a.repaint),Image.open(a.mask));a.output.parent.mkdir(parents=True,exist_ok=True);out.save(a.output)
    report.update({'status':'LOCAL_REPAIR_CANDIDATE_REQUIRES_BOUNDARY_REVIEW','inputs':{name:{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}for name,path in [('original',a.original),('repaint',a.repaint),('mask',a.mask)]},'owner_approved':False,'runtime_admitted':False})
    a.output.with_suffix('.receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
