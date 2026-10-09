#!/usr/bin/env python3
"""Technical pose guide only. No procedural pixels become production artwork."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'authoring/characters/true-modular/swordsman-male-v2'

def build():
    motion_path = ROOT / 'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'
    motion = json.loads(motion_path.read_text())
    pose = motion['actions']['Idle']['directions']['S']['frames'][0]
    guide = Image.new('RGBA', (1024, 1024))
    d = ImageDraw.Draw(guide)
    def points(ps): return [(round(x*3.2), round(y*3.2)) for x,y in ps]
    def poly(ps): d.polygon(points(ps), fill=(91,117,136,105), outline=(91,117,136,220), width=3)
    # Compact neutral body pose; anatomical right appears on screen left.
    poly([(156,132),(164,132),(166,140),(182,141),(190,153),(198,170),(204,176),(203,184),(196,186),(191,180),(184,164),(179,158),(176,185),(181,202),(186,226),(185,252),(190,260),(185,264),(171,264),(170,258),(172,231),(166,212),(160,208),(153,212),(147,231),(148,255),(150,260),(143,262),(132,262),(130,257),(137,250),(135,227),(139,203),(144,185),(141,158),(134,163),(129,176),(125,185),(117,185),(116,178),(119,173),(122,156),(130,143),(154,140)])
    d.ellipse([round(v*3.2) for v in (139,94,181,136)], fill=(127,149,162,80), outline=(127,149,162,200), width=3)
    for name in ['root','head','mainHand','offHand','waist','footL','footR','back']:
        a=pose['anchors'][name]; x,y=points([(a['x'],a['y'])])[0]
        color=(218,112,140,220) if name=='mainHand' else (76,175,182,220)
        d.line((x-10,y,x+10,y),fill=color,width=2)
        d.line((x,y-10,x,y+10),fill=color,width=2)
        d.text((x+12,y-12),name,fill=color)
    for y in [142,194,264]: d.line(points([(104,y),(216,y)]),fill=(76,175,182,110),width=2)
    DEST.mkdir(parents=True,exist_ok=True)
    guide.save(DEST/'south-pose-guide.png')
    contract={'schemaVersion':'2.0-authoring','classId':'Swordsman','bodyVariant':'male',
      'status':'REQUIRES_OWNER_VISUAL_REVIEW','registration':motion['registration'],
      'generationCanvas':[1024,1024],'generationScale':3.2,'directionOrder':motion['directions'],
      'pose':{'action':'Idle','direction':'S','frameIndex':0,'poseId':pose['id'],
        'motionTemplate':str(motion_path.relative_to(ROOT)), 'anchors':pose['anchors'],
        'timingAuthority':'baseline MotionTemplate; guide contains no independent clock'},
      'guidePurpose':'TECHNICAL_ONLY; never production art or a new gait',
      'authoringRule':'ISOLATED_COMPONENT_FROM_INCEPTION; no destructive full-character decomposition',
      'normalization':'whole canvas 1024 to 320; one shared transform; no alpha-bounds fitting',
      'neckOverlap':{'bodyNeck':[156,132,164,143],'headNeck':[155,128,165,141]},
      'identityReference':'authoring/characters/gait-rig-v50/approved-warrior-seed.png',
      'identityUse':'appearance reference only; no pixels copied into modular sources'}
    (DEST/'pose-contract.json').write_text(json.dumps(contract,indent=2)+'\n')

if __name__=='__main__': build()
