"""Export evaluated native skeletons for a new canonical-rig retarget pilot.

Run with the original Blender 4.3 runtime. This does not produce or certify a
new image capture. Existing camera/world landmarks are checked before export.
The canonical renderer and all source files remain unchanged.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument(source):
    class Visitor(ast.NodeTransformer):
        def visit_Assign(self, node):
            if any(isinstance(t, ast.Name) and t.id == 'bones' for t in node.targets):
                return [ast.parse('_record_skeleton(rig, original, rec, direction, i)').body[0], node]
            return self.generic_visit(node)

        def visit_Call(self, node):
            expression = ast.unparse(node.func)
            if expression == 'bpy.ops.render.render':
                return ast.copy_location(ast.Constant(None), node)
            if expression == 'Image.open' and len(node.args) == 1 and ast.unparse(node.args[0]) == 'path':
                node.args[0] = ast.parse('_existing_image(direction, i)', mode='eval').body
            return self.generic_visit(node)

    tree = ast.parse(source)
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__')]
    return ast.fix_missing_locations(Visitor().visit(tree))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-guide', type=Path, required=True)
    parser.add_argument('--direction', default='NE')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    import bpy
    source = args.source_guide.resolve()
    manifest = json.loads((source / 'manifest.json').read_text())
    job = manifest['job']
    renderer = Path(__file__).with_name('render_patch001_guides.py')
    if sha(renderer) != job['renderer_sha256']:
        raise ValueError('Source renderer digest differs')
    if bpy.app.version[:2] != (4, 3):
        raise ValueError('Replay source skeletons with Blender 4.3')
    if args.output.exists():
        raise ValueError('Use a new skeleton export destination')
    expected = manifest['views'][args.direction]['frames']
    rest = {}
    records = []

    def record(rig, original, sample, direction, index):
        if not rest:
            rest.update({bone.name: {'parent': bone.parent.name if bone.parent else None,
                         'world_matrix': [list(row) for row in original @ bone.matrix_local]}
                         for bone in rig.data.bones})
        row = expected[index]
        if (row['action'], row['source_frame']) != (sample['action'], sample['source_frame']):
            raise ValueError('Native source sample differs')
        names = {'root': 'root', 'head': 'head', 'pelvis': 'pelvis',
                 'hand_r': 'hand_r', 'hand_l': 'hand_l', 'foot_r': 'foot_r', 'foot_l': 'foot_l'}
        error = max(abs(float((rig.matrix_world @ rig.pose.bones[bone].head)[axis]) - row['world_landmarks'][key][axis])
                    for key, bone in names.items() for axis in range(3))
        if error > 2e-6:
            raise ValueError('Evaluated source world landmarks differ: ' + str(error))
        records.append({'index': index, 'action': row['action'], 'source_frame': row['source_frame'],
                        'maximum_world_landmark_error_m': error,
                        'bones': {bone.name: {'world_matrix': [list(v) for v in rig.matrix_world @ bone.matrix],
                                             'head': list(rig.matrix_world @ bone.head),
                                             'tail': list(rig.matrix_world @ bone.tail)}
                                  for bone in rig.pose.bones}})

    scope = {'__name__': 'skeleton_metadata_export', '__file__': str(renderer),
             '_record_skeleton': record,
             '_existing_image': lambda direction, index: source / direction / f'{index:03d}.png'}
    exec(compile(instrument(renderer.read_text()), str(renderer), 'exec'), scope)
    with tempfile.TemporaryDirectory(prefix='astraeon-skeleton-export-') as scratch:
        directory = Path(scratch)
        temporary_job = {**job, 'directions': [args.direction]}
        (directory / 'job.json').write_text(json.dumps(temporary_job))
        sys.argv = [sys.argv[0], '--', '--job', str(directory / 'job.json'), '--output', str(directory)]
        scope['main']()
    if len(records) != len(expected):
        raise ValueError('Incomplete native skeleton export')
    receipt = {'status': 'EVALUATED_SOURCE_SKELETON_METADATA_NOT_NEW_IMAGE_CAPTURE',
               'source_job': job['id'], 'source_manifest_sha256': sha(source / 'manifest.json'),
               'source_file': job['source_file'], 'source_sha256': job['source_sha256'],
               'source_renderer_sha256': sha(renderer), 'implementation_sha256': sha(__file__),
               'blender': bpy.app.version_string, 'rest_bones': rest, 'frames': records,
               'source_files_modified': False, 'runtime_admitted': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print('SKELETON_EXPORT', len(records), len(rest), flush=True)


if __name__ == '__main__':
    main()
