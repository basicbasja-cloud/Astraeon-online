"""Import replacement FX through the real factory, preserving every base asset.

The selected action remains a variant until character-level admission. The
original store/bindings are unchanged; the variant store is portable in Git.
"""
import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import patch001_factory as factory
import cutout_asset_store as assets
import import_patch001_cutouts as importer
import package_imported_action_review as packer
from track_visible_cutouts import pin_inputs, verify_inputs


def build(job_id, intake_path, effects, output):
    root, base = factory.ROOT, factory.BASE
    effects, output, intake_path = effects.resolve(), output.resolve(), intake_path.resolve()
    if output.exists() or not output.is_relative_to(root) or not effects.is_relative_to(root):
        raise ValueError('Choose a new repository destination and repository FX frames')
    ledger = json.loads((base/'ledger.json').read_text())
    job = ledger['paint_jobs'][job_id]
    original = json.loads((base/'cutouts'/job_id/'bindings.json').read_text())
    intake = json.loads(intake_path.read_text())
    if intake.get('pose_recipes') or intake.get('source_pose_recipes'):
        raise ValueError('Certified remapping recipes need an explicit portable reference adapter')
    pinned = pin_inputs([base/'cutouts'/job_id/'bindings.json',base/'cutouts'/job_id/'import-receipt.json',base/'cutout-store/index.json',base/'factory.json',base/'ledger.json',intake_path])
    output.mkdir(parents=True)
    for row in intake['frames']:
        row['master'] = os.path.relpath((intake_path.parent/row['master']).resolve(),output)
        for role,file in row['parts'].items():
            path = effects/row['direction']/role/f"{row['index']:03d}.png" if role.startswith('WeaponLight') else (intake_path.parent/file).resolve()
            row['parts'][role] = os.path.relpath(path,output)
    manifest = output/'import-manifest.json'
    manifest.write_text(json.dumps(intake,indent=2)+'\n')
    variant_store = output/'factory-store'
    # Only filesystem roots are redirected: every validator/register/packer runs.
    replay_root=root/'.factory-replay';replay_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fx-variant-',dir=replay_root) as work:
        sandbox=Path(work)
        for name in ['factory.json','ledger.json']:shutil.copy2(base/name,sandbox/name)
        (sandbox/'guides').mkdir();(sandbox/'guides'/job['guide_job']).symlink_to(base/'guides'/job['guide_job'],target_is_directory=True)
        with patch.object(factory,'BASE',sandbox),patch.object(importer,'BASE',sandbox),patch.object(importer,'STORE',variant_store),patch.object(assets,'STORE',variant_store):
            importer.import_job(job_id,manifest)
        shutil.copy2(variant_store/'index.json',sandbox/'cutout-store-index.json')
        (sandbox/'cutout-store').mkdir();shutil.copy2(variant_store/'index.json',sandbox/'cutout-store/index.json')
        rebuilt=json.loads((sandbox/'cutouts'/job_id/'bindings.json').read_text())
        old={(r['direction'],r['index']):r for r in original['frames']};same=0
        for row in rebuilt['frames']:
            prior=old[row['direction'],row['index']]
            for key in ['pose_id','camera_id','sockets','source_pose_index','base_draw_order','layer_draw_order']:
                if row.get(key)!=prior.get(key):raise ValueError('FX variant changed pose fitting/order: '+key)
            for role,identity in prior['assets'].items():
                if not role.startswith('WeaponLight'):
                    if row['assets'][role]!=identity:raise ValueError('FX variant changed base asset')
                    same+=1
        for name in ['bindings.json','import-receipt.json']:shutil.copy2(sandbox/'cutouts'/job_id/name,variant_store/name)
        with patch.object(packer,'BASE',sandbox):packer.package(job_id,manifest,output/'runtime')
    template=root/'docs/character-factory/review/patch001-imported-swordsman-basicattack-20261024'
    prefix=os.path.relpath(root,output/'runtime').replace(os.sep,'/')+'/'
    for name in ['index.html','review.js','capture.py']:
        source=(template/name).read_text()
        if name in ['index.html','review.js']:source=source.replace('../../../../',prefix).replace('actual factory import','FX variant factory import')
        else:source=source.replace("docs/character-factory/review/patch001-imported-swordsman-basicattack-20261024",str((output/'runtime').relative_to(root)))
        (output/'runtime'/name).write_text(source)
    verify_inputs(pinned)
    proof={'status':'REAL_FACTORY_FX_VARIANT_NOT_CHARACTER_ADMISSION','paint_job':job_id,'guide_job':job['guide_job'],'imported_frames':len(rebuilt['frames']),'unchanged_non_fx_asset_bindings':same,'baseline_factory_changed':False,'runtime_admitted':False,'baseline_pins':pinned}
    (output/'factory-variant-receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
    return {k:v for k,v in proof.items()if k!='baseline_pins'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paint-job',required=True)
    for name in ['intake','effects','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.paint_job,a.intake,a.effects,a.output)))
