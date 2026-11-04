"""Trace fixed rest-mesh heel/toe vertex sets, not a changing lowest vertex.

This supplies inspectable source features. Painted correspondences, visibility
and intended contact must still be reviewed before measuring contact error.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from audit_swordsman_hit_frozen_feet import indices_by_weight


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import bpy
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
    from PIL import Image, ImageDraw
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.output.exists() or args.output.is_symlink():
        raise ValueError('Fresh output required')
    guide_path = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'
    guide = json.loads(guide_path.read_text()); job = guide['job']
    source = ROOT / job['source_file']
    if sha(source) != job['source_sha256'] or job['source_actions'] != ['Walk']:
        raise ValueError('Native source mismatch')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    rig = max((o for o in bpy.data.objects if o.type == 'ARMATURE'), key=lambda o: len(o.data.bones))
    if rig.parent is not None:
        raise ValueError('Unexpected rig parent')
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    action = bpy.data.actions.get('Walk_' + rig.name)
    if action is None:
        raise ValueError('Missing native Walk')
    rig.animation_data.action = action
    if hasattr(rig.animation_data, 'action_slot') and action.slots:
        rig.animation_data.action_slot = action.slots[0]
    rig.matrix_world = Matrix.Identity(4)
    mesh = next(o for o in bpy.data.objects if o.type == 'MESH' and o.parent == rig)
    selections = {}
    for side in ('l', 'r'):
        ids = indices_by_weight(mesh, side)
        rest = {i: mesh.matrix_world @ mesh.data.vertices[i].co for i in ids}
        foot = rig.matrix_world @ rig.data.bones['foot_' + side].head_local
        ball = rig.matrix_world @ rig.data.bones['ball_' + side].head_local
        forward = ball - foot; forward.z = 0; forward.normalize()
        lowest = min(p.z for p in rest.values())
        sole = [i for i, p in rest.items() if p.z <= lowest + .004]
        position = {i: (rest[i] - foot).dot(forward) for i in sole}
        back, front = min(position.values()), max(position.values())
        if front - back < .05:
            raise ValueError('Sole geometry cannot distinguish heel/toe')
        selections[side] = {'heel': [i for i in sole if position[i] <= back + .2 * (front-back)],
                            'toe': [i for i in sole if position[i] >= front - .2 * (front-back)],
                            'rest_sole_min_z': lowest, 'rest_axis_forward': list(forward)}
    scene = bpy.context.scene; camera_spec = guide['views']['SW']['camera']
    scene.render.resolution_x = scene.render.resolution_y = 1536
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new('FrozenGuideCamera'); cam = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(cam); scene.camera = cam; data.type = 'ORTHO'
    data.ortho_scale = camera_spec['ortho_scale']; cam.location = camera_spec['location']; cam.rotation_euler = camera_spec['rotation']
    args.output.mkdir(parents=True); rows = []
    for frame in guide['views']['SW']['frames']:
        t = frame['source_frame']; scene.frame_set(math.floor(t), subframe=t % 1)
        rig.matrix_world = Matrix.Identity(4); bpy.context.view_layer.update()
        for name in ('head', 'foot_l', 'foot_r'):
            actual = rig.matrix_world @ rig.pose.bones[name].head
            if (actual - Vector(frame['world_landmarks'][name])).length > 1e-4:
                raise ValueError('Source pose changed at ' + str(frame['frame']))
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()); geometry = evaluated.to_mesh()
        features = {}
        try:
            if len(geometry.vertices) != len(mesh.data.vertices):
                raise ValueError('Topology changed')
            for side in ('l', 'r'):
                features[side] = {}
                for role in ('heel', 'toe'):
                    ids = selections[side][role]
                    point = sum((evaluated.matrix_world @ geometry.vertices[i].co for i in ids), Vector()) / len(ids)
                    q = world_to_camera_view(scene, cam, point)
                    features[side][role] = {'vertex_indices': ids, 'world_xyz': list(point),
                                             'source_guide_xy': [q.x * 1536, (1-q.y) * 1536]}
        finally:
            evaluated.to_mesh_clear()
        rows.append({'frame': frame['frame'], 'source_frame': t, 'features': features})
        # Same coordinate system as the paintings: authoring is half the guide.
        native = Image.open(guide_path.parent / 'SW' / f"{frame['frame']:03}.png").convert('RGBA').resize((768, 768))
        background = Image.new('RGBA', native.size, '#ccc'); background.alpha_composite(native)
        draw = ImageDraw.Draw(background)
        for side, color in (('l', '#0075ff'), ('r', '#ff7400')):
            for role in ('heel', 'toe'):
                x, y = [v / 2 for v in features[side][role]['source_guide_xy']]
                draw.ellipse((x-3, y-3, x+3, y+3), outline=color, width=2)
                draw.text((x+4, y-10), side + ':' + role, fill=color)
        background.crop((270, 430, 485, 600)).resize((645, 510)).convert('RGB').save(args.output / f"feet{frame['frame']:02}.png")
    result = {'status': 'FIXED_SOURCE_FEATURES_NOT_PAINTED_CONTACT_APPROVAL', 'guide_sha256': sha(guide_path),
              'source_sha256': sha(source), 'script_sha256': sha(Path(__file__)), 'selection': selections, 'frames': rows,
              'limitations': ['Rest-mesh bottom bands and heel/toe axis selections require visual anatomical review.',
                             'Fixed sets eliminate changing-vertex identity; their averages are not proven painted boot features.',
                             'Occlusion, costume shape, planted phases, gameplay velocity and painted correspondences are not inferred.',
                             'No source-relative one-pixel contact pass or action acceptance is claimed.']}
    (args.output / 'trace.json').write_text(json.dumps(result, indent=2) + '\n')
    print('FIXED_SOLE_FEATURES', len(rows), selections, flush=True)


if __name__ == '__main__':
    main()
