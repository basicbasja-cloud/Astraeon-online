"""Reproduce the registered SE pilot specification from immutable painted source.

These are inspected atlas rectangles and once-only attachment fitting values,
not equal-grid assumptions, automatic anatomy inference, or per-frame fitting.
"""
import hashlib
import json
import math
from pathlib import Path

from painted_character_factory import DIRECTIONS, sample_pose

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'authoring/characters/swordsman-production/fresh-2d/painted-rig-01'


def main():
    joints = {'root': [0, 0, 0], 'waist': [0, 0, 1.70], 'neck': [0, 0, 2.78],
              'head': [0, 0, 3.35], 'back': [0, 0.1, 2.36],
              'shoulder_R': [-0.42, -0.02, 2.70], 'elbow_R': [-0.56, -0.05, 2.13],
              'wrist_R': [-0.57, -0.10, 1.68], 'grip_R': [-0.58, -0.12, 1.46],
              'shoulder_L': [0.42, -0.02, 2.70], 'elbow_L': [0.53, -0.05, 2.16],
              'wrist_L': [0.53, -0.09, 1.70], 'grip_L': [0.53, -0.09, 1.50],
              'hip_R': [-0.25, 0, 1.61], 'knee_R': [-0.29, -0.02, 0.83],
              'sole_R': [-0.30, -0.24, 0.05], 'hip_L': [0.25, 0, 1.61],
              'knee_L': [0.28, -0.03, 0.85], 'sole_L': [0.29, -0.24, 0.05]}
    def key(time, elbow, wrist, grip, axis):
        return {'time': time, 'elbow_R': elbow, 'wrist_R': wrist, 'grip_R': grip, 'weapon_axis': axis}
    rest = [0, -0.82, -0.82]
    spec = {'schemaVersion': 1, 'id': 'swordsman-painted-rig-01', 'status': 'DEV_ONLY',
            'directions': DIRECTIONS, 'mirroring': 'none',
            'registration': {'canvas': [320, 320], 'root': [160, 264], 'referenceHeight': 176},
            'bodyJoints': joints, 'restWeaponAxis': rest,
            'requiredActions': ['Idle','Walk','Run','Sprint','BasicAttack','SkillAction','CastChannel',
                                'CastRelease','Guard','Dash','Hit','Death','Interact','Pickup','ItemUse','Respawn'],
            'images': {'SE': {'file': 'source/SE-parts.png', 'size': [1024,1536],
                             'sha256': hashlib.sha256((FOLDER/'source/SE-parts.png').read_bytes()).hexdigest()},
                       'SE-hidden': {'file': 'source/SE-hidden-surfaces.png', 'size': [1536,1024],
                                     'sha256': hashlib.sha256((FOLDER/'source/SE-hidden-surfaces.png').read_bytes()).hexdigest()}},
            'views': {'SE': {'state': 'REGISTERED_PILOT', 'ownerApproval': 'PENDING', 'attachments': []}},
            'motions': {
                'Idle': {'state': 'AUTHORED_PILOT', 'loop': True, 'durations': [150]*8},
                'Walk': {'state': 'AUTHORED_PILOT', 'loop': True, 'durations': [55]*16},
                'BasicAttack': {'state': 'AUTHORED_PILOT', 'loop': False,
                                'durations': [65,65,60,60,55,45,35,35,45,65,80,80,85,85,85,85],
                                'impactFrame': 8, 'keys': [
                                    key(0, joints['elbow_R'], joints['wrist_R'], joints['grip_R'], rest),
                                    key(250, [-0.66,0.05,2.38],[-0.68,0.08,2.91],[-0.66,0.10,3.05],[0,0.10,1.0]),
                                    key(340, [-0.62,-0.16,2.32],[-0.46,-0.32,2.81],[-0.40,-0.35,2.93],[0,-0.18,1.0]),
                                    key(460, [-0.44,-0.42,2.20],[-0.18,-0.72,1.91],[-0.10,-0.83,1.72],[0,-1.12,-0.25]),
                                    key(625, [-0.49,-0.35,2.07],[-0.30,-0.61,1.77],[-0.23,-0.70,1.59],[0,-0.65,-0.74]),
                                    key(1080, joints['elbow_R'], joints['wrist_R'], joints['grip_R'], rest)]}},
            'variants': {'default': {'outfit':'bronze','weapon':'bronze','cape':'on','hair':'on'},
                         'training': {'outfit':'bronze','weapon':'training','cape':'on','hair':'on'},
                         'steel': {'outfit':'steel','weapon':'bronze','cape':'on','hair':'on'},
                         'body-only': {'outfit':'none','weapon':'none','cape':'off','hair':'off'},
                         'no-weapon': {'outfit':'bronze','weapon':'none','cape':'on','hair':'on'},
                         'no-cape': {'outfit':'bronze','weapon':'bronze','cape':'off','hair':'on'}},
            'limits': ['Only SE source art exists; never mirror or synthesize another view.',
                       'Pilot motion is unapproved and needs redraws for out-of-plane poses.',
                       'Complete alternate outfit, offhand and headgear art remain missing.',
                       'No playable or release-ready character is claimed.']}
    bones = sample_pose(spec, 'SE', 'Idle', 0)['bones']
    def add(name, bone, slot, bounds, pivot, axis, depth, select=None, scale=None, image='SE'):
        x,y,x2,y2 = bounds
        if scale is None:
            scale = math.dist(*bones[bone])/math.dist(pivot,axis)
        spec['views']['SE']['attachments'].append({'id': name, 'image': image, 'bone': bone,
                   'slot': slot, 'rect': [x,y,x2-x,y2-y], 'pivot': pivot, 'axisEnd': axis,
                   'depth': depth, 'scale': scale, 'select': select or {}})
    add('head-base','head','BaseBody',[55,44,234,276],[149,258],[149,130],11,scale=0.21)
    add('hair-silver','head','Hair',[264,25,537,256],[404,300],[404,150],40,{'hair':'on'},scale=0.21)
    add('torso-under','torso','BaseBody',[560,20,740,278],[660,244],[660,45],10,scale=0.235)
    add('torso-bronze','torso','Outfit',[784,5,1018,337],[887,227],[892,46],23,{'outfit':'bronze'},scale=0.235)
    add('torso-steel','torso','Outfit',[786,1191,1016,1518],[890,1400],[890,1226],23,{'outfit':'steel'},scale=0.235)
    add('arm-R-skin','upper_R','BaseBody',[72,290,179,505],[127,317],[104,483],12)
    add('fore-R-skin','fore_R','BaseBody',[309,297,457,499],[335,324],[431,473],13)
    add('hand-R-skin','hand_R','BodyHands',[127,42,364,357],[196,84],[263,288],36,image='SE-hidden')
    add('hand-R-grip','hand_R','Hands',[868,36,1111,357],[954,80],[1019,287],38,{'outfit':['bronze','steel']},image='SE-hidden')
    add('arm-L-skin','upper_L','BaseBody',[840,306,961,502],[882,332],[930,478],12)
    add('fore-L-skin','fore_L','BaseBody',[51,516,203,708],[80,540],[177,683],13)
    add('hand-L-skin','hand_L','BodyHands',[460,36,705,402],[529,78],[635,340],36,image='SE-hidden')
    add('hand-L-rest','hand_L','Hands',[1222,31,1441,400],[1293,77],[1380,336],38,{'outfit':['bronze','steel']},image='SE-hidden')
    add('sleeve-R','upper_R','Outfit',[548,507,731,714],[653,554],[630,687],24,{'outfit':'bronze'})
    add('bracer-R','fore_R','Outfit',[834,512,985,714],[881,543],[947,684],25,{'outfit':'bronze'})
    add('sleeve-L','upper_L','Outfit',[57,707,231,917],[144,753],[172,889],21,{'outfit':'bronze'})
    add('bracer-L','fore_L','Outfit',[305,719,456,917],[392,749],[335,886],22,{'outfit':'bronze'})
    add('thigh-R-skin','thigh_R','BaseBody',[98,416,312,926],[236,460],[174,870],10,image='SE-hidden')
    add('thigh-L-skin','thigh_L','BaseBody',[457,418,718,928],[519,470],[648,870],10,image='SE-hidden')
    add('shin-R-skin','shin_R','BaseBody',[833,425,1090,973],[943,459],[1002,944],12,image='SE-hidden')
    add('shin-L-skin','shin_L','BaseBody',[1224,424,1481,955],[1316,461],[1430,925],12,image='SE-hidden')
    add('trouser-R','thigh_R','Outfit',[570,720,710,931],[646,751],[620,906],20,{'outfit':['bronze','steel']})
    add('trouser-L','thigh_L','Outfit',[815,720,970,929],[870,750],[900,906],20,{'outfit':['bronze','steel']})
    add('boot-R','shin_R','Outfit',[568,937,708,1187],[627,963],[635,1167],21,{'outfit':['bronze','steel']})
    add('boot-L','shin_L','Outfit',[848,938,1003,1177],[909,965],[949,1150],21,{'outfit':['bronze','steel']})
    add('cape-gold','torso','BackAccessory',[7,1192,268,1514],[150,1388],[155,1190],5,{'cape':'on'},scale=0.235)
    add('sword-bronze','weapon','Weapon',[300,1175,532,1514],[347,1229],[520,1494],34,{'weapon':'bronze'})
    add('sword-training','weapon','Weapon',[545,1192,759,1499],[596,1237],[748,1486],34,{'weapon':'training'})
    (FOLDER/'rig.json').write_text(json.dumps(spec, indent=2)+'\n', encoding='utf-8')
    print(FOLDER/'rig.json')


if __name__ == '__main__':
    main()
