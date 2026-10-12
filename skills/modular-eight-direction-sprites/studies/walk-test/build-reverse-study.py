"""Research-only captured pose paintovers; preserve keys and unknown anatomy."""
import base64
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'research/sprite-animation/reverse-paintover-v19'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bound(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': sha(p)}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def frames(folder):
    return sorted((STUDY / folder / 'frames').glob('*.png'))


def animated(folder, images, delay, label):
    folder.mkdir(parents=True, exist_ok=True)
    rgba = [Image.open(p).convert('RGBA') for p in images]
    rgba[0].save(folder / (label + '.png'), save_all=True, append_images=rgba[1:],
                 duration=delay, loop=0, disposal=0, blend=0)
    strip = Image.new('RGB', (512 * len(rgba), 512), '#272727')
    opaque = []
    for i, im in enumerate(rgba):
        bg = Image.new('RGBA', im.size, '#272727'); bg.alpha_composite(im)
        opaque.append(bg.convert('RGB')); strip.paste(opaque[-1], (512*i, 0))
    pal = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    gif = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in opaque]
    gif_delay = [round((i+1)*delay/10)*10 - round(i*delay/10)*10 for i in range(len(rgba))]
    gif[0].save(folder / (label + '.gif'), save_all=True, append_images=gif[1:],
                duration=gif_delay, loop=0, disposal=2, optimize=False)
    clocks = []
    for suffix in ['png', 'gif']:
        with Image.open(folder / (label + '.' + suffix)) as im:
            times=[]
            for i in range(im.n_frames):
                im.seek(i); times.append(im.info.get('duration'))
            if im.n_frames != len(images) or abs(sum(times)-len(images)*delay)>1e-6:
                raise ValueError('Actual decoded exposure clock/count differs')
            clocks.append({'file': label+'.'+suffix, 'actual_frames':im.n_frames,
                          'decoded_duration_ms':times, 'total_ms':sum(times)})
    return clocks


def contract(capture_path, kind, keys, sequence, cycle, mode):
    cap=json.loads(capture_path.read_text())
    observed=[dict(bound(capture_path.parent/f['file']),index=f['index'],
                   time_ms=f['time_ms'],duration_ms=f['duration_ms']) for f in cap['frames']]
    return {'schema':'reference-truth-contract-v1','capture':bound(capture_path),
            'source_kind':kind,'observed_frames':observed,
            'recovered_hidden_skeleton':False,'recovered_world_contact':False,
            'observations':[], 'experiment': {'mode':mode,'canvas':[512,512],
             'keys':[bound(p) for p in keys],'sequence':sequence,'cycle_ms':cycle,
             'clock_scope':'same_captured_cycle','art_status':'UNAPPROVED_RESEARCH'}}


