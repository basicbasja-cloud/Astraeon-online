#!/usr/bin/env python3
"""Rebuild v46 review assets from retained native strips. No provider calls or per-frame fitting."""
from pathlib import Path
import base64, hashlib, io, json, zipfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parent
VIEWS = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW']
DURATIONS = [190, 180, 190, 180, 190, 180, 190, 600]
SIZE = (384, 512)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def png(im):
    b = io.BytesIO(); im.save(b, format='PNG'); return b.getvalue()
def bg(im):
    out = Image.new('RGBA', im.size, '#292b30'); out.alpha_composite(im); return out.convert('RGB')
def observe(im):
    a = np.array(im.getchannel('A')) >= 128
    lab, n = ndimage.label(a)
    if not n: return {'status': 'EMPTY'}
    counts = np.bincount(lab.ravel()); counts[0] = 0
    k = int(counts.argmax()); y, x = np.where(lab == k)
    return dict(status='OBSERVED_COMPONENT_NOT_ANATOMY', bbox=[int(x.min()), int(y.min()), int(x.max()), int(y.max())], width=int(x.max()-x.min()+1), height=int(y.max()-y.min()+1), bottom_proxy=int(y.max()), alpha128_pixels=int(a.sum()), boundary_pixels=int(a[0].sum()+a[-1].sum()+a[:,0].sum()+a[:,-1].sum()))
def ora(view, art):
    root = ET.Element('image', w='1536', h='1024', name=view+' painted review; NOT separated runtime parts', version='0.0.1')
    stack = ET.SubElement(root, 'stack')
    layers = [('painted_full_REVIEW', art, True), ('ownership_SOURCE_ONLY', Image.open(P/'inputs'/f'{view}-owners.png'), False), ('pose_SOURCE_ONLY', Image.open(P/'inputs'/f'{view}-pose.png'), False)]
    with zipfile.ZipFile(P/'editor'/f'{view}.ora', 'w') as z:
        z.writestr('mimetype','image/openraster', compress_type=zipfile.ZIP_STORED)
        for i, (name, im, visible) in enumerate(layers):
            src = f'data/layer{i}.png'; z.writestr(src, png(im))
            ET.SubElement(stack, 'layer', name=name, src=src, opacity='1.0', visibility='visible' if visible else 'hidden', x='0', y='0', **{'composite-op':'svg:src-over'})
        z.writestr('stack.xml', ET.tostring(root, encoding='utf-8'))
        z.writestr('mergedimage.png', png(art)); z.writestr('Thumbnails/thumbnail.png', png(art.resize((256,171))))

