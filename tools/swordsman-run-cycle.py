"""Original authoring-only run, using the established fixed human leg chain.

A shorter support interval, airborne transfer, stronger knee recovery, loaded
compression and forward commitment distinguish this from a sped-up walk.
"""
import importlib.util
import math
from pathlib import Path
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'tools/swordsman-walk-cycle.py').exists())
spec = importlib.util.spec_from_file_location('shared_human_chain', ROOT/'tools/swordsman-walk-cycle.py')
shared = importlib.util.module_from_spec(spec); spec.loader.exec_module(shared)
ik, smooth, foot_point, serializable = shared.ik, shared.smooth, shared.foot_point, shared.serializable
DIRECTIONS = shared.DIRECTIONS
FEMUR, TIBIA, FOOT_LENGTH = shared.FEMUR, shared.TIBIA, shared.FOOT_LENGTH
HEEL, TOE, ANKLE_HEIGHT = shared.HEEL, shared.TOE, shared.ANKLE_HEIGHT
DUTY = .42
STANCE_TRAVEL = .72
CYCLE_DISTANCE = STANCE_TRAVEL/DUTY
CYCLE_SECONDS = .72
PHASE_NAMES = ('R contact', 'R load / L recovery', 'R drive', 'R release',
               'L contact', 'L load / R recovery', 'L drive', 'L release')


def foot(phase, side):
    q = (phase+(0. if side == 'R' else .5)) % 1.
    stance = q < DUTY
    if stance:
        pitch = .10*(1-smooth(q/.06)) if q < .06 else -.38*smooth((q-.22)/(DUTY-.22))
        pivot = HEEL if pitch > 0 else TOE if pitch < 0 else 0.
        y = STANCE_TRAVEL/2-CYCLE_DISTANCE*q+pivot-(pivot*math.cos(pitch)+ANKLE_HEIGHT*math.sin(pitch))
        z = ANKLE_HEIGHT*math.cos(pitch)-pivot*math.sin(pitch)
        clearance = 0.
    else:
        u = (q-DUTY)/(1-DUTY)
        pitch = -.38-.17*smooth(u/.20) if u < .20 else -.55+.65*smooth((u-.20)/.80)
        def endpoint(q0, angle, pivot):
            return STANCE_TRAVEL/2-CYCLE_DISTANCE*q0+pivot-(pivot*math.cos(angle)+ANKLE_HEIGHT*math.sin(angle))
        rear, front = endpoint(DUTY, -.38, TOE), endpoint(0., .10, HEEL)
        tangent = -CYCLE_DISTANCE*(1-DUTY)
        y = rear+(front-rear)*smooth(u)+tangent*u*(1-u)*(1-2*u)
        clearance = .15*math.sin(math.pi*u)**2
        z = -min(HEEL*math.sin(pitch)-ANKLE_HEIGHT*math.cos(pitch),
                 TOE*math.sin(pitch)-ANKLE_HEIGHT*math.cos(pitch))+clearance
    ankle = np.array((.105 if side == 'R' else -.105, y, z))
    points = {name: foot_point(ankle, pitch, value) for name, value in [('heel', HEEL), ('sole', 0.), ('toe', TOE)]}
    return {'phase': q, 'stance': stance, 'pitch': pitch, 'ankle': ankle, **points,
            'clearance': clearance,
            'contactKind': 'swing' if not stance else 'heel' if pitch > 0 else 'toe' if pitch < 0 else 'sole'}


def pose(phase):
    phase %= 1.
    feet = {s: foot(phase, s) for s in ('R', 'L')}
    sway = .018*math.sin(math.tau*phase)
    yaw = .075*math.sin(math.tau*phase)
    hips = {s: np.array((sway+sign*.105*math.cos(yaw), sign*.105*math.sin(yaw), 0.))
            for s, sign in [('R', 1), ('L', -1)]}
    reach = FEMUR+TIBIA-.003
    limits = [f['ankle'][2]+math.sqrt(reach*reach-float(np.dot(f['ankle'][:2]-hips[s][:2], f['ankle'][:2]-hips[s][:2])))
              for s, f in feet.items()]
    load_phase = (phase-.11+.25) % .5-.25
    hip_z = min(limits)-.035*math.exp(-(load_phase/.08)**2)
    pelvis = np.array((sway, 0., hip_z))
    chest = pelvis+np.array((0., .10, .48))
    neck = pelvis+np.array((0., .13, .60))
    head = pelvis+np.array((0., .16, .78))
    bones = {'pelvis': (pelvis-np.array((.105, 0., 0.)), pelvis+np.array((.105, 0., 0.))),
             'spine': (pelvis, chest), 'neck': (chest, neck), 'head': (neck, head)}
    for s, sign in [('R', 1), ('L', -1)]:
        f = feet[s]; hip = hips[s]+np.array((0., 0., hip_z)); knee = ik(hip, f['ankle'])
        f.update(hip=hip, knee=knee, thighForwardDegrees=math.degrees(math.atan2(knee[1]-hip[1], hip[2]-knee[2])))
        a, b = (hip-knee)/FEMUR, (f['ankle']-knee)/TIBIA
        f['kneeFlexDegrees'] = math.degrees(math.acos(float(np.clip(-np.dot(a, b), -1, 1))))
        f['poleDot'] = float(np.dot(knee-(hip+(f['ankle']-hip)*FEMUR/(FEMUR+TIBIA)), (0., 1., 0.)))
        bones[s+'-femur'], bones[s+'-tibia'] = (hip, knee), (knee, f['ankle'])
        bones[s+'-foot'] = (f['ankle'], f['ankle']+np.array((0., FOOT_LENGTH*math.cos(f['pitch']), FOOT_LENGTH*math.sin(f['pitch']))))
        shoulder = np.array((sway+sign*.205, .10, hip_z+.48))
        hand = np.array((sway+sign*.24, .05-.14*sign*math.cos(math.tau*phase), hip_z+.065))
        elbow = ik(shoulder, hand, .25, .24)
        bones[s+'-upperarm'], bones[s+'-forearm'] = (shoulder, elbow), (elbow, hand)
    contacts = sum(f['stance'] for f in feet.values())
    weights = {s: float(f['stance'])/max(contacts, 1) for s, f in feet.items()}
    return {'phase': phase, 'root': np.zeros(3), 'pelvis': pelvis, 'chest': chest, 'head': head,
            'bones': bones, 'feet': feet, 'supportWeights': weights}