def main():
    import os
    os.chdir(ROOT)
    evidence=STUDY/'evidence'
    keys=frames('ro-keys'); mids=frames('ro-midpoints'); val=frames('valyria-keys')
    if list(map(len,[keys,mids,val])) != [8,8,6]: raise ValueError('Expected 8/8/6 actual draws')
    inter=STUDY/'ro-sixteen'/'frames';inter.mkdir(parents=True,exist_ok=True)
    ordered=[];seq=[]
    for i in range(16):
        p=keys[i//2] if i%2==0 else mids[i//2]
        dest=inter/f'{i:02}.png';shutil.copyfile(p,dest);ordered.append(dest)
        f=dict(bound(dest),time_ms=i*37.5,duration_ms=37.5)
        if i%2==0:f.update(role='authored_key',source_index=i//2)
        else:f.update(role='authored_inbetween',source_pair=[i//2,(i//2+1)%8],recovered_from_game=False)
        seq.append(f)
    key_seq=[dict(bound(p),time_ms=i*75,duration_ms=75,role='authored_key',source_index=i) for i,p in enumerate(keys)]
    val_seq=[dict(bound(p),time_ms=i*130,duration_ms=130,role='authored_key',source_index=i) for i,p in enumerate(val)]
    rocap=ROOT/'research/sprite-animation/motion-reference-v6/ro/walk-W/capture.json'
    valcap=ROOT/'research/sprite-animation/cross-game-factory-v18/captures/valyria-walk-west/capture.json'
    contracts={'ro-keys':contract(rocap,'community_rendered_game',keys,key_seq,600,'key_paintover'),
        'ro-sixteen':contract(rocap,'community_rendered_game',keys,seq,600,'locked_keys_with_midpoints'),
        'valyria-keys':contract(valcap,'native_script_atlas',val,val_seq,780,'key_paintover')}
    loader=importlib.util.spec_from_file_location('truth',ROOT/'skills/modular-eight-direction-sprites/scripts/reference-truth.py')
    truth=importlib.util.module_from_spec(loader);loader.loader.exec_module(truth)
    for name,c in contracts.items():save(evidence/(name+'-truth-contract.json'),c);save(evidence/(name+'-truth-report.json'),truth.audit(c,ROOT))
    formats=animated(STUDY/'ro-sixteen',ordered,37.5,'walk-native-cycle-600ms')
    formats+=animated(STUDY/'ro-sixteen',ordered,50,'walk-uniform-control-800ms')
    formats+=animated(STUDY/'ro-keys',keys,100,'walk-uniform-control-800ms')
    formats+=animated(STUDY/'valyria-keys',val,130,'walk-native-cycle-780ms')
    save(evidence/'decoded-format-clocks.json',formats)
    # Detect actual failure instead of clipping away cross-cell cape pixels.
    a=np.array(Image.open(evidence/'RO-attempt1-raw.png').convert('RGBA'))[:,:,3]
    cuts=[int(a[:,x-1:x+1].max()) for x in [384,768,1152]]
    save(evidence/'attempt1-pack-rejection.json',{'raw':bound(evidence/'RO-attempt1-raw.png'),
         'column_cut_max_alpha':cuts,'threshold':64,'status':'REJECTED_CELL_CUT',
         'foreground_deleted':False,'individual_fitting':False})
    # Calibrated silver-hair occupancy; no hidden joint/owner claims.
    loader=importlib.util.spec_from_file_location('continuity',ROOT/'skills/modular-eight-direction-sprites/scripts/walk-continuity.py')
    continuity=importlib.util.module_from_spec(loader);loader.loader.exec_module(continuity)
    probe={'roi':[80,10,370,240],'max_hsv_saturation_255':110,'min_hsv_value_255':75,
           'min_blue_green_ratio':.88,'min_red_green_ratio':.88,'minimum_pixels':100,
           'max_step_px':20}
    for name,paths,dt in [('ro-keys',keys,75),('ro-sixteen',ordered,37.5),('valyria-keys',val,130)]:
        spec={'schema':'walk-visible-observations-v1','label':name,'canvas':[512,512],
            'loop':True,'registration':'Shared fixed logical canvas, no individual scale/fit',
            'tracked_landmarks':['root'],'palette_patch_probe':probe,
            'scope':'Palette calibrated by visual hair review on these sheets only; 20px provisional warning, not anatomy/naturalness score',
            'frames':[{'image':str(p.relative_to(ROOT)),'sha256':sha(p),'duration_ms':dt,'landmarks':{'root':None},'batch':'midpoints' if name=='ro-sixteen' and i%2 else name} for i,p in enumerate(paths)]}
        save(evidence/(name+'-continuity-input.json'),spec);save(evidence/(name+'-continuity.json'),continuity.audit(spec))
    banks=[('RO converter / observed pixels',rocap.parent,75,8),('RO paintover / UNAPPROVED',STUDY/'ro-keys/frames',75,8),
           ('RO keys + authored midpoints / FAILED CONTINUITY',inter,37.5,16),
           ('Valyria native atlas / script timing',valcap.parent,130,6),
           ('Valyria paintover / UNAPPROVED',STUDY/'valyria-keys/frames',130,6),
           ('King Lucas developer GIF / comparison only',ROOT/'research/sprite-animation/motion-reference-v6/other-games/king-lucas-walk-1',30,13)]
    data=[]
    for label,folder,dt,n in banks:
        files=sorted(folder.glob('[0-9]*.png'))
        if len(files)!=n:raise ValueError('Comparison bank incomplete')
        data.append({'label':label,'duration':dt,'cycle':dt*n,'urls':['data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in files]})
    html='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Reverse paintover v19</title><style>body{background:#181b20;color:#eee;font:16px system-ui;margin:20px}button,select,input{font:inherit;margin:8px}.banks{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px}.bank{padding:12px;background:#272727}.bank img{display:block;height:320px;max-width:100%;margin:auto;object-fit:contain}.bank.native img{image-rendering:pixelated}.bank h3{height:96px;margin:0 0 8px;font-size:18px;line-height:24px}.warning{color:#ffca80}p{max-width:1000px;line-height:1.5}</style><h1>RO pose paintover / locked-key interpolation experiment</h1><p class="warning">Research-only, new art UNAPPROVED. Inserted drawings are authored guesses, not recovered RO frames or skeletons. Exact v17 upright source approval remains separate.</p><p>ทุก bank ใช้ canvas/scale คงที่ทั้งคลิป ไม่มี per-frame fit. Native clocks differ. Equal800ms mode retimes each bank; cross-game phases are fractional review positions, not bone alignment. Frame counts are exposures, not necessarily unique art.</p><button id="play">Play</button><button id="back">Previous</button><button id="next">Next</button><select id="mode"><option value="native">Recorded clocks</option><option value="equal">Equal800ms controls</option></select><input id="phase" type="range" min="0" max="15" value="0"><output id="time"></output><div id="banks" class="banks"></div><p>16drawings cannot fix incorrect midpoint poses, changed proportions or foot placement. Hidden hip/foot world contacts remain unknown. Keys are retained byte-for-byte at slots1,3,5,...15. APNG600ms stores37.5ms; GIF600ms quantizes to30/40ms. Uniform800ms controls preserve50ms16poses and100ms8keys.</p><script>const DATA=__DATA__;let playing=false,elapsed=0,last=0;const panels=DATA.map((b,i)=>{const el=document.createElement('div');el.className='bank'+([0,3,5].includes(i)?' native':'');el.innerHTML='<h3>'+b.label+'</h3><img><output></output>';banks.append(el);return el});function draw(){DATA.forEach((b,i)=>{const cycle=mode.value==='native'?b.cycle:800;const k=Math.floor(((elapsed%cycle)/cycle)*b.urls.length);panels[i].querySelector('img').src=b.urls[k];panels[i].querySelector('output').textContent='frame '+(k+1)+' / '+b.urls.length+' · cycle '+cycle+'ms';panels[i].dataset.frame=k});time.textContent=Math.round(elapsed)+'ms';phase.value=Math.floor((elapsed%600)/37.5)}function step(d){playing=false;elapsed=(Math.floor(elapsed/37.5)+d+16)%16*37.5;play.textContent='Play';draw()}play.onclick=()=>{playing=!playing;play.textContent=playing?'Pause':'Play';last=0};back.onclick=()=>step(-1);next.onclick=()=>step(1);phase.oninput=()=>{playing=false;play.textContent='Play';elapsed=Number(phase.value)*37.5;draw()};mode.onchange=draw;function tick(t){if(playing&&last)elapsed+=Math.min(t-last,100);last=t;if(playing)draw();requestAnimationFrame(tick)}window.REVIEW={DATA,draw,setTime:t=>{elapsed=t;draw()},get playing(){return playing}};draw();requestAnimationFrame(tick);</script>'''
    (STUDY/'frame-review.html').write_text(html.replace('__DATA__',json.dumps(data)))
    # Fixed-scale paired boards for visual source-pose review, not metric alignment.
    for name,source,own,n,scale in [('RO',rocap.parent,keys,8,4),('Valyria',valcap.parent,val,6,4)]:
        board=Image.new('RGB',(1024,536*((n+1)//2)),'#272727');d=ImageDraw.Draw(board)
        for i,p in enumerate(own):
            x=i%2*512;y=i//2*536
            src=Image.open(source/f'{i:04}.png').convert('RGBA');src=src.resize((src.width*scale,src.height*scale),Image.Resampling.NEAREST)
            art=Image.open(p).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
            board.paste(src,(x+4,y+72),src);board.paste(art,(x+188,y+100),art)
            d.text((x+8,y+15),f'{name} source {i+1} | our UNAPPROVED drawing',fill='white')
        board.save(evidence/(name+'-source-paintover-board.png'))
    print('BUILD v19: bound 8 keys /16 locked exposures /6 alternative paintovers; production blocked')


if __name__=='__main__':main()