def main():
    for d in ['frames','previews','editor']: (P/d).mkdir(exist_ok=True)
    report = {'production_pass':False, 'status':'PAINTED_REVIEW_CANDIDATE', 'clock_ms':DURATIONS, 'total_ms':sum(DURATIONS), 'transform':'Exact atlas cells only; no scale, fit, translation, warp or opacity cleanup', 'observer':'Largest alpha>=128 connected component; bottom is NOT sole tracking. Hidden joints UNKNOWN.', 'views':{}}
    bank = {}; comparison = {}
    for view in VIEWS:
        raw = P/'raw'/f'{view}-attempt1.png'
        im = Image.open(raw).convert('RGBA')
        if im.size != (1536,1024): raise ValueError(f'{view}: exact plate mismatch {im.size}; do not silently fit')
        (P/'frames'/view).mkdir(exist_ok=True)
        seq=[]; measures=[]; pairs=[]
        source = Image.open(P/'inputs'/f'{view}-pose.png').convert('RGBA')
        for k in range(8):
            x=(k%4)*384; y=(k//4)*512; box=(x,y,x+384,y+512)
            frame=im.crop(box); frame.save(P/'frames'/view/f'{k:02}.png')
            seq.append(bg(frame)); measures.append(observe(frame))
            pair=Image.new('RGB',(768,512),'#292b30'); pair.paste(bg(source.crop(box)),(0,0));pair.paste(bg(frame),(384,0));pairs.append(pair)
        bank[view]=seq; comparison[view]=pairs
        seq[0].save(P/'previews'/f'{view}.gif',save_all=True,append_images=seq[1:],duration=DURATIONS,loop=0,disposal=2)
        pairs[0].save(P/'previews'/f'{view}-source-vs-painted.gif',save_all=True,append_images=pairs[1:],duration=DURATIONS,loop=0,disposal=2)
        obs={'raw_sha256':digest(raw),'frames':measures,'alpha_min':int(np.array(im.getchannel('A')).min()),'alpha_max':int(np.array(im.getchannel('A')).max()),'transparent_fraction':float((np.array(im.getchannel('A'))==0).mean())}
        obs['neutral_return_height_delta']=measures[7]['height']-measures[0]['height']
        obs['bottom_proxy_range']=max(m['bottom_proxy'] for m in measures)-min(m['bottom_proxy'] for m in measures)
        obs['approval']='NOT_APPROVED; geometry/costume/ownership/manual review required'
        report['views'][view]=obs; ora(view,im)
    mosaics=[]
    for k in range(8):
        plate=Image.new('RGB',(1536,1060),'#292b30');draw=ImageDraw.Draw(plate)
        for j,v in enumerate(VIEWS):
            x=j%4*384;y=j//4*530;plate.paste(bank[v][k],(x,y+18));draw.text((x+8,y+3),f'{v}  frame {k+1}/8',fill='white')
        mosaics.append(plate)
    mosaics[0].save(P/'previews'/'eight-directions.gif',save_all=True,append_images=mosaics[1:],duration=DURATIONS,loop=0,disposal=2)
    overview=Image.new('RGB',(1536,8*268),'#292b30');draw=ImageDraw.Draw(overview)
    for j,v in enumerate(VIEWS):
        for k,frame in enumerate(bank[v]):overview.paste(frame.resize((192,256),Image.Resampling.LANCZOS),(k*192,j*268+12))
        draw.text((3,j*268),v+'  1..8 left to right',fill='white')
    overview.save(P/'previews'/'all-frames.png')
    (P/'paint-review.json').write_text(json.dumps(report,indent=2)+'\n')
    # Portable offline viewer embeds exact retained frame PNGs. Source overlay is never a painted tracker.
    payload={v:[base64.b64encode((P/'frames'/v/f'{k:02}.png').read_bytes()).decode() for k in range(8)] for v in VIEWS}
    guides={v:base64.b64encode((P/'inputs'/f'{v}-pose.png').read_bytes()).decode() for v in VIEWS}
    html='''<!doctype html><meta charset="utf-8"><title>v46 painted review — unapproved</title><style>body{background:#202228;color:white;font:16px sans-serif}canvas{background:#292b30;max-width:100%;height:auto}button,select,input{margin:8px}p{max-width:1000px}</style><h1>v46 painted pickup review</h1><p>8 drawings per facing, 1900 ms source review clock. No per-frame fitting. Source is a guide, not painted joint tracking. Art, contacts, anatomy and modular swaps are NOT approved.</p><select id="view"></select><button id="play">Pause</button><input id="key" type="range" min="0" max="7" value="0"><label><input id="grid" type="checkbox" checked>32px grid</label><span id="label"></span><p>Left: corrected source. Right: actual painted pixels.</p><canvas width="768" height="512" id="c"></canvas><script>const frames=PAYLOAD,guides=GUIDES,ms=CLOCK;const views=Object.keys(frames),sel=document.querySelector('#view'),slider=document.querySelector('#key'),ctx=document.querySelector('#c').getContext('2d');let playing=true,base=performance.now(),current=0;let images={},source={};for(const v of views){sel.add(new Option(v,v));images[v]=frames[v].map(s=>{let i=new Image();i.src='data:image/png;base64,'+s;return i});source[v]=new Image();source[v].src='data:image/png;base64,'+guides[v]}document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'Pause':'Play';base=performance.now()-ms.slice(0,current).reduce((a,b)=>a+b,0)};slider.oninput=()=>{playing=false;current=+slider.value;document.querySelector('#play').textContent='Play'};function draw(t){if(playing){let p=(t-base)%ms.reduce((a,b)=>a+b,0);current=0;while(p>=ms[current]&&current<7){p-=ms[current++]}slider.value=current}ctx.clearRect(0,0,768,512);let v=sel.value;ctx.drawImage(source[v],current%4*384,Math.floor(current/4)*512,384,512,0,0,384,512);ctx.drawImage(images[v][current],384,0);if(document.querySelector('#grid').checked){ctx.strokeStyle='#ffffff28';ctx.lineWidth=1;for(let x=0;x<=768;x+=32){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,512);ctx.stroke()}for(let y=0;y<=512;y+=32){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(768,y);ctx.stroke()}}document.querySelector('#label').textContent=`Frame ${current+1}/8 — ${ms[current]} ms`;requestAnimationFrame(draw)}Promise.all(Object.values(source).concat(...Object.values(images)).map(i=>i.decode())).then(()=>requestAnimationFrame(draw));</script>'''
    html=html.replace('PAYLOAD',json.dumps(payload)).replace('GUIDES',json.dumps(guides)).replace('CLOCK',json.dumps(DURATIONS))
    (P/'review.html').write_text(html)
    print(json.dumps({'views':len(bank),'painted_frames':64,'production_pass':False,'bottom_proxy_ranges':{v:report['views'][v]['bottom_proxy_range'] for v in VIEWS}}))

if __name__=='__main__': main()
