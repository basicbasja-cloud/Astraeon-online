#!/usr/bin/env python3
"""Reviewed-empty-region alpha checks. Never infer anatomy or erase source pixels."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image


def audit_sheet(path):
    a=np.array(Image.open(path).convert('RGBA'))
    if a.shape!=(1024,1536,4):
        raise ValueError('This adapter requires the declared 4x2 384x512 layout')
    points=[[20,20],[364,20],[20,470],[364,470]]
    rows=[]
    for i in range(8):
        for x,y in points:
            xx=i%4*384+x;yy=i//4*512+y
            alpha=a[yy-2:yy+3,xx-2:xx+3,3]
            rows.append(dict(art_index=i,center_native=[x,y],patch_size=[5,5],maximum_alpha=int(alpha.max()),pass_=bool(alpha.max()==0)))
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                scope='Manually reviewed empty cell-corner patches for this unclipped crouch family; not automatic matting. RGB at alpha0 is ignored.',
                observations=rows,empty_patch_pass=all(r['pass_'] for r in rows),source_pixels_modified=False,production_pass=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sheets',type=Path,nargs='+',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();report=[audit_sheet(path) for path in a.sheets]
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({r['path']:r['empty_patch_pass'] for r in report}))
