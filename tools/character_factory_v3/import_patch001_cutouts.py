"""Import complete same-frame cutouts without fabricating missing coverage.

An input manifest has guide_job, fit_id and frames. Each frame specifies direction,
index, master, parts (paths for real visible layers) and sockets. Labels may be
provided instead of the five base part files. Effects remain separate images.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from patch001_factory import BASE,ROOT,read,write,receipt_valid,digest
from cutout_asset_store import STORE,ROLES,register,save_index,import_frame
from register_clear_paint_candidate import validated_pose_map,resolved_recipe

BASE_ORDER=['BackAccessory','BodyCostume','HeadHair','Weapon','WeaponHandOccluder','Headgear']

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


def import_job(job_id,manifest_path):
    config=read(BASE/'factory.json');canvas=config['canvas']['authoring'];root=config['canvas'].get('authoring_root',[256,422.4])
    ledger=read(BASE/'ledger.json');job=ledger['paint_jobs'][job_id];guide_job=ledger['guide_jobs'][job['guide_job']]
    if not receipt_valid(guide_job):raise ValueError('Matching complete source guide is missing')
    manifest=read(manifest_path)
    if manifest.get('guide_job')!=job['guide_job']or manifest.get('fit_id')!=job['fit_id']:raise ValueError('Pose/fit identity does not match the paint job')
    expected={(d,i)for d in job['directions']for i in range(job['frame_count'])};records=manifest.get('frames',[])
    if len(records)!=len(expected)or{(r['direction'],r['index'])for r in records}!=expected:raise ValueError('Missing, duplicate or unexpected pose records')
    guide_path=BASE/'guides'/job['guide_job']/'manifest.json';guide=read(guide_path)
    pose_maps,pose_evidence=source_pose_maps(manifest,guide,guide_path,manifest_path.parent)
    folder=BASE/'cutouts'/job_id;folder.mkdir(parents=True,exist_ok=True)
    index=read(STORE/'index.json')if(STORE/'index.json').exists()else{'version':1,'assets':{},'objects':{}}
    bindings=[];nonempty={r:0 for r in ['BodyCostume','HeadHair','Weapon']}
    for record in records:
        direction=record['direction'];i=record['index'];source_i=pose_maps[direction][i]
        if 'source_pose_index'in record and (not isinstance(record['source_pose_index'],int)or isinstance(record['source_pose_index'],bool)or record['source_pose_index']!=source_i):raise ValueError('Uncertified source pose override')
        reference=guide['views'][direction]['frames'][source_i]
        master_path=(manifest_path.parent/record['master']).resolve();master=Image.open(master_path)
        if master.mode!='RGBA'or list(master.size)!=canvas:raise ValueError('Master must match the full canonical RGBA canvas')
        parts={r:(manifest_path.parent/p).resolve()for r,p in record.get('parts',{}).items()}
        if 'labels'in record:
            targets={r:folder/'derived'/direction/r/f'{i:03d}.png'for r in BASE_ORDER}
            import_frame(master_path,(manifest_path.parent/record['labels']).resolve(),targets);parts.update(targets)
        if any(r not in parts for r in ['BodyCostume','HeadHair','Weapon']):raise ValueError('Required actual visible parts are missing')
        combined=Image.new('RGBA',tuple(canvas))
        draw_order=visible_draw_order(parts,record.get('base_draw_order'))
        layer_order=authored_layer_order(parts,draw_order,record.get('layer_draw_order'))
        for role in draw_order:combined.alpha_composite(Image.open(parts[role]).convert('RGBA'))
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
            im=Image.open(path)
            if role in nonempty and im.getbbox():nonempty[role]+=1
            metadata={'role':role,'canvas':canvas,'fit_id':job['fit_id'],'pose_id':pose_id,'camera_id':camera_id,'root':sockets['root'],'source_reference':str(master_path.relative_to(ROOT))if master_path.is_relative_to(ROOT)else str(master_path),'semantic_status':'IMPORTED_VISIBLE_CUTOUT_NOT_HIDDEN_ANATOMY','occlusion_reason':record.get('occlusion_reasons',{}).get(role)}
            bound[role]=register(path,metadata,index=index)
        binding={'direction':direction,'index':i,'source_pose_index':source_i,'pose_id':pose_id,'camera_id':camera_id,'sockets':sockets,'base_draw_order':draw_order,'assets':bound}
        if layer_order is not None:binding['layer_draw_order']=layer_order
        bindings.append(binding)
    if any(n==0 for n in nonempty.values()):raise ValueError('A complete action cannot have an entirely empty required art slot')
    save_index(index);write(folder/'bindings.json',{'paint_job':job_id,'character':job['character'],'actions':job['actions'],'frames':bindings})
    write(folder/'import-receipt.json',{'paint_job':job_id,'guide_job':job['guide_job'],'input_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'pose_recipe_evidence':pose_evidence,'all_frames_present':True,'frames':len(bindings),'recomposition_mismatches':0,'status':'IMPORTED_REQUIRES_VISUAL_REVIEW','owner_approved':False,'runtime_admitted':False,'hidden_surfaces_authored':False})
    print(json.dumps({'paint_job':job_id,'imported_frames':len(bindings),'distinct_pixel_objects_in_store':len(index['objects'])}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paint-job',required=True);p.add_argument('--manifest',type=Path,required=True);a=p.parse_args();import_job(a.paint_job,a.manifest.resolve())
