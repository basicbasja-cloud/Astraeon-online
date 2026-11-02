"""Import complete same-frame cutouts without fabricating missing coverage.

An input manifest has guide_job, fit_id and frames. Each frame specifies direction,
index, master, parts (paths for real visible layers) and sockets. Labels may be
provided instead of the five base part files. Effects remain separate images.
"""
import argparse,hashlib,io,json,math,os,shutil,tempfile
from contextlib import contextmanager
from pathlib import Path
import numpy as np
from PIL import Image
from patch001_factory import BASE,ROOT,read,write,receipt_valid,digest
from cutout_asset_store import STORE,ROLES,register,save_index,import_frame,validate_object,restore_index_bytes
from register_clear_paint_candidate import validated_pose_map,resolved_recipe

BASE_ORDER=['WeaponBack','BackAccessory','BodyCostume','HeadHair','Weapon','WeaponHandOccluder','Headgear']

def source_pose_maps(manifest,guide,guide_path,manifest_folder):
    """Keep timeline slots distinct from a certified held source pose."""
    maps={};evidence={}
    recipes=manifest.get('pose_recipes',{})
    if not isinstance(recipes,dict) or set(recipes)-set(guide['views']):raise ValueError('Invalid pose recipe directions')
    for direction in guide['views']:
        if direction not in recipes:
            maps[direction]=list(range(guide['frame_count']));continue
        path=(manifest_folder/recipes[direction]).resolve();recipe=read(path)
        if recipe.get('guide_manifest_sha256')!=hashlib.sha256(guide_path.read_bytes()).hexdigest():raise ValueError('Pose recipe guide digest mismatch')
        # Certificates in a persisted recipe resolve against the recipe itself.
        recipe=resolved_recipe(recipe,path.parent)
        maps[direction]=validated_pose_map(recipe,guide,direction)
        evidence[direction]={'recipe_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_pose_indices':maps[direction],'certificates':{k:hashlib.sha256(Path(v).read_bytes()).hexdigest()for k,v in recipe['certificates'].items()}}
    return maps,evidence

def visible_draw_order(parts,requested=None):
    expected={r for r in parts if r in BASE_ORDER}
    order=requested if requested is not None else [r for r in BASE_ORDER if r in expected]
    if not isinstance(order,list)or any(not isinstance(r,str)for r in order)or len(order)!=len(expected)or set(order)!=expected:raise ValueError('Base draw order must contain each present character role exactly once')
    return order


def authored_layer_order(parts,base_order,requested=None):
    if requested is None:return None
    if not isinstance(requested,list)or len(requested)!=len(parts)or len(set(requested))!=len(requested)or set(requested)!=set(parts):raise ValueError('Authored layer order must contain every actual part exactly once')
    if [r for r in requested if r in BASE_ORDER]!=base_order:raise ValueError('Authored FX order changes the declared base ordering')
    return requested


@contextmanager
def publication_lock():
    """Fail fast rather than let two batch imports overwrite the shared index."""
    STORE.mkdir(parents=True,exist_ok=True);lock=STORE/'.cutout-import.lock'
    try:descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError as exc:raise ValueError('Another cutout import owns the publication lock; inspect before retrying') from exc
    try:
        with os.fdopen(descriptor,'w') as stream:stream.write(str(os.getpid())+'\n')
        yield
    finally:lock.unlink()


def publish_staged_import(staged,folder,objects,index,validate_inputs):
    """Publish only a complete intake; its receipt is the final readiness marker.

    This handles ordinary validation/I/O exceptions, not machine crashes across
    several filesystem operations. Other direct store writers must run separately.
    """
    created=[];reserved=False;index_attempted=False
    with publication_lock():
        if folder.exists()or folder.is_symlink():raise ValueError('Cutout import target already exists; choose a fresh isolated destination')
        path=STORE/'index.json'
        if path.is_symlink():raise ValueError('Store index must not be a symlink')
        previous=path.read_bytes()if path.exists()else None
        merged=json.loads(previous)if previous is not None else{'version':1,'assets':{},'objects':{}}
        for section in ('assets','objects'):
            for key,value in index[section].items():
                if key in merged[section]and merged[section][key]!=value:raise ValueError('Conflicting existing cutout index entry: '+key)
                merged[section][key]=value
        validate_inputs()
        try:
            # mkdir reserves the exact new destination without replacing even
            # an empty directory created by another task since preflight.
            folder.mkdir(exist_ok=False);reserved=True
            for pixel_hash,record in index['objects'].items():
                target=STORE/'objects'/(pixel_hash+'.png')
                if record['file']!=str(target.relative_to(ROOT)):raise ValueError('Unexpected object publication path')
                if target.exists()or target.is_symlink():validate_object(target,pixel_hash,record['canvas'])
                else:
                    source=objects/(pixel_hash+'.png');validate_object(source,pixel_hash,record['canvas'])
                    target.parent.mkdir(parents=True,exist_ok=True)
                    try:os.link(source,target)
                    except FileExistsError:validate_object(target,pixel_hash,record['canvas'])
                    else:created.append(target)
            for child in staged.iterdir():
                if child.name!='import-receipt.json':child.rename(folder/child.name)
            index_attempted=True;save_index(merged)
            # Readers cannot observe a complete import before every referenced
            # object and the new index are available. Never replace a receipt.
            os.link(staged/'import-receipt.json',folder/'import-receipt.json')
        except BaseException:
            if index_attempted:restore_index_bytes(previous)
            if reserved:shutil.rmtree(folder)
            for target in reversed(created):target.unlink()
            raise
    return len(merged['objects'])


