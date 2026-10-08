"""Original fixed-chain sword-action pose sequence for offline painted baking."""
import importlib.util
import math
from pathlib import Path
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'tools/swordsman-walk-cycle.py').exists())
spec = importlib.util.spec_from_file_location('human_chain', ROOT/'tools/swordsman-walk-cycle.py')
shared = importlib.util.module_from_spec(spec); spec.loader.exec_module(shared)
ik, serializable = shared.ik, shared.serializable
FEMUR, TIBIA, FOOT_LENGTH = shared.FEMUR, shared.TIBIA, shared.FOOT_LENGTH

# Each pose specifies pelvis advance, loading, hand offsets above the pelvis
# and the carried blade vector. One sequence drives every cosmetic surface.
ATTACK = [
    (0., 0., 0., [.24, -.04, .05], [-.24, -.04, .05], [.15, .45, -.9]),
    (.14, -.025, .014, [.25, -.14, .34], [-.24, -.10, .08], [.20, -.55, .90]),
    (.28, -.025, .020, [.26, -.17, .38], [-.24, -.12, .08], [.25, -.55, .90]),
    (.43, .085, .030, [.24, .28, .11], [-.24, -.06, .04], [.20, .98, -.18]),
    (.57, .060, .025, [.27, .17, .02], [-.24, -.02, .05], [.35, .65, -.72]),
    (.72, .020, .008, [.25, .05, .03], [-.24, -.03, .05], [.20, .50, -.84]),
    (.86, .005, .002, [.24, -.02, .05], [-.24, -.04, .05], [.15, .45, -.9]),
    (1., 0., 0., [.24, -.04, .05], [-.24, -.04, .05], [.15, .45, -.9]),
]

# Reusable committed sword thrust: no elemental or permanent effect layer.
# Retraction stays low, distinguishing it from BasicAttack's raised wind-up.
SKILL = [
    (0., 0., 0., [.24, -.04, .05], [-.24, -.04, .05], [.15, .45, -.9]),
    (.16, -.035, .018, [.25, -.15, .09], [-.24, -.08, .09], [.25, .80, .10]),
    (.30, -.040, .025, [.26, -.18, .10], [-.24, -.10, .10], [.25, .90, .08]),
    (.44, .115, .035, [.26, .35, .20], [-.24, -.04, .09], [.25, .95, .05]),
    (.56, .110, .032, [.26, .34, .20], [-.24, -.04, .09], [.25, .95, .05]),
    (.72, .045, .012, [.25, .11, .13], [-.24, -.04, .07], [.20, .70, -.45]),
    (.88, .008, .003, [.24, -.02, .06], [-.24, -.04, .05], [.15, .45, -.9]),
    (1., 0., 0., [.24, -.04, .05], [-.24, -.04, .05], [.15, .45, -.9]),
]


def parameters(phase, animation='BasicAttack'):
    sequence = {'BasicAttack': ATTACK, 'SkillAction': SKILL}[animation]
    phase = float(np.clip(phase, 0, 1))
    for a, b in zip(sequence, sequence[1:]):
        if phase <= b[0]:
            t = shared.smooth((phase-a[0])/(b[0]-a[0]))
            return [(1-t)*np.asarray(x)+t*np.asarray(y) for x, y in zip(a[1:], b[1:])]
    return [np.asarray(x) for x in sequence[-1][1:]]


def blade_angle(phase, animation, azimuth, source_angle):
    """Continuous painted blade arc, calibrated to the actual source grip/tip.

    Interpolating 3D vectors through a camera-facing orientation is singular
    when projected. Painted blades keep their dimensions, so interpolate the
    inspected key orientations instead of rotating from that tiny projection.
    """
    sequence = {'BasicAttack': ATTACK, 'SkillAction': SKILL}[animation]
    angles = []
    for index, key in enumerate(sequence):
        x, y, z = key[-1]
        angle = math.atan2((math.sin(azimuth)*x+math.cos(azimuth)*y-z)/math.sqrt(2),
                           -math.cos(azimuth)*x+math.sin(azimuth)*y)
        angles.append(source_angle if index in (0, len(sequence)-1) else angle)
    # Unwrap adjacent keys: independently wrapping each key around the rest
    # angle made NW interpolate a 261-degree detour during the strike.
    delta = np.unwrap(np.asarray(angles))-source_angle
    for a, b, first, second in zip(sequence, sequence[1:], delta, delta[1:]):
        if phase <= b[0]:
            t = shared.smooth((max(phase, a[0])-a[0])/(b[0]-a[0]))
            return float((1-t)*first+t*second)
    return float(delta[-1])


def pose(phase, animation='BasicAttack'):
    advance, loading, right, left, blade = parameters(phase, animation)
    hips = {s: np.array((sign*.105, float(advance), 0.)) for s, sign in [('R', 1), ('L', -1)]}
    ankles = {s: np.array((sign*.105, sign*.08, .085)) for s, sign in [('R', 1), ('L', -1)]}
    reach = FEMUR+TIBIA-.0015
    limits = [a[2]+math.sqrt(reach*reach-float(np.dot(a[:2]-hips[s][:2], a[:2]-hips[s][:2]))) for s, a in ankles.items()]
    hip_z = min(1.032-float(loading), *limits)
    pelvis = np.array((0., float(advance), hip_z))
    bones = {}; feet = {}
    for s, sign in [('R', 1), ('L', -1)]:
        hip = hips[s]+[0, 0, hip_z]; ankle = ankles[s]; knee = ik(hip, ankle)
        heel, sole, toe = [shared.foot_point(ankle, 0., x) for x in [shared.HEEL, 0., shared.TOE]]
        feet[s] = {'hip': hip, 'knee': knee, 'ankle': ankle, 'heel': heel, 'sole': sole, 'toe': toe,
                   'pitch': 0., 'stance': True, 'contactKind': 'sole'}
        bones[s+'-femur'], bones[s+'-tibia'], bones[s+'-foot'] = (hip, knee), (knee, ankle), (ankle, ankle+[0, FOOT_LENGTH, 0])
        shoulder = pelvis+[sign*.205, .018, .48]
        hand = pelvis+(right if s == 'R' else left)
        elbow = ik(shoulder, hand, .25, .24, pole=(0., -1., 0.))
        bones[s+'-upperarm'], bones[s+'-forearm'] = (shoulder, elbow), (elbow, hand)
    return {'phase': phase, 'root': np.zeros(3), 'pelvis': pelvis, 'feet': feet,
            'bones': bones, 'bladeVector': blade, 'neutralBladeVector': np.asarray(ATTACK[0][-1])}
