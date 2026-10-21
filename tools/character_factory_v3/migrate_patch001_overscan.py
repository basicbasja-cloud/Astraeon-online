"""Add uniform capture padding while preserving source projection and scale.

Unclipped RGBA captures can be padded losslessly. Any old view touching an edge
requires a fresh Blender capture; pixels outside the old image are never invented.
"""
import argparse,copy,hashlib,json,math
from pathlib import Path
from PIL import Image
from patch001_factory import BASE,read,write,plan,status,receipt_valid,digest


def signature(job):
    return digest({k:v for k,v in job.items()if k not in ['id','uses','directions','resolution','ortho_scale','camera_up_offset']})


def migrate():
    config=read(BASE/'factory.json')
    if config['canvas']['source_guide']==[1024,1024]:
        old=read(BASE/'ledger.json')
        if not all(receipt_valid(j)for j in old['guide_jobs'].values()):raise ValueError('Finish the current source capture pass before migrating')
        write(BASE/'research/pre-overscan-ledger.json',old)
        config['canvas'].update({'authoring':[768,768],'authoring_root':[384,550.4],'source_guide':[1536,1536],'runtime':[240,240],'runtime_root':[120,172],'uniform_runtime_scale':.3125,'overscan_policy':'Add 256 source pixels / 128 authoring pixels / 40 runtime pixels per side; preserve pixels-per-meter and world camera position. No pose-wise crop or resizing.'})
        config['camera']={'ortho_scale':5.325,'up_offset':1.15375,'projection_pixels_per_meter':1536/5.325,'locked_across_actions':True}
        write(BASE/'factory.json',config)
    elif config['canvas']['source_guide']==[1536,1536]:old=read(BASE/'research/pre-overscan-ledger.json')
    else:raise ValueError('Unsupported source configuration')
    new=plan();lookup={signature(j):j for j in old['guide_jobs'].values()};results=[]
    for job in new['guide_jobs'].values():
        previous=lookup.get(signature(job))
        if not previous:raise ValueError('No equivalent source job for '+job['id'])
        if receipt_valid(job):
            results.append({'old_job':previous['id'],'new_job':job['id'],'status':'EXISTING_COMPLETE_OVERSCAN_CAPTURE'});continue
        if job['directions']!=previous['directions']:raise ValueError('Source camera directions changed')
        ratio=job['resolution']/previous['resolution']
        if abs(job['ortho_scale']/previous['ortho_scale']-ratio)>1e-9:raise ValueError('Projection scale changed')
        if abs(job['camera_up_offset']-previous.get('camera_up_offset',.325*previous['ortho_scale']))>1e-9:raise ValueError('World camera offset changed')
        pad=(job['resolution']-previous['resolution'])//2
        if pad*2+previous['resolution']!=job['resolution']:raise ValueError('Non-integer padding')
        source=BASE/'guides'/previous['id'];edge_frames=[]
        for d in previous['directions']:
            for i in range(previous['frames']):
                image=Image.open(source/d/f'{i:03d}.png');alpha=image.getchannel('A');w,h=image.size
                if any(alpha.crop(box).getbbox()for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]):edge_frames.append([d,i])
        if edge_frames:
            results.append({'old_job':previous['id'],'new_job':job['id'],'status':'FRESH_BLENDER_CAPTURE_REQUIRED','edge_frames':edge_frames});continue
        target=BASE/'guides'/job['id'];target.mkdir(parents=True,exist_ok=True);manifest=copy.deepcopy(read(source/'manifest.json'))
        for d,view in manifest['views'].items():
            (target/d).mkdir(exist_ok=True);view['camera']['ortho_scale']=job['ortho_scale'];contact=Image.new('RGB',(1024,256*math.ceil(job['frames']/4)),'white')
            for i,frame in enumerate(view['frames']):
                image=Image.open(source/d/f'{i:03d}.png').convert('RGBA');padded=Image.new('RGBA',(job['resolution'],job['resolution']));padded.paste(image,(pad,pad));padded.save(target/d/f'{i:03d}.png',compress_level=1)
                frame['landmarks']={n:[round(v+pad,4)for v in point]for n,point in frame['landmarks'].items()}
                frame['weapon_guide']={n:[round(v+pad,4)for v in point]if isinstance(point,list)else point for n,point in frame['weapon_guide'].items()}
                thumb=padded.resize((256,256),Image.Resampling.LANCZOS);bg=Image.new('RGBA',(256,256),'white');bg.alpha_composite(thumb);contact.paste(bg.convert('RGB'),(i%4*256,i//4*256))
            contact.save(target/d/'contact.png')
        manifest['job']=job;manifest['overscan_migration']={'source_job':previous['id'],'source_manifest_sha256':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),'operation':'lossless constant transparent padding; no resampling of source captures','pad_px_per_side':pad,'all_old_frames_clear_of_edges':True,'camera_world_position_unchanged':True,'pixels_per_meter_unchanged':True}
        write(target/'manifest.json',manifest)
        if not receipt_valid(job):raise ValueError('Incomplete migrated capture '+job['id'])
        results.append({'old_job':previous['id'],'new_job':job['id'],'status':'LOSSLESS_OVERSCAN_MIGRATED'})
        print(json.dumps(results[-1]),flush=True)
    write(BASE/'research/overscan-migration-receipt.json',{'status':'CAPTURE_PADDING_ONLY_NOT_ART_APPROVAL','jobs':results,'source_pixel_padding':256,'authoring_pixel_padding':128,'runtime_pixel_padding':40,'visible_source_pixels_resized':False})
    print(json.dumps(status(new),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args();migrate()