def stage_frames(job,guide_job,guide,records,pose_maps,canvas,root,manifest_folder,folder,objects,index,pin):
    bindings=[];nonempty={r:0 for r in ['BodyCostume','HeadHair','Weapon']}
    for record in records:
        direction=record['direction'];i=record['index'];source_i=pose_maps[direction][i]
        if 'source_pose_index'in record and (not isinstance(record['source_pose_index'],int)or isinstance(record['source_pose_index'],bool)or record['source_pose_index']!=source_i):raise ValueError('Uncertified source pose override')
        reference=guide['views'][direction]['frames'][source_i]
        master_path=(manifest_folder/record['master']).resolve()
        with Image.open(io.BytesIO(pin(master_path))) as image:
            if image.mode!='RGBA'or list(image.size)!=canvas:raise ValueError('Master must match the full canonical RGBA canvas')
            master=image.copy()
        parts={r:(manifest_folder/p).resolve()for r,p in record.get('parts',{}).items()}
        if 'labels'in record:
            targets={r:folder/'derived'/direction/r/f'{i:03d}.png'for r in BASE_ORDER}
            labels=(manifest_folder/record['labels']).resolve();pin(labels)
            import_frame(master_path,labels,targets);parts.update(targets)
        if any(r not in parts for r in ['BodyCostume','HeadHair','Weapon']):raise ValueError('Required actual visible parts are missing')
        combined=Image.new('RGBA',tuple(canvas))
        draw_order=visible_draw_order(parts,record.get('base_draw_order'))
        layer_order=authored_layer_order(parts,draw_order,record.get('layer_draw_order'))
        for role in draw_order:
            with Image.open(io.BytesIO(pin(parts[role]))) as image:
                if image.mode!='RGBA'or list(image.size)!=canvas:raise ValueError('Part must match the full canonical RGBA canvas')
                combined.alpha_composite(image)
        a=np.array(master);b=np.array(combined);visible=(a[:,:,3]>0)|(b[:,:,3]>0)
        if not np.array_equal(a[:,:,3],b[:,:,3])or not np.array_equal(a[visible],b[visible]):raise ValueError(f'Same-frame recomposition differs: {direction}/{i}')
        sockets=record.get('sockets',{})
        if sockets.get('root')!=root:raise ValueError('Canonical source root must be explicit and stable')
        for socket in ['head','hand_R','hand_L','back','waist']:
            value=sockets.get(socket,[])
            if not isinstance(value,list)or len(value)!=2 or any(isinstance(v,bool)or not isinstance(v,(int,float))or not math.isfinite(v)for v in value):raise ValueError('Invalid or missing finite socket '+socket)
        camera_id=digest(guide['views'][direction]['camera'])
        pose_id=digest({'guide_job':job['guide_job'],'source_sha256':guide_job['source_sha256'],'action':reference['action'],'frame':reference['source_frame'],'landmarks':reference['world_landmarks'],'rotations':reference['bone_rotations'],'transition':{k:reference[k]for k in ['transition_from','transition_frame','transition_weight']if k in reference},'retarget_to':guide_job.get('retarget_to')})
        bound={}
        for role,path in parts.items():
            if role not in ROLES:raise ValueError('Unexpected part '+role)
            with Image.open(io.BytesIO(pin(path))) as im:
                if role in nonempty and im.getbbox():nonempty[role]+=1
            metadata={'role':role,'canvas':canvas,'fit_id':job['fit_id'],'pose_id':pose_id,'camera_id':camera_id,'root':sockets['root'],'source_reference':str(master_path.relative_to(ROOT))if master_path.is_relative_to(ROOT)else str(master_path),'semantic_status':'IMPORTED_VISIBLE_CUTOUT_NOT_HIDDEN_ANATOMY','occlusion_reason':record.get('occlusion_reasons',{}).get(role)}
            bound[role]=register(path,metadata,index=index,staging_dir=objects)
        binding={'direction':direction,'index':i,'source_pose_index':source_i,'pose_id':pose_id,'camera_id':camera_id,'sockets':sockets,'base_draw_order':draw_order,'assets':bound}
        if layer_order is not None:binding['layer_draw_order']=layer_order
        bindings.append(binding)
    if any(n==0 for n in nonempty.values()):raise ValueError('A complete action cannot have an entirely empty required art slot')
    return bindings


