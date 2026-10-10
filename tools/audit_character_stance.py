"""Measure painted sole drift inside artist-selected boot regions, without edits.

Regions must isolate a boot from blades and other art. Alpha-based bottom-edge
measurements are diagnostics, not inferred anatomical joints or visual approval.
"""
import argparse
import json
import math
from pathlib import Path
from PIL import Image


def measure(image, cell, regions, scale=1, tolerance=2):
    sw,sh=cell
    if image.mode!='RGBA' or image.width%sw or image.height%sh:
        raise ValueError('Expected RGBA image on a complete cell grid')
    if not regions or scale<=0 or tolerance<0:
        raise ValueError('Invalid stance configuration')
    records=[]
    for row in range(image.height//sh):
        for col in range(image.width//sw):
            frame=image.crop((col*sw,row*sh,(col+1)*sw,(row+1)*sh))
            soles={}
            for name,rect in regions.items():
                x0,y0,x1,y1=rect
                if not 0<=x0<x1<=sw or not 0<=y0<y1<=sh:
                    raise ValueError('Boot region exceeds source cell')
                alpha=frame.crop(rect).getchannel('A').point(lambda a:255 if a>=128 else 0)
                bounds=alpha.getbbox()
                if bounds is None:raise ValueError('Empty boot region: '+name)
                if bounds[0]==0 or bounds[2]==alpha.width or bounds[3]==alpha.height:
                    raise ValueError('Boot touches measurement region boundary: '+name)
                bottom=bounds[3]-1
                xs=[x for y in range(max(0,bottom-2),bottom+1) for x in range(alpha.width) if alpha.getpixel((x,y))]
                soles[name]=[x0+sum(xs)/len(xs),y0+bottom]
            records.append(dict(pose=len(records),soles=soles))
    findings=[]
    for record in records:
        record['driftPixels']={}
        for name,p in record['soles'].items():
            base=records[0]['soles'][name]
            drift=math.dist(p,base)*scale;record['driftPixels'][name]=round(drift,3)
            if drift>tolerance:findings.append(dict(pose=record['pose'],foot=name,driftPixels=round(drift,3)))
    return dict(status='DIAGNOSTIC_ONLY',visualApproval=False,tolerancePixels=tolerance,
        method='Bottom three opaque-alpha rows within manually isolated boot regions',
        limitation='Region contents and intended planted-foot interval require visual inspection; not a pose correction',
        frames=records,findings=findings)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();plan=json.loads(args.plan.read_text())
    results={}
    for label,source in plan['sources'].items():
        with Image.open(source) as image:
            results[label]=measure(image,plan['cell'],plan['regions'],plan['scale'],plan['tolerancePixels'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n')
    print({label:len(result['findings']) for label,result in results.items()})
