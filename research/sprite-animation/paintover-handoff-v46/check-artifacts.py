#!/usr/bin/env python3
"""Check actual decoded delivery files against raw cells and frozen guide pixels, without writing art."""
from pathlib import Path
import json, zipfile
import numpy as np
from PIL import Image, ImageSequence
P=Path(__file__).resolve().parent
VIEWS=['S','SE','E','NE','N','NW','W','SW']
checks={}; failures=[]
for v in VIEWS:
    raw=Image.open(P/'raw'/f'{v}-attempt1.png').convert('RGBA')
    checks[v+'_raw_layout']=raw.size==(1536,1024)
    for kind,folder in [('pose','key'),('owners','ownership')]:
        guide=Image.open(P/'inputs'/f'{v}-{kind}.png').convert('RGBA')
        for k in range(8):
            x=k%4*384;y=k//4*512;box=(x,y,x+384,y+512)
            src=Image.open(P.parent/'left-arm-repair-v45'/'review'/folder/v/f'{k:02}.png').convert('RGBA')
            # Original atlas assembly alpha-composited each guide on transparent cells.
            # This clears hidden RGB where alpha=0, without moving or changing visible pixels.
            expected=Image.new('RGBA',src.size); expected.alpha_composite(src)
            checks[f'{v}_{kind}_{k}_source_composite_exact']=np.array_equal(np.array(guide.crop(box)),np.array(expected))
    for k in range(8):
        x=k%4*384;y=k//4*512
        frame=Image.open(P/'frames'/v/f'{k:02}.png').convert('RGBA')
        checks[f'{v}_paint_{k}_exact']=np.array_equal(np.array(raw.crop((x,y,x+384,y+512))),np.array(frame))
    for name in [v,v+'-source-vs-painted']:
        gif=Image.open(P/'previews'/f'{name}.gif')
        durations=[f.info.get('duration') for f in ImageSequence.Iterator(gif)]
        checks[name+'_eight_exposures']=len(durations)==8
        checks[name+'_exact_clock']=durations==[190,180,190,180,190,180,190,600]
    with zipfile.ZipFile(P/'editor'/f'{v}.ora') as z:
        checks[v+'_ora_integrity']=z.testzip() is None and z.read('mimetype')==b'image/openraster'
        import io
        checks[v+'_ora_full_art_exact']=np.array_equal(np.array(Image.open(io.BytesIO(z.read('data/layer0.png'))).convert('RGBA')),np.array(raw))
report={'checks':checks,'pass':all(checks.values()),'check_count':len(checks),'failures':[k for k,v in checks.items() if not v],'production_pass':False,'scope':'Actual decoded frame/guide/clock/editor integrity; not visible anatomy or smoothness acceptance'}
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['pass'] else 1)
