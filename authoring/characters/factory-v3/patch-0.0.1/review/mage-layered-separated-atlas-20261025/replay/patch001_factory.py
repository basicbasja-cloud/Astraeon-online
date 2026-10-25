"""Resumable six-character motion/paint/cutout production ledger.

Planning is never counted as authored art. Identical donor-pose jobs are shared;
paint and cutout reuse still requires matching camera, pose and body fitting.
"""
import argparse,concurrent.futures,hashlib,json,math,struct,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
TOOLS=Path(__file__).resolve().parent


def read(p):return json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def plan():
    config=read(BASE/'factory.json');jobs={};bindings={};paint_jobs={}
    approved_sources={s['file']:s['sha256']for s in config['sources'].values()if isinstance(s,dict)and'file'in s}
    for kind,klass in config['classes'].items():
        for name,a in klass['actions'].items():
            source=ROOT/a['source_file']
            if not source.is_file():raise ValueError('Missing source '+str(source))
            if filehash(source)!=approved_sources.get(a['source_file']):raise ValueError('Source differs from retained intake digest')
            geometry={'source_file':a['source_file'],'source_sha256':filehash(source),'source_actions':a['source_actions'],'frames':a['frames'],'loop':a['loop'],'ortho_scale':config.get('camera',{}).get('ortho_scale',3.55),'resolution':config['canvas']['source_guide'][0],'weapon':{'Swordsman':'sword','Mage':'staff','Archer':'bow'}[kind],'guide_aa':'OFF','renderer_sha256':filehash(TOOLS/'render_patch001_guides.py')}
            if config.get('camera',{}).get('up_offset')is not None:geometry['camera_up_offset']=config['camera']['up_offset']
            if a.get('explicit_source_samples')is not None:
                from render_explicit_patch001_guides import explicit_samples
                explicit_samples({**geometry,'explicit_source_samples':a['explicit_source_samples']})
                geometry['explicit_source_samples']=a['explicit_source_samples']
                geometry['explicit_sampling_implementation_sha256']=filehash(TOOLS/'render_explicit_patch001_guides.py')
                geometry['explicit_capture_png_sha256']=filehash(TOOLS/'render_frozen_patch001_guides.py')
            if a['source_provider']=='KayKit':
                geometry['retarget_to']=config['source']['file']
                geometry['retarget_to_sha256']=filehash(ROOT/config['source']['file'])
                geometry['retarget_implementation_sha256']=filehash(TOOLS/'kaykit_motion_adapter.py')
                geometry['closed_left_grip_revision']=1
                geometry['bow_proxy_basis']='wrist-local-aim'if'CombatRanged'in a['source_file']else'wrist-local-carry'
                if'CombatRanged'in a['source_file']:
                    geometry['arrow_release_phase']=a.get('arrow_release_phase',.03)
                    geometry['archery_contact_adapter']='cheek-anchor-arm-IK-floor-elbow-v3'
                    geometry['guide_aa']='8'
                geometry['pose_evaluation_revision']=2
                if a['source_actions'][0]in ['Ranged_Bow_Draw','Ranged_Bow_Draw_Up']:
                    geometry['source_ranges']={a['source_actions'][0]:[8,32]}
                    geometry['entry_transition']={'action':'Ranged_Bow_Idle','source_frame':0,'frames':4,'method':'local-joint-TRS-interpolation; no pixel warping'}
            else:geometry['pose_evaluation_revision']=2
            if kind=='Archer'and a['source_provider']=='Mesh2Motion':geometry['bow_proxy_basis']='wrist-local-carry'
            if a.get('floor_sit_adapter'):
                geometry['floor_sit_adapter']=a['floor_sit_adapter']
                geometry['floor_sit_implementation_sha256']=filehash(TOOLS/'floor_sit_adapter.py')
            for transition in ['entry_transition','exit_transition']:
                if a.get(transition):geometry[transition]=a[transition]
            if kind=='Mage':
                geometry.update({'staff_grip_mode':'wrist-local-prop-reference','held_staff_hand':'r','staff_arm_reference':'Idle_Lantern'})
            if a.get('source_ranges'):geometry['source_ranges']=a['source_ranges']
            if geometry.get('staff_arm_reference')or geometry.get('floor_sit_adapter'):
                geometry['render_pose_freeze_revision']=1
                geometry['render_pose_freeze_sha256']=filehash(TOOLS/'render_frozen_patch001_guides.py')
            if 'Sword_Regular_B_Rec' in a['source_actions']:geometry['source_ranges']={'Sword_Regular_B':[0,8],'Sword_Regular_B_Rec':[8,22]}
            key=digest(geometry)[:20]
            job=jobs.setdefault(key,{'id':key,**geometry,'directions':[],'uses':[]})
            job['directions']=[d for d in config['direction_inputs']if d in set(job['directions'])|set(a['authored_directions'])]
            job['uses'].append(kind+'/'+name);bindings[kind+'/'+name]=key
    for key,job in jobs.items():write(BASE/'guide-jobs'/f'{key}.json',job)
    for character in config['characters']:
        klass=config['classes'][character['class']]
        identity=ROOT/character['identity_reference']
        direction_sheet=ROOT/character['direction_reference_sheet']
        if not direction_sheet.is_file():raise ValueError('Missing direction identity sheet')
        reference_name=direction_sheet.stem.removesuffix('-turnaround')
        references=BASE/'identities/views'/reference_name
        reference_receipt=read(references/'receipt.json')
        if reference_receipt['source_sha256']!=filehash(direction_sheet):raise ValueError('Stale direction identity crops; regenerate them first')
        if not identity.is_file():raise ValueError('Missing character identity reference')
        for name,a in klass['actions'].items():
            # One pose family may serve multiple game actions with different
            # timing/effects. It is not re-painted and counted as new art.
            guide=bindings[character['class']+'/'+name]
            key=digest({'identity':filehash(identity),'direction_identity':filehash(direction_sheet),'direction_crop_revision':reference_receipt['head_crop_revision'],'fit':character['anatomy_fit_id'],'guide':guide})[:20]
            pj=paint_jobs.setdefault(key,{'id':key,'character':character['id'],'identity_reference':character['identity_reference'],'identity_sha256':filehash(identity),'fit_id':character['anatomy_fit_id'],'guide_job':guide,'directions':jobs[guide]['directions'],'frame_count':a['frames'],'actions':[],'status':'MISSING_PAINTED_MASTERS_AND_LABELS','master_first':True,'layers_from_same_frame':config['parts'],'generation_policy':'one complete source strip per action/view, then same-frame cutouts; no independent layer generation','approval':{'owner_approved':False,'runtime_admitted':False}})
            pj['actions'].append(name)
            if not(references/'receipt.json').is_file():raise ValueError('Prepare view-specific identity references before planning: '+reference_name)
            pj['direction_identity_references']={direction:{'full_view':str((references/f'{direction}.png').relative_to(ROOT)),'head_upper':str((references/f'{direction}-head-upper.png').relative_to(ROOT))}for direction in pj['directions']}
            pj['reference_authority']={'geometry':'current guide_job only','design':'matching-direction identity study; inspect view before use','generic_front_portrait_for_rear_views':False}
    for key,job in paint_jobs.items():write(BASE/'paint-jobs'/f'{key}.json',job)
    ledger={'schema_version':1,'characters':[c['id']for c in config['characters']],'guide_jobs':jobs,'action_guide_bindings':bindings,'paint_jobs':paint_jobs,'requested_action_instances':sum(len(config['classes'][c['class']]['actions'])for c in config['characters']),'requested_pose_positions':sum(a['frames']*len(a['authored_directions'])for c in config['characters']for a in config['classes'][c['class']]['actions'].values()),'source_capture_positions_after_reuse':sum(j['frames']*len(j['directions'])for j in jobs.values()),'planning_is_not_authored_coverage':True}
    write(BASE/'ledger.json',ledger);return ledger


