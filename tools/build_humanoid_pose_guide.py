"""Original 3D anatomical planning diagrams; never production sprite artwork.

RO1 references inform compact proportions and overhead-cut phase order. Geometry
is explicitly VISUAL_DERIVED, not decoded RO bones (ACT contains no skeleton).
All directions project the same right-handed pose; no 2D mirroring or limb warps.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/characters/baselines/humanoid-ro1-v1/pose-guide'
DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
PHASES = ['ready', 'anticipation', 'acceleration', 'contact', 'followThrough', 'recovery']
FRAMES = [0, 4, 6, 7, 10, 14]
# Direction vectors, not independently positioned elbows/wrists. Fixed lengths.
UPPER = [[.70,-.40,.59],[.55,-.50,.67],[.38,.59,.71],[.40,.65,-.65],[.15,.55,-.82],[.64,.35,.68]]
FORE = [[-.38,.60,.70],[-.35,.45,.82],[-.28,.93,.23],[-.38,.77,-.51],[-.58,.65,-.49],[-.36,.70,.61]]
SWORD = [-105,-125,5,140,163,-5]
LEAN = [0,-3,4,12,15,4]


def add(a, b): return [x+y for x,y in zip(a,b)]
def mul(a, s): return [x*s for x in a]
def unit(a): return mul(a, 1/math.sqrt(sum(x*x for x in a)))
def length(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def knee(hip, foot):
    direction=unit([b-a for a,b in zip(hip,foot)])
    distance=length(hip,foot)
    along=distance/2
    pole=[0,1,0]
    dot=sum(a*b for a,b in zip(pole,direction))
    normal=unit([a-dot*b for a,b in zip(pole,direction)])
    return add(add(hip,mul(direction,along)),mul(normal,math.sqrt(52**2-along**2)))


def pose(i):
    drop = [0,0,2,6,7,1][i]
    forward = LEAN[i]
    pelvis = [0,0,99-drop]
    neck = [0,forward,145-drop]
    shoulder_r = [25,forward,138-drop]
    shoulder_l = [-25,forward,138-drop]
    elbow_r = add(shoulder_r,mul(unit(UPPER[i]),34))
    wrist_r = add(elbow_r,mul(unit(FORE[i]),32))
    hand_r = add(wrist_r,mul(unit(FORE[i]),8))
    elbow_l = add(shoulder_l,mul(unit([-.30,.15,-.94]),34))
    wrist_l = add(elbow_l,mul(unit([.70,.70,.20]),32))
    angle = math.radians(SWORD[i]);blade = [0,math.sin(angle),math.cos(angle)]
    points = dict(pelvis=pelvis,neck=neck,chest=[0,forward,138-drop],head=[0,forward,176-drop],
                  shoulderR=shoulder_r,elbowR=elbow_r,wristR=wrist_r,handR=hand_r,
                  shoulderL=shoulder_l,elbowL=elbow_l,wristL=wrist_l,
                  hipR=[14,0,99-drop],hipL=[-14,0,99-drop],
                  kneeR=[17,5,51-drop/2],kneeL=[-17,22,51-drop/2],
                  footR=[19,-8,0],footL=[-19,15,0],
                  grip=hand_r,guard=add(hand_r,mul(blade,12)),
                  pommel=add(hand_r,mul(blade,-10)),tip=add(hand_r,mul(blade,88)))
    for side in ['L','R']:
        points['knee'+side]=knee(points['hip'+side],points['foot'+side])
        assert abs(length(points['hip'+side],points['knee'+side])-52)<1e-8
        assert abs(length(points['foot'+side],points['knee'+side])-52)<1e-8
    assert abs(length(points['shoulderR'],points['elbowR'])-34)<1e-8
    assert abs(length(points['elbowR'],points['wristR'])-32)<1e-8
    return points


def project(p, direction):
    yaw = math.radians(direction*45)
    x = p[0]*math.cos(yaw)+p[1]*math.sin(yaw)
    y = -p[0]*math.sin(yaw)+p[1]*math.cos(yaw)
    elevation = math.radians(30)
    return [160-x,264+y*math.sin(elevation)-p[2]*math.cos(elevation),y*math.cos(elevation)+p[2]*math.sin(elevation)]


def render(points, direction, phase):
    im = Image.new('RGB',(320,320),'#233541');draw=ImageDraw.Draw(im)
    p={k:project(v,direction)for k,v in points.items()}
    draw.line((10,264,310,264),fill='#415969',width=1)
    primitives=[]
    def segment(a,b,color,width):
        primitives.append(((p[a][2]+p[b][2])/2,'line',[p[a][:2],p[b][:2]],color,width))
    for side in ['L','R']:
        segment('hip'+side,'knee'+side,'#718795',14)
        segment('knee'+side,'foot'+side,'#8497a5',12)
        color='#ffba59' if side=='R' else '#75add0'
        segment('shoulder'+side,'elbow'+side,color,12)
        segment('elbow'+side,'wrist'+side,color,10)
    primitives.append((p['neck'][2],'poly',[p[k][:2]for k in ['shoulderR','shoulderL','hipL','hipR']],'#98aabc',1))
    segment('chest','head','#b4c5cf',12)
    segment('pommel','guard','#bd8157',5)
    segment('guard','tip','#e8eff5',5)
    primitives.append((p['head'][2],'head',[p['head'][:2]],'#ccd8df',1))
    for _,kind,coords,color,width in sorted(primitives,key=lambda item:item[0]):
        if kind=='line':draw.line([tuple(v)for v in coords],fill=color,width=width)
        elif kind=='poly':draw.polygon([tuple(v)for v in coords],fill=color)
        else:
            x,y=coords[0];draw.ellipse((x-19,y-23,x+19,y+23),fill=color)
            forward=project(add(points['head'],[0,20,0]),direction)
            draw.line((x,y,forward[0],forward[1]),fill='#294555',width=3)
    for name in ['shoulderR','elbowR','wristR','grip']:
        x,y=p[name][:2];draw.ellipse((x-3,y-3,x+3,y+3),fill='#243440',outline='#ffe2a0')
    draw.text((7,6),f'{DIRECTIONS[direction]} / {phase}',fill='white')
    draw.text((7,302),'RIGHT ARM gold / derived planning only',fill='#c1d1dc')
    return im,p


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    board=Image.new('RGB',(320*6,320*8),'#17232d');records=[]
    for d,direction in enumerate(DIRECTIONS):
        strip=Image.new('RGB',(320*6,320),'#17232d')
        for i,phase in enumerate(PHASES):
            points=pose(i);im,projected=render(points,d,phase)
            im.save(OUT/f'{direction}-{phase}.png');board.paste(im,(i*320,d*320))
            strip.paste(im,(i*320,0))
            records.append(dict(direction=direction,phase=phase,targetFrame=FRAMES[i],
                                worldPoints=points,projectedPoints={k:v[:2]for k,v in projected.items()}))
        strip.save(OUT/f'{direction}-six-phases.png')
    board.save(OUT/'eight-directions-six-phases.png')
    (OUT/'pose-plan.json').write_text(json.dumps(dict(classification='VISUAL_DERIVED',status='PLANNING_ONLY',
      rightHanded=True,projection='orthographic; camera elevation 30 degrees; eight yaw angles',
      limitations=['Not raw RO anatomical coordinates','Not final art','Wrist articulation not yet validated','Occlusion in guide is approximate segment depth sorting'],
      sourceReferences=['private-ro-reference/rebuild-ro1/attack','private-ro-reference/true8dir/attack-raw.png'],
      records=records),indent=2)+'\n')
    print('48 original planning views exported; fixed arm lengths and consistent right-hand ownership.')


if __name__=='__main__':main()
