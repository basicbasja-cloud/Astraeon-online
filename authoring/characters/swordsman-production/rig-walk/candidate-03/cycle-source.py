"""Authoring-only articulated gait. No runtime code or painted pixels.

Coordinates: +Y anatomical forward, +X anatomical right, +Z up, metres.
The root is the fixed origin in sprite space. Adding unwrapped phase times
cycleDistance to Y gives the corresponding travelling actor in world space.
Ankle rotation moves a rigid heel/sole/toe assembly, never scales a foot.
"""
import math
import numpy as np

DIRECTIONS = ('S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE')
FEMUR = .49
TIBIA = .47
FOOT_LENGTH = .28
HEEL = -.09
TOE = .19
ANKLE_HEIGHT = .085
DUTY = .60
STANCE_TRAVEL = .58
FOOT_TRACK_OFFSET = -.06
CYCLE_DISTANCE = STANCE_TRAVEL / DUTY
CYCLE_SECONDS = 1.12
PHASE_NAMES = ('R contact', 'R down / L lift', 'R passing', 'R up / L reach',
               'L contact', 'L down / R lift', 'L passing', 'L up / R reach')


def smooth(x):
    x = max(0., min(1., x))
    return x*x*(3-2*x)


def ik(hip, ankle, upper=FEMUR, lower=TIBIA, pole=(0., 1., 0.)):
    """Analytic two-bone IK, fixed lengths, anatomical forward knee pole."""
    hip, ankle = np.asarray(hip, float), np.asarray(ankle, float)
    delta = ankle-hip
    distance = float(np.linalg.norm(delta))
    if not abs(upper-lower) < distance < upper+lower:
        raise ValueError(('Unreachable ankle; never stretch the chain', distance))
    axis = delta/distance
    bend = np.asarray(pole, float)
    bend -= axis*np.dot(bend, axis)
    bend /= np.linalg.norm(bend)
    along = (upper*upper-lower*lower+distance*distance)/(2*distance)
    return hip+axis*along+bend*math.sqrt(max(0., upper*upper-along*along))


def foot_point(ankle, pitch, longitudinal):
    """Rigid sole point around ankle; heel/toe offsets share one foot frame."""
    c, s = math.cos(pitch), math.sin(pitch)
    return np.asarray(ankle)+np.array((0., longitudinal*c+ANKLE_HEIGHT*s,
                                      longitudinal*s-ANKLE_HEIGHT*c))


def foot(phase, side):
    offset = 0. if side == 'R' else .5
    q = (phase+offset) % 1.
    stance = q < DUTY
    if stance:
        pitch = .14*(1-smooth(q/.08)) if q < .08 else (
            -.26*smooth((q-.36)/(.60-.36)) if q > .36 else 0.)
        pivot = HEEL if pitch > 0. else TOE if pitch < 0. else 0.
        # The pivot in virtual world space is invariant within a contact
        # interval. When flat, both heel and toe are planted simultaneously.
        y = STANCE_TRAVEL/2+FOOT_TRACK_OFFSET-CYCLE_DISTANCE*q+pivot-(pivot*math.cos(pitch)+ANKLE_HEIGHT*math.sin(pitch))
        z = ANKLE_HEIGHT*math.cos(pitch)-pivot*math.sin(pitch)
        clearance = 0.
    else:
        u = (q-DUTY)/(1-DUTY)
        # Finish push-off with plantar flexion before dorsiflexing for heel
        # contact. Returning directly from toe-off to heel pitch left the
        # extended rear ankle too low, forcing the loaded leg into a crouch.
        pitch = -.26-.12*smooth(u/.12) if u < .12 else -.38+.52*smooth((u-.12)/.88)
        def endpoint(q0, angle, p):
            return STANCE_TRAVEL/2+FOOT_TRACK_OFFSET-CYCLE_DISTANCE*q0+p-(p*math.cos(angle)+ANKLE_HEIGHT*math.sin(angle))
        back, front = endpoint(DUTY, -.26, TOE), endpoint(0., .14, HEEL)
        # Hermite endpoint velocity matches stance (-cycleDistance), rather
        # than freezing the ankle at toe-off and snapping it into swing.
        tangent = -CYCLE_DISTANCE*(1-DUTY)
        y = back+(front-back)*smooth(u)+tangent*u*(1-u)*(1-2*u)
        clearance = .065*math.sin(math.pi*u)**2
        z = -min(HEEL*math.sin(pitch)-ANKLE_HEIGHT*math.cos(pitch),
                 TOE*math.sin(pitch)-ANKLE_HEIGHT*math.cos(pitch))+clearance
        pivot = None
    ankle = np.array((.105 if side == 'R' else -.105, y, z))
    points = {name: foot_point(ankle, pitch, value) for name, value in
              [('heel', HEEL), ('sole', 0.), ('toe', TOE)]}
    return {'phase': q, 'stance': stance, 'pitch': pitch, 'ankle': ankle,
            **points, 'clearance': clearance,
            'contactKind': 'swing' if not stance else 'heel' if pitch > 0 else 'toe' if pitch < 0 else 'sole',
            'contactPivot': pivot}


