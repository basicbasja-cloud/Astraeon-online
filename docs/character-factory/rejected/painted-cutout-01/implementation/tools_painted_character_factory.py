"""Offline painted-part rig contracts and canonical motion sampling.

This module does not paint, cut pixels, generate missing directions or approve art.
Independent image attachments are registered once; every pose uses the same source.
Blender performs the bake. ASTRAEON's existing packer remains the runtime adapter.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
HEADINGS = {name: -i * math.pi / 4 for i, name in enumerate(DIRECTIONS)}
SLOTS = ['BackAccessory', 'BaseBody', 'Outfit', 'Hair', 'Weapon', 'BodyHands', 'Hands', 'Headgear']
PARENTS = {'torso': None, 'head': 'torso', 'upper_R': 'torso', 'fore_R': 'upper_R',
           'hand_R': 'fore_R', 'weapon': 'hand_R', 'upper_L': 'torso',
           'fore_L': 'upper_L', 'hand_L': 'fore_L', 'thigh_R': 'torso',
           'shin_R': 'thigh_R', 'thigh_L': 'torso', 'shin_L': 'thigh_L'}


def read_spec(path):
    path = Path(path).resolve()
    spec = json.loads(path.read_text(encoding='utf-8'))
    validate_spec(spec, path.parent)
    return spec


def validate_spec(spec, folder):
    if spec.get('schemaVersion') != 1 or spec.get('directions') != DIRECTIONS:
        raise ValueError('Expected painted factory v1 and canonical eight-direction order')
    if spec.get('registration') != {'canvas': [320, 320], 'root': [160, 264], 'referenceHeight': 176}:
        raise ValueError('Registration must preserve the audited ASTRAEON contract')
    if spec.get('mirroring') != 'none':
        raise ValueError('Mirroring is forbidden')
    if spec.get('status') != 'DEV_ONLY':
        raise ValueError('This pilot cannot grant production approval')
    for name, source in spec['images'].items():
        file = (folder / source['file']).resolve()
        if not file.is_relative_to(folder.resolve()):
            raise ValueError('Source must stay inside the source package')
        if hashlib.sha256(file.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'Source hash changed: {name}')
    for direction, view in spec['views'].items():
        if direction not in DIRECTIONS or not view.get('attachments'):
            raise ValueError('Every provided view needs independent named attachments')
        ids = set()
        for attachment in view['attachments']:
            if attachment['id'] in ids:
                raise ValueError('Duplicate attachment ID')
            ids.add(attachment['id'])
            if attachment['image'] not in spec['images'] or attachment['bone'] not in PARENTS:
                raise ValueError('Unknown attachment source or bone')
            if attachment['slot'] not in SLOTS or attachment['scale'] <= 0:
                raise ValueError('Invalid slot or fixed attachment scale')
            x, y, w, h = attachment['rect']
            iw, ih = spec['images'][attachment['image']]['size']
            if min(x, y) < 0 or min(w, h) <= 0 or x+w > iw or y+h > ih:
                raise ValueError('Attachment rectangle outside source')
            if math.dist(attachment['pivot'], attachment['axisEnd']) < 1:
                raise ValueError('Attachment needs a real local orientation axis')
    for action, clip in spec['motions'].items():
        if action not in ('Idle', 'Walk', 'BasicAttack') or clip.get('state') != 'AUTHORED_PILOT':
            raise ValueError('Unknown or unauthored pilot motion')
        if len(clip['durations']) < 2 or any(not isinstance(t, int) or t <= 0 for t in clip['durations']):
            raise ValueError('Invalid motion timing')


def require_coverage(spec, directions, actions, release=False):
    missing = [d for d in directions if d not in spec['views']]
    if missing:
        raise ValueError('Missing independent directional art: ' + ', '.join(missing))
    missing = [a for a in actions if a not in spec['motions']]
    if missing:
        raise ValueError('Missing authored motion: ' + ', '.join(missing))
    if release:
        if directions != DIRECTIONS:
            raise ValueError('Release requires every true direction')
        if any(spec['views'][d].get('ownerApproval') != 'APPROVED' for d in directions):
            raise ValueError('Owner visual approval is missing; release refused')
        raise ValueError('Complete character/equipment gates are not yet satisfied; release refused')


def project(point, direction):
    """Exact named heading, fixed orthographic camera at 30 degrees elevation.

    Body coordinates: x = anatomical left, y = rear, z = up. Body forward is -y.
    Every heading rotates the same pose; source attachments are direction-specific.
    """
    theta = HEADINGS[direction]
    x, y, z = point
    x, y = x*math.cos(theta)-y*math.sin(theta), x*math.sin(theta)+y*math.cos(theta)
    return [160 + x*50.8, 264 - (z*math.cos(math.pi/6) + y*math.sin(math.pi/6))*50.8]


def canonical_pose(spec, action, index):
    """Shared body-space keyframes; equipment geometry never selects the pose."""
    clip = spec['motions'][action]
    count = len(clip['durations'])
    if not 0 <= index < count:
        raise ValueError('Frame index outside authored clip')
    p = {k: list(v) for k, v in spec['bodyJoints'].items()}
    phase = math.tau * index/count
    if action == 'Idle':
        bob = 0.012 * math.sin(phase)
        for k in p:
            if k not in ('root', 'knee_R', 'sole_R', 'knee_L', 'sole_L'):
                p[k][2] += bob
    elif action == 'Walk':
        # In-place body motion for a translating actor: support foot travels
        # backward through stance; swing foot advances and rises smoothly.
        for side, offset in [('R', 0.0), ('L', 0.5)]:
            t = (index/count + offset) % 1
            if t < 0.6:
                travel = -0.24 + 0.48*t/0.6
                lift = 0
            else:
                u = (t-0.6)/0.4
                travel = 0.24 - 0.48*(u*u*(3-2*u))
                lift = 0.10*math.sin(math.pi*u)
            p['sole_'+side][1] += travel
            p['sole_'+side][2] += lift
            p['knee_'+side][1] += travel*0.45 - 0.06*math.sin(math.pi*t)
            p['knee_'+side][2] += lift*0.5
        bob = 0.018*math.cos(phase*2)
        for k in p:
            if k not in ('root', 'knee_R', 'sole_R', 'knee_L', 'sole_L'):
                p[k][2] += bob
        swing = 0.10*math.sin(phase)
        for k in ('elbow_L', 'wrist_L', 'grip_L'):
            p[k][1] += swing
        for k in ('elbow_R', 'wrist_R', 'grip_R'):
            p[k][1] -= swing*0.35
    elif action == 'BasicAttack':
        # Deliberate authored anticipation -> strike -> recovery. These keys
        # are a motion pilot, never automatically described as approved.
        keys = clip['keys']
        time = sum(clip['durations'][:index])
        a, b = keys[0], keys[-1]
        for left, right in zip(keys, keys[1:]):
            if left['time'] <= time <= right['time']:
                a, b = left, right
                break
        u = max(0, min(1, (time-a['time'])/max(1, b['time']-a['time'])))
        u = u*u*(3-2*u)
        for joint in ('elbow_R', 'wrist_R', 'grip_R'):
            p[joint] = [a[joint][i]*(1-u)+b[joint][i]*u for i in range(3)]
        p['weapon_axis'] = [a['weapon_axis'][i]*(1-u)+b['weapon_axis'][i]*u for i in range(3)]
        # Lift the relaxed offhand out to the body's left, clearing the sword arc.
        clear = math.sin(math.pi*min(1,time/sum(clip['durations'])))**0.7
        for joint,out,forward,up in [('elbow_L',0.18,0.06,0.08),('wrist_L',0.32,0.12,0.18),('grip_L',0.40,0.18,0.22)]:
            p[joint][0] += out*clear
            p[joint][1] -= forward*clear
            p[joint][2] += up*clear
    if 'weapon_axis' not in p:
        p['weapon_axis'] = list(spec['restWeaponAxis'])
    # The hilt location is derived once from the canonical hand contact.
    p['weapon_tip'] = [p['grip_R'][i]+p['weapon_axis'][i] for i in range(3)]
    return p


def sample_pose(spec, direction, action, index):
    p = canonical_pose(spec, action, index)
    j = {name: project(point, direction) for name, point in p.items() if name != 'weapon_axis'}
    bones = {'torso': [j['waist'], j['neck']], 'head': [j['neck'], j['head']],
             'weapon': [j['grip_R'], j['weapon_tip']]}
    for side in ('R', 'L'):
        bones.update({'upper_'+side: [j['shoulder_'+side], j['elbow_'+side]],
                      'fore_'+side: [j['elbow_'+side], j['wrist_'+side]],
                      'hand_'+side: [j['wrist_'+side], j['grip_'+side]],
                      'thigh_'+side: [j['hip_'+side], j['knee_'+side]],
                      'shin_'+side: [j['knee_'+side], j['sole_'+side]]})
    sockets = {'root': [160, 264], 'head': j['head'], 'hand_R': j['grip_R'],
               'hand_L': j['grip_L'], 'back': j['back'], 'waist': j['waist'],
               'weapon': j['grip_R'], 'offhand': j['grip_L'],
               'foot_R': j['sole_R'], 'foot_L': j['sole_L']}
    return {'bones': bones, 'sockets': sockets, 'bodyJoints': p,
            'direction': direction, 'action': action, 'index': index}


def attachment_points(attachment):
    """Raw atlas rectangle -> fixed bone-local card vertices, without pixel edits."""
    x, y, w, h = attachment['rect']
    px, py = attachment['pivot']
    ex, ey = attachment['axisEnd']
    dx, dy = ex-px, ey-py
    length = math.hypot(dx, dy)
    scale = attachment['scale']
    vertices = []
    for sx, sy in [(x, y+h), (x+w, y+h), (x+w, y), (x, y)]:
        vx, vy = sx-px, sy-py
        vertices.append([(-vx*dy+vy*dx)/length*scale,
                         (vx*dx+vy*dy)/length*scale, attachment['depth']])
    return vertices


def variant_enabled(attachment, variant):
    return all(variant.get(key) in value if isinstance(value, list) else variant.get(key) == value
               for key, value in attachment.get('select', {}).items())


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--release-check', action='store_true')
    args = parser.parse_args()
    spec = read_spec(args.spec)
    if args.release_check:
        require_coverage(spec, DIRECTIONS, spec['requiredActions'], release=True)
    print(json.dumps({'status': spec['status'], 'views': list(spec['views']),
                      'motions': list(spec['motions']), 'release': 'NOT_READY'}))


if __name__ == '__main__':
    main()
