"""Reimport retained art against a fresh Blender capture into an isolated store.

Only output roots are redirected. Real source validation, reconciliation,
recomposition, pixel hashing, registration and index writing are executed.
The existing imported character and cutout store are never overwritten.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
import patch001_factory as factory
import cutout_asset_store as asset_store
import import_patch001_cutouts as importer
from import_preserved_basic_attack import prepare
from source_capture_identity import sha
from track_visible_cutouts import pin_inputs,verify_inputs


def verify(source,sockets,fresh_guide,output,effects=None):
    root=factory.ROOT;baseline=factory.BASE;store=asset_store.STORE
    if output.exists()or not output.resolve().is_relative_to(root):raise ValueError('Choose a fresh isolated destination under the repository root')
    output.mkdir(parents=True);job_id,intake=prepare(source,sockets,output/'intake',fresh_guide)
    if effects is not None:
        import os
        selected=json.loads(intake.read_text())
        for row in selected['frames']:
            for role in ['WeaponLightBack','WeaponLightFront']:
                path=effects/row['direction']/role/f"{row['index']:03d}.png"
                if not path.is_file():raise ValueError('Incomplete selected effect profile')
                row['parts'][role]=os.path.relpath(path,intake.parent)
        intake.write_text(json.dumps(selected,indent=2)+'\n')
    old_bindings_path=baseline/'cutouts'/job_id/'bindings.json';old_bindings=json.loads(old_bindings_path.read_text());old_index=json.loads((store/'index.json').read_text());expected_assets={v for r in old_bindings['frames']for v in r['assets'].values()};expected_objects={old_index['assets'][key]['object']for key in expected_assets}
    manifest=json.loads(intake.read_text());original_parts=[(intake.parent/path).resolve()for r in manifest['frames']for path in [r['master'],*r['parts'].values()]];pinned=pin_inputs([old_bindings_path,store/'index.json',*original_parts])
    sandbox=output/'factory';sandbox.mkdir();shutil.copy2(baseline/'factory.json',sandbox/'factory.json');shutil.copy2(baseline/'ledger.json',sandbox/'ledger.json');(sandbox/'guides').mkdir();guide_id=manifest['guide_job'];(sandbox/'guides'/guide_id).symlink_to(fresh_guide.resolve(),target_is_directory=True);new_store=sandbox/'cutout-store'
    with patch.object(factory,'BASE',sandbox),patch.object(importer,'BASE',sandbox),patch.object(importer,'STORE',new_store),patch.object(asset_store,'STORE',new_store):
        importer.import_job(job_id,intake)
    rebuilt=json.loads((sandbox/'cutouts'/job_id/'bindings.json').read_text());new_index=json.loads((new_store/'index.json').read_text())
    if rebuilt!=old_bindings:raise ValueError('Rebuilt pose bindings differ from retained factory')
    if set(new_index['assets'])!=expected_assets or set(new_index['objects'])!=expected_objects:raise ValueError('Rebuilt asset/pixel identities differ')
    if any(new_index['assets'][key]!=old_index['assets'][key]for key in expected_assets):raise ValueError('Rebuilt fitting compatibility metadata differs')
    objects=[]
    for key in sorted(expected_objects):
        old_path=root/old_index['objects'][key]['file'];new_path=root/new_index['objects'][key]['file'];left=np.array(Image.open(old_path).convert('RGBA'));right=np.array(Image.open(new_path).convert('RGBA'));left[left[:,:,3]==0]=0;right[right[:,:,3]==0]=0
        if hashlib.sha256(left.tobytes()).hexdigest()!=key or not np.array_equal(left,right):raise ValueError('Rebuilt object pixels differ')
        objects.append({'object':key,'decoded_rgba_identical':True,'png_bytes_identical':sha(old_path)==sha(new_path)})
    verify_inputs(pinned);reconciliation=json.loads((intake.parent/'reconciliation-proof.json').read_text());result={'status':'FRESH_CAPTURE_REIMPORT_MATCHES_RETAINED_FACTORY_NOT_RELEASE_APPROVAL','paint_job':job_id,'guide_job':guide_id,'implementation_sha256':sha(Path(__file__)),'fresh_guide_manifest_sha256':sha(fresh_guide/'manifest.json'),'source_reference_verification':reconciliation['source_capture_verification'],'reimported_poses':len(rebuilt['frames']),'part_bindings':sum(len(r['assets'])for r in rebuilt['frames']),'distinct_pixel_objects':len(objects),'asset_ids_and_metadata_identical':True,'pose_bindings_identical':True,'baseline_source_files_changed':False,'objects':objects,'runtime_admitted':False,'art_approval_implied':False}
    (output/'replay-proof.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','sockets','fresh-guide','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--effects',type=Path)
    a=p.parse_args();r=verify(a.source.resolve(),a.sockets.resolve(),a.fresh_guide.resolve(),a.output.resolve(),a.effects.resolve()if a.effects else None);print(json.dumps({k:v for k,v in r.items()if k not in ['objects','source_reference_verification']}))
