"""Actual source phase plus reviewed visible shoe targets, not hidden image bones."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
source_path=P.parent/'pickup-pilot-v31/source/source.json'
source=json.loads(source_path.read_text())
raw_path=P.parent/'neck-motion-v36/motion-attempt2-raw.png'
raw=Image.open(raw_path).convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
guide=Image.new('RGBA',raw.size,'#263443');guide.alpha_composite(raw)
draw=ImageDraw.Draw(guide)
heady=[f['points']['head']['xy'][1] for f in source['frames']]
headx=[f['points']['head']['xy'][0] for f in source['frames']]
fractions=[(y-heady[0])/(heady[3]-heady[0]) for y in heady]
rows=[]
for i,fraction in enumerate(fractions):
    ox,oy=i%4*384,i//4*512
    # Two explicit observed art calibrations: collar midpoint at rest and peak.
    neck=[187+(155.5-187)*fraction,130.5+(244-130.5)*fraction]
    for x in [125,205]:draw.line((ox+x,oy+410,ox+x,oy+500),fill='#65ffff',width=2)
    draw.line((ox+100,oy+466,ox+175,oy+466),fill='#65ffff',width=2)
    draw.line((ox+185,oy+485,ox+270,oy+485),fill='#65ffff',width=2)
    x,y=neck;draw.ellipse((ox+x-7,oy+y-7,ox+x+7,oy+y+7),outline='#ff72f3',width=3)
    draw.text((ox+8,oy+8),f'{i+1}: source {source["frames"][i]["source_time_seconds"]:.3f}s',font=font,fill='white')
    draw.text((ox+8,oy+30),f'Collar ({x:.0f},{y:.0f}); feet fixed',font=font,fill='#ffb9f9')
    draw.rectangle((ox+1,oy+1,ox+382,oy+510),outline='#8196a9',width=1)
    rows.append(dict(index=i,source_time_seconds=source['frames'][i]['source_time_seconds'],source_head_vertical_fraction=fraction,
                     desired_collar_surface_midpoint_native=neck,far_forefoot_toe_sole_native=[125,466],near_forefoot_toe_sole_native=[205,485],
                     definition='Authored visible-surface phase targets calibrated at rest/peak, not actual detected image joints'))
guide.convert('RGB').save(P/'repair-guide.png')
sheet=Image.new('RGBA',(1536,1024),'#263443')
for i,frame in enumerate(source['frames']):
    path=ROOT/frame['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['sha256']
    im=Image.open(path).convert('RGBA');sheet.alpha_composite(im,(i%4*384,i//4*512))
sheet.convert('RGB').save(P/'source-poses.png')
(P/'guide-contract.json').write_text(json.dumps(dict(source=dict(path=str(source_path.relative_to(ROOT)),sha256=hashlib.sha256(source_path.read_bytes()).hexdigest()),
    raw_art=dict(path=str(raw_path.relative_to(ROOT)),sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest()),
    calibration_indices=[0,3],frames=rows,old_own_attack_used=False),indent=2)+'\n')
