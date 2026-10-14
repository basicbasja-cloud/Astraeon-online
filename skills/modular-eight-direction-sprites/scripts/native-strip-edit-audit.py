#!/usr/bin/env python3
"""Bound requested-cell edit scope. Invisible RGB never counts as visible change."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def audit(before,after,allowed_cells):
    a=np.array(Image.open(before).convert('RGBA'));b=np.array(Image.open(after).convert('RGBA'))
    if a.shape!=b.shape or a.shape!=(1024,1536,4):
        raise ValueError('Expected matching 4x2 384x512 native strips')
    def premultiplied(x):
        rgb=(x[:,:,:3].astype(np.uint16)*x[:,:,3:4].astype(np.uint16)+127)//255
        return np.concatenate([rgb,x[:,:,3:4]],axis=2)
    delta=np.any(premultiplied(a)!=premultiplied(b),axis=2)
    rows=[]
    for i in range(8):
        x,y=i%4*384,i//4*512;mask=delta[y:y+512,x:x+384]
        opaque=(a[y:y+512,x:x+384,3]>=240)|(b[y:y+512,x:x+384,3]>=240)
        rows.append(dict(art_index=i,requested_edit=i in allowed_cells,
                         changed_visible_pixels=int(mask.sum()),changed_opaque_region_pixels=int((mask&opaque).sum()),
                         exact_visible_preservation=not bool(mask.any())))
    return dict(before=dict(path=str(before),sha256=hashlib.sha256(before.read_bytes()).hexdigest()),
                after=dict(path=str(after),sha256=hashlib.sha256(after.read_bytes()).hexdigest()),
                rows=rows,unrequested_cells_preserved=all(r['exact_visible_preservation'] for r in rows if not r['requested_edit']),
                scope='Premultiplied RGBA edit-scope integrity, not a similarity/acting/anatomy score',production_pass=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--allowed-cells',type=int,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(a.before,a.after,a.allowed_cells);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(unrequested_cells_preserved=r['unrequested_cells_preserved'])))
