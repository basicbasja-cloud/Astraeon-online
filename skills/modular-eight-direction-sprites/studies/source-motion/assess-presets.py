"""Audit a fresh proportion-only skeleton from real transforms; expose contact gaps.

The two-segment result is a diagnostic, NOT an applied/baked rig or contact cleanup.
"""
import argparse, gzip, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from retarget_math import fk, two_segment

p = argparse.ArgumentParser(); p.add_argument('--input', type=Path, required=True)
p.add_argument('--output', type=Path, required=True); a = p.parse_args()
if a.output.exists(): raise ValueError('Output must be new')
source = json.loads(gzip.decompress(a.input.read_bytes()))
rest = source['rest_bones']; object_world = source['object_world_matrix']
def edge_scale(name):
    if name in ['root', 'pelvis']: return .64
    if name.startswith(('spine_',)): return .80
    if name.startswith(('neck_', 'Head')): return 1.15
    if name.startswith(('clavicle_', 'upperarm_', 'thigh_')): return .85
    if name.startswith(('lowerarm_', 'hand_')): return .72
    if name.startswith(('calf_', 'foot_', 'ball_')): return .64
    return .85  # authored finger offsets
factors = {n: edge_scale(n) for n in rest}; identity = {n: 1.0 for n in rest}
target_rest = fk(rest, {n: v['local_matrix'] for n, v in rest.items()}, factors, object_world)
lengths = {n: float(np.linalg.norm(target_rest[n][:3, 3] - target_rest[v['parent']][:3, 3]))
           for n, v in rest.items() if v['parent']}
chains = [('right.arm', ['upperarm_r', 'lowerarm_r', 'hand_r']),
          ('left.arm', ['upperarm_l', 'lowerarm_l', 'hand_l']),
          ('right.leg', ['thigh_r', 'calf_r', 'foot_r']),
          ('left.leg', ['thigh_l', 'calf_l', 'foot_l'])]
def project(v, root, view=1, size=192):
    x, y, z = np.asarray(v) - np.asarray(root); theta = view * math.pi / 4
    rx, ry = x * math.cos(theta) - y * math.sin(theta), x * math.sin(theta) + y * math.cos(theta)
    return (size / 2 + rx * size * .48, size * .93 + ry * size * .24 - z * size * .48 * math.cos(math.pi / 6))
def diagram(j, root, view=1, goals=None, size=192, endpoint_only=False):
    im = Image.new('RGB', (size, size), '#26303b'); d = ImageDraw.Draw(im)
    pts = {n: project(v, root, view, size) for n, v in j.items()}
    for n, entry in rest.items():
        parent = entry['parent']
        if endpoint_only and (name_is_distal(n) or name_is_distal(parent)): continue
        if parent and parent != 'root':
            col = '#4ba0ff' if n.endswith('_r') else '#ff9740' if n.endswith('_l') else '#eceef2'
            d.line([pts[parent], pts[n]], fill=col, width=2 if size == 192 else 1)
    if goals:
        for name, v in goals.items():
            x, y = project(v, root, view, size); d.ellipse((x-3,y-3,x+3,y+3), outline='#ff6575')
    return im
def name_is_distal(name):
    return bool(name and name.startswith(('thumb_', 'index_', 'middle_', 'ring_', 'pinky_', 'ball_')))

clips = []; identity_error = 0; length_error = 0
for clip in source['clips']:
    frames = []; records = {name: [] for name, _ in chains}
    for f in clip['frames']:
        reconstructed = fk(rest, f['local_matrices'], identity, object_world)
        source_j = {n: np.asarray(v) for n, v in f['world_joints'].items()}
        identity_error = max(identity_error, max(float(np.linalg.norm(reconstructed[n][:3,3] - source_j[n])) for n in rest))
        target = fk(rest, f['local_matrices'], factors, object_world)
        j = {n: m[:3, 3] for n, m in target.items()}; diagnostic = dict(j); goals = {}; results = {}
        for n, v in rest.items():
            if v['parent'] and n != 'pelvis':
                length_error = max(length_error, abs(float(np.linalg.norm(j[n]-j[v['parent']]))-lengths[n]))
        for name, chain in chains:
            base, mid, end = chain; anchor = 'spine_03' if '.arm' in name else 'root'
            goal_scale = .80 if '.arm' in name else .64
            goal = j[anchor] + (source_j[end] - source_j[anchor]) * goal_scale
            pole = j[base] + (source_j[mid] - source_j[base]) * goal_scale
            solved = two_segment(j[base], pole, goal, lengths[mid], lengths[end])
            goals[end] = goal; diagnostic[mid] = solved['middle']; diagnostic[end] = solved['end']
            r = {'before_error': float(np.linalg.norm(j[end]-goal)), 'after_error': solved['residual'],
                 'reachable': solved['reachable'], 'goal_world': goal.tolist(),
                 'middle_world': solved['middle'].tolist(), 'end_world': solved['end'].tolist()}
            records[name].append(r); results[name] = r
        frames.append({'source_index': f['source_index'], 'time_seconds': f['time_seconds'],
                       'duration_seconds': f['duration_seconds'], 'source_joints': f['world_joints'],
                       'target_fk_joints': {n: v.tolist() for n,v in j.items()}, 'diagnostic_chains': results})
    summary = {}
    for name, rs in records.items():
        summary[name] = {'samples': len(rs), 'unreachable': sum(not r['reachable'] for r in rs),
                         'max_before_error': max(r['before_error'] for r in rs),
                         'max_after_error': max(r['after_error'] for r in rs)}
    clips.append({'name': clip['name'], 'duration_seconds': clip['duration_seconds'], 'frames': frames, 'summary': summary})
