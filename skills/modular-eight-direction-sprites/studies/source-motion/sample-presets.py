"""Blender: real source timestamps/local bone transforms for a bounded CC0 preset study.

Same-rest-basis FK experiment only. No Mixamo account, inferred mocap or original art.
"""
import argparse, gzip, hashlib, json, math, struct, sys
from pathlib import Path
import bpy

PRESETS = ['Idle_Loop', 'Walk_Loop', 'Jog_Fwd_Loop', 'Sprint_Loop',
           'Jump_Start', 'Jump_Land', 'Roll', 'Sword_Attack']
p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
if a.output.exists(): raise ValueError('Use a new isolated output directory')
blob = a.source.read_bytes()
if hashlib.sha256(blob).hexdigest() != 'be684571ed655a1b892c2c07e6e2aeca053b606c442d34004adaf1d944090d01':
    raise ValueError('This bounded adapter requires the audited author Standard RM source')
size = struct.unpack_from('<I', blob, 12)[0]
gltf = json.loads(blob[20:20 + size]); base = 20 + size
n = struct.unpack_from('<I', blob, base)[0]; binary = blob[base + 8:base + 8 + n]
def times(animation):
    values = set()
    for sampler in animation['samplers']:
        ac = gltf['accessors'][sampler['input']]; view = gltf['bufferViews'][ac['bufferView']]
        if ac['componentType'] != 5126 or ac['type'] != 'SCALAR' or view.get('byteStride') or ac.get('sparse'):
            raise ValueError('Unsupported timestamp accessor')
        start = view.get('byteOffset', 0) + ac.get('byteOffset', 0)
        values.update(struct.unpack_from('<' + 'f' * ac['count'], binary, start))
    result = sorted(values)
    if not result or not all(math.isfinite(t) for t in result): raise ValueError('Invalid source times')
    return result
def matrix(m): return [list(row) for row in m]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; scene.render.fps = 30; scene.render.fps_base = 1
bpy.ops.import_scene.gltf(filepath=str(a.source))
rigs = [o for o in scene.objects if o.type == 'ARMATURE']
if len(rigs) != 1: raise ValueError('Adapter requires exactly one source armature')
rig = rigs[0]
for track in rig.animation_data.nla_tracks: track.mute = True
order = sorted(rig.data.bones, key=lambda b: len(b.parent_recursive))
rest = {}
for b in order:
    local = b.parent.matrix_local.inverted() @ b.matrix_local if b.parent else b.matrix_local
    rest[b.name] = {'parent': b.parent.name if b.parent else None,
                    'local_matrix': matrix(local), 'armature_matrix': matrix(b.matrix_local)}
clips = []
for wanted in PRESETS:
    animation = next(x for x in gltf['animations'] if x['name'] == wanted)
    ts = times(animation); action = bpy.data.actions.get(wanted + '_Armature')
    if action is None or abs(action.frame_range[1] - ts[-1] * 30) > .001:
        raise ValueError('Imported action/time mismatch: ' + wanted)
    rig.animation_data.action = action; frames = []
    for i, t in enumerate(ts):
        f = t * 30; scene.frame_set(math.floor(f), subframe=f - math.floor(f)); bpy.context.view_layer.update()
        local, world = {}, {}
        for b in order:
            pb = rig.pose.bones[b.name]
            local[b.name] = matrix(pb.parent.matrix.inverted() @ pb.matrix if pb.parent else pb.matrix)
            world[b.name] = list(rig.matrix_world @ pb.head)
        frames.append({'source_index': i, 'time_seconds': t,
                       'duration_seconds': ts[i + 1] - t if i + 1 < len(ts) else None,
                       'local_matrices': local, 'world_joints': world})
    clips.append({'name': wanted, 'frames': frames, 'duration_seconds': ts[-1] - ts[0]})
report = {'schema': 'preset-local-transform-study-v1', 'source_sha256': hashlib.sha256(blob).hexdigest(),
          'blender': bpy.app.version_string, 'fps_before_import': 30,
          'object_world_matrix': matrix(rig.matrix_world), 'rest_bones': rest,
          'clips': clips, 'all_available_presets': [x['name'] for x in gltf['animations']],
          'scope': 'Actual evaluated transforms; same topology/rest roll only, no production acceptance'}
a.output.mkdir(parents=True)
with (a.output / 'source-transforms.json.gz').open('wb') as stream:
    with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0, filename='') as zipped:
        zipped.write(json.dumps(report, separators=(',', ':')).encode())
print('PRESETS_SAMPLED', [(x['name'], len(x['frames']), x['duration_seconds']) for x in clips])