def receipt_valid(job,folder=None):
    folder=Path(folder)if folder is not None else BASE/'guides'/job['id'];manifest=folder/'manifest.json'
    if not manifest.is_file():return False
    data=read(manifest)
    captured=data.get('job',{})
    geometry=lambda value:{k:v for k,v in value.items()if k not in ['uses','directions']}
    if geometry(captured)!=geometry(job)or data.get('frame_count')!=job['frames']:return False
    if job.get('explicit_source_samples')is not None:
        proof=data.get('sampling_override',{})
        if proof.get('implementation_sha256')!=job['explicit_sampling_implementation_sha256']or proof.get('canonical_source_sha256')!=job['renderer_sha256']or proof.get('explicit_source_samples')!=job['explicit_source_samples']or proof.get('body_or_prop_geometry_overridden')is not False:return False
        if data.get('implementation_digests_at_process_start',{}).get('render_explicit_patch001_guides.py')!=job['explicit_sampling_implementation_sha256']:return False
        images={f'{d}/{i:03d}.png'for d in job['directions']for i in range(job['frames'])};png=data.get('png_normalization',{});rows=png.get('frames',[])
        if png.get('implementation_sha256')!=job['explicit_capture_png_sha256']or len(rows)!=len(images)or{r.get('image')for r in rows}!=images:return False
        for row in rows:
            path=folder/row['image']
            if row.get('visible_rgb_or_alpha_changed')is not False or not path.is_file()or filehash(path)!=row.get('normalized_sha256'):return False
        for direction in job['directions']:
            frames=data.get('views',{}).get(direction,{}).get('frames',[])
            if [r.get('source_frame')for r in frames]!=job['explicit_source_samples']or any(r.get('action')!=job['source_actions'][0]for r in frames):return False
    if job.get('render_pose_freeze_revision'):
        proof=data.get('render_pose_freeze',{});images={f'{d}/{i:03d}.png'for d in job['directions']for i in range(job['frames'])}
        rows=proof.get('rendered_frames',[]);pngs=data.get('png_normalization',{}).get('frames',[])
        if proof.get('revision')!=job['render_pose_freeze_revision']or proof.get('implementation_sha256')!=job['render_pose_freeze_sha256']:return False
        if data.get('implementation_digests_at_process_start',{}).get('render_frozen_patch001_guides.py')!=job['render_pose_freeze_sha256']:return False
        if len(rows)!=len(images)or{r.get('image')for r in rows}!=images or len(pngs)!=len(images)or{r.get('image')for r in pngs}!=images:return False
        for row in rows:
            if not row.get('actors'):return False
            for actor in row['actors']:
                error=actor.get('max_world_matrix_component_error')
                if isinstance(error,bool)or not isinstance(error,(float,int))or not math.isfinite(error)or not 0<=error<=1e-5:return False
        for row in pngs:
            path=folder/row['image']
            if row.get('visible_rgb_or_alpha_changed')is not False or not path.is_file()or filehash(path)!=row.get('normalized_sha256'):return False
    for d in job['directions']:
        if len(data.get('views',{}).get(d,{}).get('frames',[]))!=job['frames']:return False
        for i in range(job['frames']):
            path=folder/d/f'{i:03d}.png'
            if not path.is_file():return False
            with path.open('rb')as image:header=image.read(24)
            if len(header)!=24 or header[:8]!=b'\x89PNG\r\n\x1a\n'or struct.unpack('>II',header[16:24])!=(job['resolution'],job['resolution']):return False
    return True