def import_job(job_id,manifest_path):
    config=read(BASE/'factory.json');canvas=config['canvas']['authoring'];root=config['canvas'].get('authoring_root',[256,422.4])
    ledger=read(BASE/'ledger.json');job=ledger['paint_jobs'][job_id]
    if Path(job['id']).name!=job['id']or job['id']in('.','..'):raise ValueError('Invalid paint job directory')
    folder=BASE/'cutouts'/job['id']
    if folder.exists()or folder.is_symlink():raise ValueError('Cutout import target already exists; choose a fresh isolated destination')
    guide_job=ledger['guide_jobs'][job['guide_job']]
    if not receipt_valid(guide_job):raise ValueError('Matching complete source guide is missing')
    fingerprints={}
    def pin(path):
        path=path.resolve();data=path.read_bytes();value=hashlib.sha256(data).hexdigest()
        if path in fingerprints and fingerprints[path]!=value:raise ValueError('Input changed during cutout import: '+str(path))
        fingerprints[path]=value;return data
    manifest_path=manifest_path.resolve();manifest=json.loads(pin(manifest_path))
    if manifest.get('guide_job')!=job['guide_job']or manifest.get('fit_id')!=job['fit_id']:raise ValueError('Pose/fit identity does not match the paint job')
    expected={(d,i)for d in job['directions']for i in range(job['frame_count'])};records=manifest.get('frames',[])
    if not isinstance(records,list)or any(not isinstance(r,dict)or type(r.get('index'))is not int or not isinstance(r.get('direction'),str)for r in records):raise ValueError('Invalid pose record types')
    if len(records)!=len(expected)or{(r['direction'],r['index'])for r in records}!=expected:raise ValueError('Missing, duplicate or unexpected pose records')
    guide_path=BASE/'guides'/job['guide_job']/'manifest.json';guide=json.loads(pin(guide_path))
    pose_maps,pose_evidence=source_pose_maps(manifest,guide,guide_path,manifest_path.parent)
    def validate_inputs():
        for path,value in list(fingerprints.items()):
            if hashlib.sha256(path.read_bytes()).hexdigest()!=value:raise ValueError('Input changed during cutout import: '+str(path))
        if source_pose_maps(manifest,guide,guide_path,manifest_path.parent)!=(pose_maps,pose_evidence):raise ValueError('Pose recipe changed during cutout import')
    folder.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder.parent,prefix='.'+job['id']+'-intake-')as temporary:
        work=Path(temporary);staged=work/'import';staged.mkdir();objects=work/'objects'
        index={'version':1,'assets':{},'objects':{}}
        bindings=stage_frames(job,guide_job,guide,records,pose_maps,canvas,root,manifest_path.parent,staged,objects,index,pin)
        write(staged/'bindings.json',{'paint_job':job_id,'character':job['character'],'actions':job['actions'],'frames':bindings})
        write(staged/'import-receipt.json',{'paint_job':job_id,'guide_job':job['guide_job'],'input_manifest_sha256':fingerprints[manifest_path],'pose_recipe_evidence':pose_evidence,'all_frames_present':True,'frames':len(bindings),'recomposition_mismatches':0,'status':'IMPORTED_REQUIRES_VISUAL_REVIEW','owner_approved':False,'runtime_admitted':False,'hidden_surfaces_authored':False,'staged_import_revision':1})
        count=publish_staged_import(staged,folder,objects,index,validate_inputs)
    print(json.dumps({'paint_job':job_id,'imported_frames':len(bindings),'distinct_pixel_objects_in_store':count}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paint-job',required=True);p.add_argument('--manifest',type=Path,required=True);a=p.parse_args();import_job(a.paint_job,a.manifest.resolve())
