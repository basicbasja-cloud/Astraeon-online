"""Package authoring rig motion evidence, never painted or runtime assets."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('walk', ROOT/'tools/swordsman-walk-cycle.py')
walk = importlib.util.module_from_spec(spec); spec.loader.exec_module(walk)
parser = argparse.ArgumentParser(); parser.add_argument('--candidate', default='candidate-01'); args = parser.parse_args()
OUT = ROOT/'authoring/characters/swordsman-production/rig-walk'/args.candidate
record = json.loads((OUT/'shared-cycle.json').read_text())
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
colors = {'R': (69,164,221), 'L': (239,143,71)}
BG = (25,35,43)


def projection(x,y,z,direction):
    angle = -walk.DIRECTIONS.index(direction)*math.pi/4
    scale = 320/2.65
    return (160+scale*(-math.cos(angle)*x+math.sin(angle)*y),
            264+scale/math.sqrt(2)*(math.sin(angle)*x+math.cos(angle)*y-z))


def frame(direction, index):
    im = Image.new('RGB', (320,320), BG); draw = ImageDraw.Draw(im)
    phase = index/8
    # Tracking camera: stationary world grid moves backwards by exactly the
    # root travel. Stance contacts move with it, not against it.
    travel = phase*walk.CYCLE_DISTANCE
    for coord in range(-5,6):
        x = coord*.2
        draw.line([projection(x,-1.-travel,0,direction),projection(x,1.-travel,0,direction)],fill=(41,52,60))
        y = coord*.2-travel
        draw.line([projection(-1,y,0,direction),projection(1,y,0,direction)],fill=(41,52,60))
    if direction in ('W','E'):
        x=record['projections'][direction][index]['pelvis'][0]
        for y in range(45,276,10):draw.line((x,y,x,y+5),fill=(103,117,129))
        draw.text((10,44),'HIP LINE: '+('ahead ← | → behind' if direction=='W' else 'behind ← | → ahead'),font=small,fill=(181,195,205))
    source = Image.open(OUT/f'{direction}-{index}.png').convert('RGBA')
    im.paste(source,(0,0),source)
    draw = ImageDraw.Draw(im)
    draw.text((8,6),f'{direction}  {index}: {walk.PHASE_NAMES[index]}',font=font,fill=(232,237,241))
    draw.text((8,24),'R blue / L orange — authoring rig only',font=small,fill=(172,187,196))
    draw.line((154,264,166,264),fill=(157,170,179));draw.line((160,258,160,270),fill=(157,170,179))
    p = record['poses'][index]
    for row, side in enumerate(('R','L')):
        f = p['feet'][side]
        thigh=f.get('thighForwardDegrees',math.degrees(math.atan2(f['knee'][1]-f['hip'][1],f['hip'][2]-f['knee'][2])))
        text = f"{side}: {f['contactKind']} / thigh {thigh:+.0f}° / knee {f['kneeFlexDegrees']:.0f}°"
        draw.text((8,283+row*16),text,font=small,fill=colors[side])
        if f['stance']:
            kind = f['contactKind']; x,y = record['projections'][direction][index]['feet'][side][kind]
            draw.ellipse((x-3,y-3,x+3,y+3),outline=colors[side],width=1)
    im.save(OUT/f'proof-{direction}-{index}.png')
    return im


frames = {direction: [frame(direction, i) for i in range(8)] for direction in walk.DIRECTIONS}
sheet = Image.new('RGB',(2560,2560),BG)
for row,direction in enumerate(walk.DIRECTIONS):
    for i,im in enumerate(frames[direction]):sheet.paste(im,(i*320,row*320))
sheet.save(OUT/'eight-phase-all-directions.png')
for direction in walk.DIRECTIONS:
    for speed,name in [(1,'normal'),(.25,'quarter')]:
        images=frames[direction]
        images[0].save(OUT/f'{direction}-{name}.gif',save_all=True,append_images=images[1:],duration=int(140/speed),loop=0,disposal=2)
for speed,name in [(1,'normal'),(.25,'quarter')]:
    images=[]
    for i in range(8):
        im=Image.new('RGB',(960,520),BG);draw=ImageDraw.Draw(im)
        draw.text((12,8),'ARTICULATED WALK PROOF — '+walk.PHASE_NAMES[i],font=font,fill='white')
        for d,direction in enumerate(walk.DIRECTIONS):im.paste(frames[direction][i].resize((240,240)),((d%4)*240,40+(d//4)*240))
        images.append(im)
    images[0].save(OUT/f'all-directions-{name}.gif',save_all=True,append_images=images[1:],duration=int(140/speed),loop=0,disposal=2)

# Dense analytical sagittal motion supplies an independent continuous contact
# proof. Same chain/cycle as Blender, with a tracking floor and rigid feet.
# This is an offline diagram, never a skeletal game renderer.
images=[]
for i in range(56):
    phase=i/56;p=walk.pose(phase);im=Image.new('RGB',(560,400),BG);draw=ImageDraw.Draw(im)
    def point(v):return (280-v[1]*150,350-v[2]*150)
    draw.line((0,350,560,350),fill=(139,154,164),width=1)
    for k in range(-10,11):
        x=280-(k*.15-phase*walk.CYCLE_DISTANCE)*150
        draw.line((x,350,x,360),fill=(81,99,109),width=2)
    draw.text((12,8),'SAME FIXED-LENGTH CYCLE — continuous contact diagnostic',font=font,fill='white')
    draw.text((12,27),'Tracking floor / 65 mm swing clearance / 1.12 s per cycle',font=small,fill=(174,191,200))
    for side in ('R','L'):
        f=p['feet'][side];color=colors[side]
        for bone in (side+'-femur',side+'-tibia',side+'-upperarm',side+'-forearm'):
            a,b=p['bones'][bone];draw.line((point(a),point(b)),fill=color,width=8 if 'femur' in bone else 6)
        for name in ('hip','knee','ankle'):
            x,y=point(f[name]);draw.ellipse((x-4,y-4,x+4,y+4),fill=(218,226,230))
        heel,toe=point(f['heel']),point(f['toe']);draw.line((heel,toe),fill=color,width=6)
        if f['stance']:
            x,y=point(f[f['contactKind']]);draw.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2)
    for name in ('spine','neck','head'):
        a,b=p['bones'][name];draw.line((point(a),point(b)),fill=(179,193,200),width=9)
    x,y=point(p['head']);draw.ellipse((x-19,y-29,x+19,y+4),fill=(179,193,200))
    for row,side in enumerate(('R','L')):draw.text((12,370+row*13),f"{side}: {p['feet'][side]['contactKind']}",font=small,fill=colors[side])
    images.append(im)
for speed,name in [(1,'normal'),(.25,'quarter')]:
    images[0].save(OUT/f'continuous-contact-{name}.gif',save_all=True,append_images=images[1:],duration=int(20/speed),loop=0,disposal=2)

html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ASTRAEON authoring walk rig</title><style>body{font:16px system-ui;background:#19232b;color:#edf3f7;max-width:1050px;margin:auto;padding:20px}button,select,input{font:inherit;margin:8px}canvas{width:min(100%,640px);height:auto;background:#19232b}img{max-width:100%;height:auto}p{max-width:850px}#grid{display:flex;flex-wrap:wrap;gap:20px}a{color:#8bccf5}</style><h1>Authoring walk rig — eight phases</h1><p>Fixed femur/tibia/foot lengths, forward knee poles and rigid heel/sole/toe pivots. Blue is anatomical right; orange is anatomical left. The grid tracks virtual forward travel to expose foot skating. This proof does not approve or replace painted Swordsman artwork.</p><label>Direction <select id="direction"></select></label><label>Speed <select id="speed"><option value="1">Normal</option><option value="0.25">Quarter</option></select></label><button id="play">Pause</button><button id="previous">Previous frame</button><button id="next">Next frame</button><label>Frame <input id="phase" type="range" min="0" max="7" value="0"></label><label><input id="size" type="checkbox">Gameplay size</label><div><canvas id="canvas" width="320" height="320"></canvas></div><p id="status"></p><p><a href="eight-phase-all-directions.png">All directions and phases</a> · <a href="shared-cycle.json">Shared pose cycle</a> · <a href="walk-proof.blend">Editable Blender rig</a></p><div id="grid"><img src="continuous-contact-normal.gif" alt="Continuous articulated contact motion" width="560"><img src="W-normal.gif" alt="Eight-phase walk from the side" width="320"></div><script>
const dirs=['S','SW','W','NW','N','NE','E','SE'],names=['R contact','R down / L lift','R passing','R up / L reach','L contact','L down / R lift','L passing','L up / R reach'];
const sel=document.querySelector('#direction'),ctx=document.querySelector('#canvas').getContext('2d'),images={};let frame=0,playing=true,last=performance.now(),acc=0;
for(const d of dirs){sel.add(new Option(d,d));images[d]=Array.from({length:8},(_,i)=>{const im=new Image();im.src=`proof-${d}-${i}.png`;return im});}sel.value='W';
function paint(){const d=sel.value,im=images[d][frame];if(im.complete){ctx.clearRect(0,0,320,320);ctx.drawImage(im,0,0)}document.querySelector('#phase').value=frame;document.querySelector('#status').textContent=`${d} · phase ${frame}/7 · ${names[frame]} · authoring only`;document.body.dataset.direction=d;document.body.dataset.frame=frame;}
function step(n){playing=false;document.querySelector('#play').textContent='Play';frame=(frame+n+8)%8;paint()}
document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'Pause':'Play';acc=0};document.querySelector('#previous').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.querySelector('#phase').oninput=e=>{playing=false;document.querySelector('#play').textContent='Play';frame=+e.target.value;paint()};sel.onchange=paint;
document.querySelector('#size').onchange=e=>document.querySelector('#canvas').style.width=e.target.checked?'154px':'min(100%,640px)';
function tick(now){acc+=(now-last)*+document.querySelector('#speed').value;last=now;if(playing&&acc>=140){frame=(frame+Math.floor(acc/140))%8;acc%=140}paint();requestAnimationFrame(tick)}requestAnimationFrame(tick);
</script></html>'''
(OUT/'preview.html').write_text(html)
print('Packaged authoring-only rig: all eight directions, normal/quarter, single-frame and continuous contact proof.')
