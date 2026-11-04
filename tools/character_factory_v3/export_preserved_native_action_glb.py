"""Export the sampled rig library without optimizing away small native motion."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    import bpy
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh GLB export')
    manifest=json.loads((a.library/'manifest.json').read_text())
    blend=a.library/'sampled-native-actions.blend'
    if sha(blend)!=manifest['outputs'][blend.name]:raise ValueError('Source action library changed')
    bpy.ops.wm.open_mainfile(filepath=str(blend.resolve()))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(a.output.resolve()),export_format='GLB',use_selection=True,
                              export_animations=True,export_animation_mode='ACTIONS',
                              export_cameras=True,export_extras=True,export_def_bones=False,
                              export_all_influences=True,export_optimize_animation_size=False)
    result={'status':'KEY_PRESERVING_GLB_EXPORT_REQUIRES_ROUNDTRIP',
            'source_blend_sha256':sha(blend),'output_sha256':sha(a.output),
            'export_optimize_animation_size':False,'implementation_sha256':sha(__file__),
            'reason':'Retain small source motion that default animation optimization may discard.'}
    a.output.with_suffix('.export.json').write_text(json.dumps(result,indent=2)+'\n')
    print('KEY_PRESERVING_GLB_EXPORTED',sha(a.output),flush=True)


if __name__=='__main__':main()
