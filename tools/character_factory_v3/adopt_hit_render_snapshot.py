"""Rebind only pending Swordsman Hit planning to a verified render-state capture.

Old job files/captures/art remain intact. This does not approve a motion, master,
cutout, variant or runtime package. Apply only while no other planner is writing.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import tempfile

import patch001_factory as factory
from render_hit_snapshot_guides import planned_geometry

PROFILE='native-hit-declared-pose-v1'


def bytes_for(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()


def proposal(base,root):
    base=base.resolve();root=root.resolve();pinned={}
    def pin(path):
        path=path.resolve();data=path.read_bytes();value=hashlib.sha256(data).hexdigest()
        if path in pinned and pinned[path]!=value:raise ValueError('Planning input changed during proposal')
        pinned[path]=value;return data
    if (base/'factory.json').is_symlink()or(base/'ledger.json').is_symlink():raise ValueError('Preserve linked planning inputs; reconcile explicitly')
    config=json.loads(pin(base/'factory.json'));ledger=json.loads(pin(base/'ledger.json'))
    before_config=copy.deepcopy(config);before_ledger=copy.deepcopy(ledger)
    old_id=ledger['action_guide_bindings']['Swordsman/Hit'];old_job=ledger['guide_jobs'][old_id]
    if old_job['uses']!=['Swordsman/Hit']:raise ValueError('Hit capture is shared by an unexpected action; reconcile explicitly')
    geometry={k:v for k,v in old_job.items()if k not in('id','directions','uses')}
    if factory.digest(geometry)[:20]!=old_id:raise ValueError('Existing source-job identity does not match its geometry')
    geometry=planned_geometry(geometry,PROFILE);new_id=factory.digest(geometry)[:20]
    for field,name in(('renderer_sha256','render_patch001_guides.py'),('render_snapshot_sha256','render_hit_snapshot_guides.py'),
                       ('render_snapshot_png_sha256','seal_source_guide_replay.py')):
        if hashlib.sha256(pin(factory.TOOLS/name)).hexdigest()!=geometry[field]:raise ValueError('Capture implementation changed during proposal')
    job={'id':new_id,**geometry,'directions':old_job['directions'],'uses':old_job['uses']}
    mapping={};new_paint={}
    for key,paint in ledger['paint_jobs'].items():
        if paint['guide_job']!=old_id:
            new_paint[key]=paint;continue
        if paint['actions']!=['Hit']or paint.get('status')!='MISSING_PAINTED_MASTERS_AND_LABELS'or paint.get('approval',{}).get('owner_approved')or paint.get('approval',{}).get('runtime_admitted'):
            raise ValueError('Existing Hit artwork or reuse requires explicit reconciliation')
        if (base/'cutouts'/key).exists()or(base/'cutouts'/key).is_symlink():raise ValueError('Preserve the existing Hit intake; do not silently change its source contract')
        character=next(c for c in config['characters']if c['id']==paint['character'])
        sheet=root/character['direction_reference_sheet'];reference_name=sheet.stem.removesuffix('-turnaround')
        reference=base/'identities/views'/reference_name/'receipt.json';crop=json.loads(pin(reference))
        identity=root/paint['identity_reference']
        identity_hash=hashlib.sha256(pin(identity)).hexdigest();sheet_hash=hashlib.sha256(pin(sheet)).hexdigest()
        if identity_hash!=paint['identity_sha256']or sheet_hash!=crop['source_sha256']:
            raise ValueError('Character identity references changed before migration')
        inputs={'identity':paint['identity_sha256'],'direction_identity':sheet_hash,
                'direction_crop_revision':crop['head_crop_revision'],'fit':paint['fit_id'],'guide':old_id}
        if factory.digest(inputs)[:20]!=key:raise ValueError('Existing paint-job key does not match current reference inputs')
        new_key=factory.digest({**inputs,'guide':new_id})[:20]
        if new_key!=key and new_key in ledger['paint_jobs']:raise ValueError('New Hit paint job would collide with existing work')
        new_paint[new_key]={**paint,'id':new_key,'guide_job':new_id,
                            'status':'MISSING_PAINTED_MASTERS_AND_LABELS',
                            'approval':{**paint.get('approval',{}),'owner_approved':False,'runtime_admitted':False}}
        mapping[key]=new_key
    if len(mapping)!=2:raise ValueError('Expected exactly male and female pending Swordsman Hit jobs')
    config['classes']['Swordsman']['actions']['Hit']['render_snapshot_profile']=PROFILE
    ledger['guide_jobs']={new_id if key==old_id else key:job if key==old_id else value
                          for key,value in ledger['guide_jobs'].items()}
    ledger['action_guide_bindings']['Swordsman/Hit']=new_id;ledger['paint_jobs']=new_paint
    unaffected_guides=[k for k in before_ledger['guide_jobs']if k!=old_id]
    unaffected_paint=[k for k in before_ledger['paint_jobs']if k not in mapping]
    if any(before_ledger['guide_jobs'][k]!=ledger['guide_jobs'][k]for k in unaffected_guides):raise ValueError('Unrelated guide changed')
    if any(before_ledger['paint_jobs'][k]!=ledger['paint_jobs'][k]for k in unaffected_paint):raise ValueError('Unrelated paint job changed')
    probe=copy.deepcopy(config)
    probe['classes']['Swordsman']['actions']['Hit'].pop('render_snapshot_profile',None)
    old_probe=copy.deepcopy(before_config)
    old_probe['classes']['Swordsman']['actions']['Hit'].pop('render_snapshot_profile',None)
    if probe!=old_probe:raise ValueError('Unrelated config changed')
    documents={base/'factory.json':config,base/'ledger.json':ledger,base/'guide-jobs'/f'{new_id}.json':job}
    documents.update({base/'paint-jobs'/f'{key}.json':new_paint[key]for key in mapping.values()})
    for path,value in documents.items():
        if path not in(base/'factory.json',base/'ledger.json')and(path.exists()or path.is_symlink()):
            if path.is_symlink()or factory.read(path)!=value:raise ValueError('Preserve conflicting existing planning file: '+str(path))
    proof={'status':'PENDING_HIT_SOURCE_REBIND_NOT_ART_APPROVAL','old_guide_job':old_id,'new_guide_job':new_id,
           'paint_job_mapping':mapping,'unrelated_guide_jobs_unchanged':len(unaffected_guides),
           'unrelated_paint_jobs_unchanged':len(unaffected_paint),
           'logical_action_instances':ledger['requested_action_instances'],
           'guide_jobs':len(ledger['guide_jobs']),'paint_jobs':len(ledger['paint_jobs']),
           'old_job_files_deleted':False,'art_or_runtime_admission':False,
           'already_current':old_id==new_id and before_config==config and before_ledger==ledger,
           'input_sha256':{str(p.relative_to(root))if p.is_relative_to(root)else str(p):value for p,value in pinned.items()}}
    return documents,job,proof


def replace_bytes(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.hit-plan-',suffix='.tmp',delete=False)as stream:
            temporary=Path(stream.name);stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def adopt(base,root,capture):
    documents,job,proof=proposal(base,root)
    if not factory.receipt_valid(job,capture):raise ValueError('Complete verified Hit snapshot capture is required before rebinding')
    for relative,value in proof['input_sha256'].items():
        if factory.filehash(root/relative)!=value:raise ValueError('Plan inputs changed before adoption')
    if not proof['already_current']:
        previous={path:path.read_bytes()if path.exists()else None for path in documents}
        written=[]
        try:
            for path,value in documents.items():
                written.append(path);replace_bytes(path,bytes_for(value))
        except BaseException:
            for path in reversed(written):
                if previous[path]is None:path.unlink(missing_ok=True)
                else:replace_bytes(path,previous[path])
            raise
    proof.update({'status':'HIT_SOURCE_REBOUND_NOT_ART_APPROVAL','verified_capture_manifest_sha256':factory.filehash(capture/'manifest.json'),
                  'implementation_sha256':factory.filehash(Path(__file__)),'applied':True})
    return proof


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path);parser.add_argument('--apply',action='store_true')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists()or args.output.is_symlink():raise ValueError('Choose a fresh proof output')
    if args.apply:
        if args.capture is None:parser.error('--capture is required with --apply')
        proof=adopt(factory.BASE,factory.ROOT,args.capture)
    else:_,_,proof=proposal(factory.BASE,factory.ROOT)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(bytes_for(proof))
    print(json.dumps(proof))
