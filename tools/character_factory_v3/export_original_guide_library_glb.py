"""Export an existing verified tall-guide Blend to a new GLB, read-only inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    import bpy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    manifest = json.loads((args.library/'manifest.json').read_text())
    blend = args.library/'original-guide-actions.blend'
    glb = args.library/'original-guide-actions.glb'
    if glb.exists() or glb.with_suffix('.export.json').exists():
        raise ValueError('Preserve earlier exports')
    digest = hashlib.sha256(blend.read_bytes()).hexdigest()
    if digest != manifest['outputs'][blend.name]:
        raise ValueError('Verified Blend changed')
    bpy.ops.wm.open_mainfile(filepath=str(blend.resolve()))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(glb.resolve()), export_format='GLB',
                              use_selection=True, export_animations=True,
                              export_animation_mode='ACTIONS', export_cameras=True,
                              export_extras=True, export_def_bones=False,
                              export_all_influences=True, export_optimize_animation_size=False)
    if hashlib.sha256(blend.read_bytes()).hexdigest() != digest:
        raise ValueError('Original Blend changed during export')
    receipt = {'source_blend_sha256': digest,
               'output_sha256': hashlib.sha256(glb.read_bytes()).hexdigest(),
               'export_optimize_animation_size': False,
               'status': 'GLB_EXPORT_REQUIRES_POSE_ROUNDTRIP',
               'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    glb.with_suffix('.export.json').write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    main()
