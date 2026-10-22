"""Reuse completed source captures only when pose/render geometry matches exactly."""
import argparse,json,hashlib,shutil
from pathlib import Path
from patch001_factory import BASE,read,write,receipt_valid


def geometry_signature(job):
    ignored={'id','directions','uses','floor_contact_preview'}
    return {k:v for k,v in job.items()if k not in ignored}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--job',type=Path,required=True);a=p.parse_args();job=read(a.job);source=read(a.source/'manifest.json')
    if source['frame_count']!=job['frames']:raise ValueError('Frame counts differ')
    implementations=source.get('implementation_digests_at_process_start',{})
    if not implementations:raise ValueError('Source capture lacks implementation provenance')
    for name,expected in implementations.items():
        path=Path(__file__).with_name(name)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Capture implementation differs: '+name)
    # floor_contact_preview creates a separate evidence image, never changes PNG poses.
    if geometry_signature(source['job'])!=geometry_signature(job):raise ValueError('Pose/render configuration differs')
    for direction in job['directions']:
        if len(source['views'].get(direction,{}).get('frames',[]))!=job['frames']:raise ValueError('Missing required source view')
        for i in range(job['frames']):
            if not(a.source/direction/f'{i:03d}.png').is_file():raise ValueError('Missing source pose')
    target=BASE/'guides'/job['id']
    if target.resolve()==a.source.resolve():raise ValueError('Cannot adopt into source directory')
    if target.exists()and any(target.iterdir()):raise ValueError('Refuse to replace a nonempty capture directory')
    target.mkdir(parents=True,exist_ok=True)
    for direction in job['directions']:
        d=target/direction;d.mkdir()
        for i in range(job['frames']):shutil.copy2(a.source/direction/f'{i:03d}.png',d/f'{i:03d}.png')
        if(a.source/direction/'contact.png').is_file():shutil.copy2(a.source/direction/'contact.png',d/'contact.png')
    source['capture_reuse']={'parent_manifest_sha256':hashlib.sha256((a.source/'manifest.json').read_bytes()).hexdigest(),'parent_job':source['job']['id'],'source_directory':str(a.source),'same_pose_and_render_configuration':True,'pixels_changed':False}
    source['job']=job;source['views']={d:source['views'][d]for d in job['directions']};write(target/'manifest.json',source)
    if not receipt_valid(job):raise ValueError('Adopted capture failed the standard artifact receipt check')
    print(json.dumps({'adopted_job':job['id'],'source':str(a.source),'frames':job['frames']*len(job['directions']),'pixels_changed':False}))

if __name__=='__main__':main()