def pose(phase):
    phase %= 1.
    feet = {side: foot(phase, side) for side in ('R', 'L')}
    sway = .028*math.sin(math.tau*phase)
    pelvis_yaw = .045*math.sin(math.tau*phase)
    shoulder_yaw = -.04*math.sin(math.tau*phase)
    hips = {side: np.array((sway+sign*.105*math.cos(pelvis_yaw),
                           sign*.105*math.sin(pelvis_yaw), 0.))
            for side, sign in [('R', 1), ('L', -1)]}
    # Follow the supporting-leg arc. Reach constraints include every ankle;
    # there is no stretch and no negative knee solution at crossover.
    limits = []
    for side, f in feet.items():
        delta_xy = f['ankle'][:2]-hips[side][:2]
        reach = FEMUR+TIBIA-.0015
        limits.append(f['ankle'][2]+math.sqrt(reach*reach-float(np.dot(delta_xy, delta_xy))))
    load_phase = (phase-.105+.25) % .5-.25
    hip_z = min(limits)-.006*math.exp(-(load_phase/.055)**2)
    pelvis = np.array((sway, 0., hip_z))
    chest = pelvis+np.array((0., .018, .48))
    neck = pelvis+np.array((0., .024, .60))
    head = pelvis+np.array((0., .024, .78))
    bones = {'pelvis': (pelvis-np.array((.105, 0., 0.)), pelvis+np.array((.105, 0., 0.))),
             'spine': (pelvis, chest), 'neck': (chest, neck), 'head': (neck, head)}
    for side, sign in [('R', 1), ('L', -1)]:
        f = feet[side]
        hip = hips[side]+np.array((0., 0., hip_z))
        knee = ik(hip, f['ankle'])
        f['hip'], f['knee'] = hip, knee
        f['thighForwardDegrees'] = math.degrees(math.atan2(knee[1]-hip[1], hip[2]-knee[2]))
        a, b = (hip-knee)/FEMUR, (f['ankle']-knee)/TIBIA
        f['kneeFlexDegrees'] = math.degrees(math.acos(float(np.clip(-np.dot(a, b), -1, 1))))
        f['poleDot'] = float(np.dot(knee-(hip+(f['ankle']-hip)*FEMUR/(FEMUR+TIBIA)), (0., 1., 0.)))
        bones[side+'-femur'] = (hip, knee)
        bones[side+'-tibia'] = (knee, f['ankle'])
        bones[side+'-foot'] = (f['ankle'], f['ankle']+np.array((0., FOOT_LENGTH*math.cos(f['pitch']), FOOT_LENGTH*math.sin(f['pitch']))))
        shoulder = np.array((sway+sign*.205*math.cos(shoulder_yaw),
                             .018+sign*.205*math.sin(shoulder_yaw), hip_z+.48))
        hand = np.array((sway+sign*.235, -.10*sign*math.cos(math.tau*phase), hip_z+.015))
        elbow = ik(shoulder, hand, .25, .24)
        bones[side+'-upperarm'] = (shoulder, elbow)
        bones[side+'-forearm'] = (elbow, hand)
    # Contact transfer is metadata for diagnosis, not inferred gameplay force.
    q = phase % .5
    if q < DUTY-.5:
        leading = 'R' if phase < .5 else 'L'
        lead_weight = smooth(q/(DUTY-.5))
        weights = {leading: lead_weight, ('L' if leading == 'R' else 'R'): 1-lead_weight}
    else:
        weights = {'R': float(phase < .5), 'L': float(phase >= .5)}
    return {'phase': phase, 'root': np.array((0., 0., 0.)), 'pelvis': pelvis,
            'chest': chest, 'head': head, 'bones': bones, 'feet': feet,
            'supportWeights': weights}


def serializable(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, dict): return {k: serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [serializable(v) for v in value]
    return value