def render_one(job):
    if receipt_valid(job):return {'job':job['id'],'state':'CACHED_GUIDE'}
    folder=BASE/'guides'/job['id'];folder.mkdir(parents=True,exist_ok=True)
    entrypoint='render_explicit_patch001_guides.py'if job.get('explicit_source_samples')is not None else'render_frozen_patch001_guides.py'if job.get('render_pose_freeze_revision')else'render_patch001_guides.py'
    command=['blender','-b','-t','2','--python-exit-code','1','--python',str(TOOLS/entrypoint),'--','--job',str(BASE/'guide-jobs'/f"{job['id']}.json"),'--output',str(folder)]
    with(folder/'render.log').open('w')as log:result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode or not receipt_valid(job):raise RuntimeError(f"Guide failed: {job['id']}; inspect {folder/'render.log'}")
    return {'job':job['id'],'state':'SOURCE_GUIDE_CAPTURED'}


def status(ledger):
    guides=sum(receipt_valid(j)for j in ledger['guide_jobs'].values())
    # An importer receipt must exist; source guides and concepts never satisfy
    # this count. Empty files are not accepted as painted/action coverage.
    imported=[]
    for job in ledger['paint_jobs'].values():
        p=BASE/'cutouts'/job['id']/'import-receipt.json'
        if p.is_file():
            r=read(p)
            if r.get('paint_job')==job['id']and r.get('all_frames_present')and r.get('recomposition_mismatches')==0:imported.append(job['id'])
    report={'characters':len(ledger['characters']),'requested_action_instances':ledger['requested_action_instances'],'requested_pose_positions_before_aliases':ledger['requested_pose_positions'],'unique_guide_jobs':len(ledger['guide_jobs']),'captured_guide_jobs':guides,'source_capture_positions_after_reuse':ledger['source_capture_positions_after_reuse'],'unique_paint_jobs':len(ledger['paint_jobs']),'imported_cutout_jobs':len(imported),'missing_cutout_jobs':len(ledger['paint_jobs'])-len(imported),'owner_approved':False,'runtime_admitted':False,'coverage_complete':len(imported)==len(ledger['paint_jobs'])and guides==len(ledger['guide_jobs']),'complete':False,'completion_policy':'Coverage alone does not establish visual acceptance or runtime admission'}
    write(BASE/'progress.json',report);return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['plan','guides','status']);p.add_argument('--class',dest='kind',choices=['all','Swordsman','Mage','Archer'],default='all');p.add_argument('--actions',help='Comma-separated action pilot, or omit for all');p.add_argument('--workers',type=int,default=2);a=p.parse_args()
    ledger=plan()  # Re-read input/config hashes before deciding which captures are cached.
    if a.stage=='guides':
        wanted=set(a.actions.split(','))if a.actions else None
        jobs=[j for j in ledger['guide_jobs'].values()if any((a.kind=='all'or use.split('/')[0]==a.kind)and(wanted is None or use.split('/')[1]in wanted)for use in j['uses'])]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(4,a.workers)))as pool:
            futures={pool.submit(render_one,j):j for j in jobs}
            for future in concurrent.futures.as_completed(futures):print(json.dumps(future.result()),flush=True)
    print(json.dumps(status(ledger),indent=2))


if __name__=='__main__':main()
