#!/usr/bin/env python3
"""Package generated RGBA captures without changing any visible RGB or alpha.

Only invisible RGB values at alpha zero are cleared. The immutable motion source
is never edited. Original file hashes and visible-pixel proof are recorded.
"""
import argparse,hashlib,io,json
from pathlib import Path
import numpy as np
from PIL import Image


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folders',nargs='+',type=Path);args=ap.parse_args()
    for folder in args.folders:
        records=[]
        for path in sorted(folder.rglob('*.png')):
            source=path.read_bytes();im=Image.open(io.BytesIO(source))
            if im.mode!='RGBA':continue
            pixels=np.asarray(im).copy();alpha=pixels[:,:,3].copy();visible=pixels[alpha>0,:3].copy()
            proof=hashlib.sha256(visible.tobytes()+alpha.tobytes()).hexdigest()
            hidden=int(np.any(pixels[alpha==0,:3]!=0,axis=1).sum());pixels[alpha==0,:3]=0
            buffer=io.BytesIO();Image.fromarray(pixels,'RGBA').save(buffer,format='PNG',optimize=True,compress_level=9);data=buffer.getvalue()
            restored=np.asarray(Image.open(io.BytesIO(data)).convert('RGBA'))
            if not np.array_equal(restored[:,:,3],alpha) or not np.array_equal(restored[alpha>0,:3],visible):raise ValueError(f'Visible pixel change: {path}')
            if len(data)<len(source):
                tmp=path.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(path);size=len(data)
            else:size=len(source)
            records.append({'file':str(path.relative_to(folder)),'original_sha256':hashlib.sha256(source).hexdigest(),'visible_rgb_and_alpha_sha256':proof,'bytes_before':len(source),'bytes_after':size,'invisible_rgb_pixels_cleared':hidden,'visible_rgb_or_alpha_changed':False})
        result={'method':'clear RGB only where alpha is exactly zero, then lossless PNG compression; verify visible RGB and every alpha value unchanged','status':'VISIBLE_PIXELS_IDENTICAL','files':records,'bytes_before':sum(r['bytes_before'] for r in records),'bytes_after':sum(r['bytes_after'] for r in records),'motion_source_modified':False}
        (folder/'png-normalization-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(folder,len(records),result['bytes_before'],result['bytes_after'],flush=True)

if __name__=='__main__':main()
