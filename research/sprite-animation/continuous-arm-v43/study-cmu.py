"""Execute the retained MIT ASF/AMC reader with a local exact XYZ Euler adapter.
No source motion channels are relabelled or shortened. Acclaim Y-up retained.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
def euler2mat(x,y,z):
    cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
raw=(P/'reference/amc_parser.py').read_text()
adapted='\n'.join(l for l in raw.splitlines() if not l.startswith(('import matplotlib','from transforms3d','from mpl_toolkits')))
ns={'__name__':'retained_mit_reader','euler2mat':euler2mat};exec(compile(adapted,'retained_amc_parser','exec'),ns)
joints=ns['parse_asf'](P/'reference/26.asf');motions=ns['parse_amc'](P/'reference/26_09.amc')
def angle(a,b):
    return math.degrees(math.acos(float(np.clip(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))
records=[];scale=.0254/.45
for i,m in enumerate(motions):
    joints['root'].set_motion(m);pts={k:j.coordinate[:,0].tolist() for k,j in joints.items()};arms={}
    for s in ['l','r']:
        shoulder=np.array(pts[s+'clavicle']);elbow=np.array(pts[s+'humerus']);wrist=np.array(pts[s+'wrist']);hand=np.array(pts[s+'hand'])
        arms[s]=dict(elbow_flex_deg=angle(elbow-shoulder,wrist-elbow),wrist_deviation_deg=angle(wrist-elbow,hand-wrist),wrist_roll_channel_deg=m[s+'wrist'][0])
    records.append(dict(frame=i+1,time_seconds=i/120,points_asf=pts,arms=arms))
def bind(p):return dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=dict(source='CMU Graphics Lab subject26 trial09: bend, pick up',sample_rate_hz=120,units='ASF/Y-up, multiply by .0254/.45 for metres',inputs=[bind(P/'reference'/n) for n in ['26.asf','26_09.amc','amc_parser.py','AMCParser-LICENSE','cmu-faq.html','cmu-subject26.html']],reader_adapter='Exact static-axis XYZ = Rz@Ry@Rx; remove display/transforms3d imports only. No frame/channel interpolation.',frames=records,video_scope='Real source preview checked; cropped below waist, not a visible sole/contact benchmark. Preview PTS not asserted to be synchronized to AMC.',production_pass=False)
(P/'cmu-motion.json').write_text(json.dumps(out,indent=2)+'\n')
# Three independent orthographic axes: original motion, no retarget or character paint.
sheet=Image.new('RGB',(1600,960),(29,35,42));draw=ImageDraw.Draw(sheet)
ids=np.linspace(0,len(records)-1,16).astype(int).tolist();ranges=np.array([v for r in records for v in r['points_asf'].values()]);lo=ranges.min(0);hi=ranges.max(0);pix=180/max(hi-lo)
for n,i in enumerate(ids):
    r=records[i];ox=n%4*400;oy=n//4*240
    draw.text((ox+5,oy+5),f'AMC {i+1} / {i/120:.3f}s',fill='white')
    for view,axes in enumerate([(0,1),(2,1),(0,2)]):
        def project(k):
            a=np.array(r['points_asf'][k]);return (ox+view*130+65+(a[axes[0]]-(lo[axes[0]]+hi[axes[0]])/2)*pix,oy+220-(a[axes[1]]-lo[axes[1]])*pix)
        for k,j in joints.items():
            if j.parent:
                col=(255,145,40) if k.startswith('l') else (40,155,255) if k.startswith('r') else (210,210,210)
                draw.line([project(j.parent.name),project(k)],fill=col,width=2)
    draw.text((ox+5,oy+223),'XY         ZY          XZ',fill=(150,170,180))
sheet.save(P/'cmu-skeleton-sheet.png')
summary={s:{k:[min(r['arms'][s][k] for r in records),max(r['arms'][s][k] for r in records)] for k in ['elbow_flex_deg','wrist_deviation_deg','wrist_roll_channel_deg']} for s in ['l','r']}
(P/'cmu-arm-summary.json').write_text(json.dumps(dict(total_frames=len(records),duration_seconds=(len(records)-1)/120,angles=summary,scope='Measured source skeletal vectors, not universal safe anatomical limits or painted-hand correctness'),indent=2)+'\n')
print(json.dumps(summary));print('frames',len(records))
