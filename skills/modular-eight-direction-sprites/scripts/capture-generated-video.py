#!/usr/bin/env python3
"""Capture every presented AI-video frame at native PTS, without FPS conversion.

A generated video is a motion proposal, never a recovered authoritative rig.
"""
import argparse,importlib.util,json,subprocess,hashlib
from pathlib import Path

spec=importlib.util.spec_from_file_location('native_capture',Path(__file__).with_name('capture-reference.py'))
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

def capture(source,output,source_url,provider=None,job_id=None,start_ms=None,end_ms=None,max_frames=900,origin='generated_candidate'):
    source=Path(source).resolve();output=Path(output).resolve()
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]))
    formats=set(info['format']['format_name'].split(','))
    if not formats.intersection({'mov','mp4','matroska','webm','avi','mpeg'}):
        raise ValueError('Requires an actual video container, not a sprite sheet/GIF renamed as video')
    if not any(s.get('codec_type')=='video' for s in info['streams']):raise ValueError('No decoded video stream')
    result=native.extract(source,output,source_url,limit=max_frames,start_ms=start_ms,end_ms=end_ms,camera_motion='unknown')
    if result['decoder']!='video':raise ValueError('Actual video decoder required')
    result.update(source_origin=origin,provider=provider,provider_job_id=job_id,
        camera_request='fixed camera requested; actual camera motion not yet measured',
        motion_review='pending',anatomy_review='pending',production_pass=False,
        old_rig_used_by_capture=False,generation_conditioning="unverified_until_provider_receipt",rig_ground_truth=False,
        scope='Every decoded source-video frame and native exposure clock. AI video pixels are a motion proposal; no hidden bones, grip correctness, motion acceptance or production approval inferred.')
    (output/'capture.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-url',required=True);p.add_argument('--provider');p.add_argument('--job-id');p.add_argument('--start-ms',type=float);p.add_argument('--end-ms',type=float);p.add_argument('--max-frames',type=int,default=900);a=p.parse_args()
    r=capture(a.source,a.output,a.source_url,a.provider,a.job_id,a.start_ms,a.end_ms,a.max_frames)
    print(json.dumps({'output':str(a.output),'decoded_frames':len(r['frames']),'native_duration_ms':r['duration_ms'],'motion_review':r['motion_review'],'production_pass':False}))
if __name__=='__main__':main()