if identity_error > 2e-5 or length_error > 2e-5:
    raise ValueError(f'FK reconstruction/rigid edge gate failed: {identity_error}, {length_error}')
report = {'schema': 'proportional-preset-diagnostic-v1', 'source_sha256': source['source_sha256'],
          'transform_capture_sha256': hashlib.sha256(a.input.read_bytes()).hexdigest(), 'edge_factors': factors,
          'target_rest_matrices': {n:m.tolist() for n,m in target_rest.items()}, 'rest_parents': {n:v['parent'] for n,v in rest.items()},
          'max_identity_reconstruction_error': identity_error, 'max_rigid_edge_length_error': length_error,
          'rigid_edge_scope': 'All parent-child head offsets except pelvis-to-root. Source pelvis has authored translation (especially roll/jump), retained rather than misclassified as stretched limb.',
          'goals': 'Synthetic per-frame trajectory goals: chest-relative wrist at 0.80, root-relative ankle at 0.64. NOT observed footplants, hilt contacts or sole patches.',
          'diagnostic_solver': 'Two segments, source bend half-plane, fixed lengths, nearest reachable endpoint. Independent chains; not applied to whole target rig, no fingers/surface/temporal correction.',
          'scope': 'Fresh generic proportion-only skeleton; same hierarchy/rest basis. No original character art, Mixamo clip or production retarget. Endpoint samples have no invented hold.',
          'release_ready': False, 'clips': clips}
a.output.mkdir(parents=True)
with (a.output/'proportion-study.json.gz').open('wb') as stream:
    with gzip.GzipFile(fileobj=stream, mode='wb', filename='', mtime=0) as zipped:
        zipped.write(json.dumps(report,separators=(',',':')).encode())
metrics = {k:v for k,v in report.items() if k not in ['clips','target_rest_matrices','rest_parents']}
metrics['clips'] = [{k:v for k,v in c.items() if k != 'frames'} | {'samples':len(c['frames'])} for c in clips]
(a.output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
for c in clips:
    fs=c['frames']; indices=[round(i*(len(fs)-1)/7) for i in range(8)]
    board=Image.new('RGB',(1536,666),'#202630'); d=ImageDraw.Draw(board)
    for col,i in enumerate(indices):
        f=fs[i]; sj=f['source_joints']; tj=f['target_fk_joints']; diagnostic=dict(tj); goals={}
        for name, chain in chains:
            _,mid,end=chain;r=f['diagnostic_chains'][name];diagnostic[mid]=r['middle_world'];diagnostic[end]=r['end_world'];goals[end]=r['goal_world']
        for row,(label,j,g) in enumerate([('source',sj,None),('target FK',tj,goals),('endpoint diagnosis',diagnostic,goals)]):
            x,y=col*192,row*222;board.paste(diagram(j,j['root'],goals=g,endpoint_only=row==2),(x,y+28));d.text((x+3,y+2),f'{label} #{i}\n{f["time_seconds"]:.3f}s',fill='white')
    board.save(a.output/(c['name']+'-comparison.png'))
    for page,start in enumerate(range(0,len(fs),48)):
        subset=fs[start:start+48];b=Image.new('RGB',(1536,math.ceil(len(subset)/6)*152),'#202630');d=ImageDraw.Draw(b)
        for k,f in enumerate(subset):
            x,y=(k%6)*256,(k//6)*152
            for col,key in enumerate(['source_joints','target_fk_joints']):
                j=f[key];b.paste(diagram(j,j['root'],size=128),(x+col*128,y+24))
            d.text((x+2,y+2),f'#{f["source_index"]} {f["time_seconds"]:.3f}s  source / FK',fill='white')
        b.save(a.output/f'{c["name"]}-dense-{page:02}.png')
    if c['name'] in ['Walk_Loop','Sword_Attack']:
        b=Image.new('RGB',(1536,1776),'#202630');d=ImageDraw.Draw(b)
        for view,heading in enumerate(['S','SE','E','NE','N','NW','W','SW']):
            for col,i in enumerate(indices):
                f=fs[i];j=f['target_fk_joints'];x,y=col*192,view*222;b.paste(diagram(j,j['root'],view),(x,y+28));d.text((x+3,y+2),f'{heading} FK #{i}\n{f["time_seconds"]:.3f}s',fill='white')
        b.save(a.output/(c['name']+'-eight-views.png'))
print('FK_GATES',identity_error,length_error)
print('PRESET_STUDY',[(c['name'],len(c['frames']),c['summary']['right.arm']['unreachable']) for c in clips])
