"""Reconcile and import the retained male BasicAttack without redrawing it.

Requires the original native sampling, matching projected source geometry,
verified canonical cutouts and actual native-rig socket export. No missing
action is substituted and no visual/runtime approval is inferred.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
from patch001_factory import ROOT,BASE,read,write,receipt_valid,filehash
from import_patch001_cutouts import import_job

ROLES=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront']


def prepare(source,sockets_path,output):
    if output.exists():raise ValueError('Preserve earlier intake manifests; choose a fresh destination')
    ledger=read(BASE/'ledger.json');job=next(j for j in ledger['paint_jobs'].values()if j['character']=='swordsman-male-patch001'and'BasicAttack'in j['actions'])
    capture_job=ledger['guide_jobs'][job['guide_job']]
    if not receipt_valid(capture_job):raise ValueError('Matching completed source capture is missing')
    catalog=read(ROOT/'authoring/characters/factory-v3/configs/layered_action_catalog.json');spec=catalog['actions']['BasicAttack']
    if capture_job.get('explicit_source_samples')!=spec['source_samples']or capture_job['frames']!=spec['poses_per_direction']or capture_job['source_sha256']!=catalog['source_sha256']:raise ValueError('Retained native pose contract differs')
    manifest_path=BASE/'guides'/job['guide_job']/'manifest.json';guide=read(manifest_path);receipt=read(source/'receipt.json');verified=read(source/'verification-receipt.json')
    if verified.get('verified_existing_images')!=896 or verified.get('original_receipt_sha256')!=filehash(source/'receipt.json'):raise ValueError('Verify all retained canonical assets before intake')
    socket_data=read(sockets_path)
    if socket_data['guide_job']!=job['guide_job']or socket_data['guide_manifest_sha256']!=filehash(manifest_path)or socket_data['maximum_landmark_error_author_px']>1e-3:raise ValueError('Native socket verification differs')
    socket_rows={(r['direction'],r['index']):r for r in socket_data['frames']}
    original=ROOT/spec['directory'];original_guide=read(original/'source-guides/manifest.json');views={v['direction']:v for v in receipt['frames']if v['action']=='BasicAttack'}
    if set(views)!=set(job['directions']):raise ValueError('Missing preserved source view')
    output.mkdir(parents=True);records=[];proof=[]
    relative=lambda path:os.path.relpath(path,output)
    for direction in job['directions']:
        native=next(c for c in original_guide['clips']if c['clip']==direction)['frames'];view=views[direction]
        for i,(legacy,old,captured)in enumerate(zip(view['frames'],native,guide['views'][direction]['frames'])):
            if (legacy['source_action'],legacy['source_frame'])!=(captured['action'],captured['source_frame']):raise ValueError('Painted pose does not correspond to native sample')
            scale=legacy['camera_scale'];offset=np.array(legacy['canvas_translation']);errors={}
            for name,xy in old['landmarks'].items():
                if name in captured['landmarks']:errors[name]=float(np.linalg.norm(np.array(xy)*.5*scale+offset-np.array(captured['landmarks'][name])*.5))
            for old_key,name in [('sword_grip','grip'),('sword_tip','tip')]:errors[name]=float(np.linalg.norm(np.array(old[old_key])*.5*scale+offset-np.array(captured['weapon_guide'][name])*.5))
            if max(errors.values())>1e-3:raise ValueError('Retained guide geometry differs from current capture')
            sockets=socket_rows[direction,i]
            if (sockets['source_action'],sockets['source_frame'])!=(captured['action'],captured['source_frame']):raise ValueError('Socket source pose differs')
            folder=source/'BasicAttack'/direction
            records.append({'direction':direction,'index':i,'master':relative(folder/'Master'/f'{i:03d}.png'),'parts':{r:relative(folder/r/f'{i:03d}.png')for r in ROLES},'sockets':sockets['sockets'],'base_draw_order':['BodyCostume','HeadHair','Weapon','WeaponHandOccluder'],'layer_draw_order':['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder']})
            proof.append({'direction':direction,'index':i,'source_action':captured['action'],'source_frame':captured['source_frame'],'source_projection_errors_author_px':errors,'master_sha256':filehash(folder/'Master'/f'{i:03d}.png')})
    if len(records)!=len(job['directions'])*job['frame_count']:raise ValueError('Incomplete retained art timeline')
    intake={'guide_job':job['guide_job'],'fit_id':job['fit_id'],'frames':records,'provenance':'Existing earlier Swordsman artwork, exact retained native samples and documented fixed-camera canonical transform','hidden_surfaces_authored':False,'owner_approved':False,'runtime_admitted':False}
    write(output/'import-manifest.json',intake)
    write(output/'reconciliation-proof.json',{'paint_job':job['id'],'guide_job':job['guide_job'],'retained_receipt_sha256':filehash(source/'receipt.json'),'retained_verification_sha256':filehash(source/'verification-receipt.json'),'native_sockets_sha256':filehash(sockets_path),'implementation_sha256':filehash(Path(__file__)),'frames':proof,'maximum_source_projection_error_author_px':max(max(r['source_projection_errors_author_px'].values())for r in proof),'painted_pixels_modified':False,'actions_substituted':False,'runtime_admitted':False})
    return job['id'],output/'import-manifest.json'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','sockets','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--import-cutouts',action='store_true');a=p.parse_args();job,manifest=prepare(a.source.resolve(),a.sockets.resolve(),a.output.resolve())
    if a.import_cutouts:import_job(job,manifest)
    else:print(json.dumps({'paint_job':job,'manifest':str(manifest)}))
