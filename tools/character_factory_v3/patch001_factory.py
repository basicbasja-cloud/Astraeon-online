"""Resumable six-character motion/paint/cutout production ledger.

Planning is never counted as authored art. Identical donor-pose jobs are shared;
paint and cutout reuse still requires matching camera, pose and body fitting.
"""
import argparse,concurrent.futures,hashlib,json,subprocess,sys
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
            geometry={'source_file':a['source_file'],'source_sha256':filehash(source),'source_actions':a['source_actions'],'frames':a['frames'],'loop':a['loop'],'ortho_scale':3.55,'resolution':1024,'weapon':{'Swordsman':'sword','Mage':'staff','Archer':'bow'}[kind],'guide_aa':'OFF'}
            if a['source_provider']=='KayKit':geometry['retarget_to']=config['source']['file']
            if kind=='Mage':geometry['staff_grip_mode']='wrist-local-idle-reference'
            if 'Sword_Regular_B_Rec' in a['source_actions']:geometry['source_ranges']={'Sword_Regular_B':[0,8],'Sword_Regular_B_Rec':[8,22]}
            key=digest(geometry)[:20]
            job=jobs.setdefault(key,{'id':key,**geometry,'directions':[],'uses':[]})
            job['directions']=[d for d in config['direction_inputs']if d in set(job['directions'])|set(a['authored_directions'])]
            job['uses'].append(kind+'/'+name);bindings[kind+'/'+name]=key
    for key,job in jobs.items():write(BASE/'guide-jobs'/f'{key}.json',job)
    for character in config['characters']:
        klass=config['classes'][character['class']]
        identity=ROOT/character['identity_reference']
        if not identity.is_file():raise ValueError('Missing character identity reference')
        for name,a in klass['actions'].items():
            # One pose family may serve multiple game actions with different
            # timing/effects. It is not re-painted and counted as new art.
            guide=bindings[character['class']+'/'+name]
            key=digest({'identity':filehash(identity),'fit':character['anatomy_fit_id'],'guide':guide})[:20]
            pj=paint_jobs.setdefault(key,{'id':key,'character':character['id'],'identity_reference':character['identity_reference'],'identity_sha256':filehash(identity),'fit_id':character['anatomy_fit_id'],'guide_job':guide,'directions':jobs[guide]['directions'],'frame_count':a['frames'],'actions':[],'status':'MISSING_PAINTED_MASTERS_AND_LABELS','master_first':True,'layers_from_same_frame':config['parts'],'generation_policy':'one complete source strip per action/view, then same-frame cutouts; no independent layer generation','approval':{'owner_approved':False,'runtime_admitted':False}})
            pj['actions'].append(name)
    for key,job in paint_jobs.items():write(BASE/'paint-jobs'/f'{key}.json',job)
    ledger={'schema_version':1,'characters':[c['id']for c in config['characters']],'guide_jobs':jobs,'action_guide_bindings':bindings,'paint_jobs':paint_jobs,'requested_action_instances':sum(len(config['classes'][c['class']]['actions'])for c in config['characters']),'requested_pose_positions':sum(a['frames']*len(a['authored_directions'])for c in config['characters']for a in config['classes'][c['class']]['actions'].values()),'source_capture_positions_after_reuse':sum(j['frames']*len(j['directions'])for j in jobs.values()),'planning_is_not_authored_coverage':True}
    write(BASE/'ledger.json',ledger);return ledger


def receipt_valid(job):
    folder=BASE/'guides'/job['id'];manifest=folder/'manifest.json'
    if not manifest.is_file():return False
    data=read(manifest)
    if data.get('job')!=job or data.get('frame_count')!=job['frames']:return False
    for d in job['directions']:
        if len(data.get('views',{}).get(d,{}).get('frames',[]))!=job['frames']:return False
        for i in range(job['frames']):
            if not(folder/d/f'{i:03d}.png').is_file():return False
    return True


def render_one(job):
    if receipt_valid(job):return {'job':job['id'],'state':'CACHED_GUIDE'}
    folder=BASE/'guides'/job['id'];folder.mkdir(parents=True,exist_ok=True)
    command=['blender','-b','-t','2','--python-exit-code','1','--python',str(TOOLS/'render_patch001_guides.py'),'--','--job',str(BASE/'guide-jobs'/f"{job['id']}.json"),'--output',str(folder)]
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
    ledger=plan()if a.stage=='plan'or not(BASE/'ledger.json').exists()else read(BASE/'ledger.json')
    if a.stage=='guides':
        wanted=set(a.actions.split(','))if a.actions else None
        jobs=[j for j in ledger['guide_jobs'].values()if any((a.kind=='all'or use.split('/')[0]==a.kind)and(wanted is None or use.split('/')[1]in wanted)for use in j['uses'])]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(4,a.workers)))as pool:
            futures={pool.submit(render_one,j):j for j in jobs}
            for future in concurrent.futures.as_completed(futures):print(json.dumps(future.result()),flush=True)
    print(json.dumps(status(ledger),indent=2))


if __name__=='__main__':main()
