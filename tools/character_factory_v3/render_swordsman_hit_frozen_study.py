"""Render an isolated Hit_Chest study with native armature object channels frozen.

This is an opt-in experiment for this source; bone animation remains active. It
must not be used as a generic root-motion policy or overwrite a canonical guide.
"""
import hashlib
import json
import sys
from pathlib import Path

BASE=Path(__file__).with_name('render_patch001_guides.py')
ACTION_MARK="        if source_rig.animation_data.action!=chosen:\n"
ORIGINAL_MARK='    original=rig.matrix_world.copy();records=[]\n'
ACTION_PATCH='''        if job.get('freeze_source_object_transform'):
            if source_rig.parent is not None or adapter is not None:
                raise ValueError('Object transform freeze requires an unparented native source rig')
            for fc in chosen.fcurves:
                if fc.data_path in {'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale'}:
                    fc.mute=True
'''
ORIGINAL_PATCH='''    if job.get('freeze_source_object_transform'):
        rig.matrix_world=Matrix.Identity(4)
        bpy.context.view_layer.update()
    original=rig.matrix_world.copy();records=[]
'''

def patched_source(source):
 if source.count(ACTION_MARK)!=1 or source.count(ORIGINAL_MARK)!=1:
  raise ValueError('Base renderer changed; re-review this study')
 return source.replace(ACTION_MARK,ACTION_PATCH+ACTION_MARK).replace(ORIGINAL_MARK,ORIGINAL_PATCH)

def main():
 args=sys.argv[sys.argv.index('--')+1:]
 if '--job' not in args or '--output' not in args or '--static' in args:
  raise ValueError('Expected --job and --output for non-static Hit study')
 job=Path(args[args.index('--job')+1]);out=Path(args[args.index('--output')+1])
 data=json.loads(job.read_text())
 if data.get('source_actions')!=['Hit_Chest'] or data.get('freeze_source_object_transform') is not True or data.get('retarget_to'):
  raise ValueError('Only explicit native Hit_Chest object-freeze studies are supported')
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 text=patched_source(BASE.read_text())
 exec(compile(text,str(BASE),'exec'),{'__name__':'__main__','__file__':str(BASE)})
 manifest=out/'manifest.json';receipt=json.loads(manifest.read_text())
 receipt['experimental_wrapper_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 receipt['experimental_status']='OBJECT_TRANSFORM_FREEZE_STUDY_NOT_APPROVED'
 receipt['limitations'].append('Source object transforms were muted for Hit_Chest only; source root motion and all contacts remain subject to review.')
 manifest.write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
