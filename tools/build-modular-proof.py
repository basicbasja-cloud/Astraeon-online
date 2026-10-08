#!/usr/bin/env python3
"""Generate DEV_ONLY geometric alignment proofs, not character designs.
Registration is inherited from the current painted Warrior v4 contract. The output
is reproducible; generated original modular strips remain in --sources for review.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']
LAYERS=['BaseBody','Hair','Outfit','Weapon','Headgear','BackAccessory']
TAGS=['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART']
CLIPS={'Idle':[350,450],'Walk':[100,120,100,120],'Run':[70,80,70,80],
       'BasicAttack':[160,70,230],'SkillAction':[180,240,180],'Hit':[90,170],
       'Death':[120,160,200,300]}

def definition(character,class_id,registration):
    extras={'Guard':[260,340],'Dash':[60,80,120]} if class_id=='Swordsman' else {'CastChannel':[180,240,180],'Blink':[70,90]}
    w=h=registration['cellSize']
    anchors={tuple(frame['anchor']) for clip in registration['clips'].values() for frame in clip['frames']}
    if len(anchors)!=1: raise ValueError('Existing registration has no shared root; review before selecting canvas')
    root_x,root_y=anchors.pop()
    canvas={'frameWidth':w,'frameHeight':h,'rootAnchorX':root_x,'rootAnchorY':root_y,'referenceHeight':registration['referenceHeight']}
    parts={layer.lower():{'slot':layer,'tags':TAGS,'frames':{}} for layer in LAYERS}
    parts['weapon-alt']={'slot':'Weapon','tags':TAGS,'frames':{}}
    clips={}
    for animation,durations in {**CLIPS,**extras}.items():
        clip={'loop':animation in ['Idle','Walk','Run','Guard','CastChannel'],'durations':durations,'directions':{}}
        for row,direction in enumerate(DIRECTIONS):
            frames=[]
            for index in range(len(durations)):
                phase=index/len(durations)*math.tau
                bob=round(math.sin(phase)*4) if animation not in ['Idle','Death'] else 0
                angle=math.pi/2+row*math.pi/4
                right=[round(root_x+math.cos(angle+math.pi/2)*34),root_y-82+bob]
                left=[round(root_x-math.cos(angle+math.pi/2)*34),root_y-82+bob]
                sockets={'root':[root_x,root_y],'head':[root_x,root_y-150+bob],
                         'hand_R':right,'hand_L':left,'back':[root_x,root_y-100+bob],
                         'waist':[root_x,root_y-65+bob]}
                frames.append({'frameIndex':index,'sockets':sockets})
            sequence={'frames':frames}
            # Rear views put the right-hand weapon behind the body without mirroring.
            if direction in ['NW','N','NE']:
                sequence['drawOrder']=['BackAccessory','Weapon','BaseBody','Outfit','Hair','Headgear']
            if animation=='BasicAttack':
                frames[1]['drawOrder']=['BackAccessory','BaseBody','Outfit','Hair','Headgear','Weapon']
            clip['directions'][direction]=sequence
        clips[animation]=clip
    return {'version':'0.1','characterId':character,'classId':class_id,'directions':DIRECTIONS,
            'mirroring':'none','tags':TAGS,'canvas':canvas,
            'source':{'status':'DEV_ONLY','reference':None,'approvedBy':None,
                      'camera':'Inherited world/v3/warrior-painted-locomotion.json camera; markers are not art',
                      'handedness':'right','normalization':{'sourceFrameWidth':w,'sourceFrameHeight':h,'sourceRootAnchor':[root_x,root_y],'scale':1},
                      'designLocks':['identity','face','hairstyle','hair length','proportions','costume construction','weapon design','weapon dimensions','handedness','palette','camera','scale','painted 2D style']},
            'slots':{layer:layer for layer in LAYERS},'defaultParts':{layer:layer.lower() for layer in LAYERS},
            'drawOrder':['BackAccessory','BaseBody','Outfit','Hair','Weapon','Headgear'],
            'clips':clips,'parts':parts,'atlases':{}}

def strips(d,source_root):
    c=d['canvas'];w,h=c['frameWidth'],c['frameHeight'];rx,ry=c['rootAnchorX'],c['rootAnchorY']
    colors={'BaseBody':(170,185,195,220),'Hair':(245,195,70,230),'Outfit':(80,175,205,170),
            'Weapon':(240,120,110,255),'Headgear':(175,135,240,230),'BackAccessory':(95,205,155,210)}
    for part_id,part in d['parts'].items():
        layer=part['slot'];color=colors[layer] if part_id!='weapon-alt' else (255,230,80,255)
        for animation,clip in d['clips'].items():
            count=len(clip['durations']);strip=Image.new('RGBA',(w*count,h*8),(0,0,0,0))
            for row,direction in enumerate(DIRECTIONS):
                for index,frame in enumerate(clip['directions'][direction]['frames']):
                    cell=Image.new('RGBA',(w,h),(0,0,0,0));draw=ImageDraw.Draw(cell);s=frame['sockets']
                    hx,hy=s['head'];bx,by=s['back'];handx,handy=s['hand_R'];wx,wy=s['waist']
                    if layer=='BaseBody':
                        draw.line([(rx,ry),(wx,wy),(hx,hy)],fill=color,width=9)
                        draw.ellipse((hx-22,hy-22,hx+22,hy+22),outline=color,width=4)
                        draw.line([(rx,ry),(rx-20,ry-4)],fill=color,width=5)
                        draw.line([(rx,ry),(rx+20,ry-4)],fill=color,width=5)
                        draw.line([s['hand_L'],(wx,wy),s['hand_R']],fill=color,width=5)
                        # Direction arrow proves eight independent authored rows.
                        a=math.pi/2+row*math.pi/4;tip=(rx+math.cos(a)*17,ry+math.sin(a)*17)
                        draw.line([(rx,ry),tip],fill=(255,255,255,255),width=3)
                    elif layer=='Hair':draw.arc((hx-26,hy-28,hx+26,hy+26),180,360,fill=color,width=6)
                    elif layer=='Outfit':draw.rectangle((wx-24,hy+26,wx+24,wy+6),outline=color,width=5)
                    elif layer=='Headgear':draw.polygon([(hx,hy-39),(hx-10,hy-28),(hx+10,hy-28)],outline=color)
                    elif layer=='BackAccessory':draw.ellipse((bx-38,by-22,bx+38,by+22),outline=color,width=4)
                    elif layer=='Weapon':
                        draw.line([(handx,handy+28),(handx,handy-55)],fill=color,width=6)
                        if d['classId']=='Swordsman':draw.line([(handx-11,handy+9),(handx+11,handy+9)],fill=color,width=5)
                        else:draw.ellipse((handx-11,handy-69,handx+11,handy-47),outline=color,width=4)
                        draw.ellipse((handx-3,handy-3,handx+3,handy+3),fill=(255,255,255,255))
                    strip.paste(cell,(index*w,row*h))
            path=source_root/'parts'/part_id/animation/'strip.png';path.parent.mkdir(parents=True,exist_ok=True)
            strip.save(path,format='PNG',compress_level=9)
    (source_root/'definition.json').write_text(json.dumps(d,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--sources',type=Path,default=Path('/tmp/astraeon-modular-sources'))
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('packer',args.repository/'tools/pack-modular-sprites.py')
    packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    registration=json.loads((args.repository/'world/v3/warrior-painted-locomotion.json').read_text())
    for character,class_id in [('swordsman-proof','Swordsman'),('mage-proof','Mage')]:
        d=definition(character,class_id,registration);root=args.sources/character
        strips(d,root);print(packer.pack(d,root,args.repository))
