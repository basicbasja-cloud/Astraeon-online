#!/usr/bin/env python3
"""Lossless frame-by-frame study extraction; no auto-centering or skeleton guess.

Accept GIF/APNG or a local video. Preserve canvas and display time; retain every
sample, including duplicates. Source URL is provenance, not an automatic fetch.
"""
import argparse
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
from PIL import Image,ImageDraw,ImageSequence

JOINTS=['head','pelvis','right.shoulder','right.elbow','right.wrist','left.shoulder','left.elbow','left.wrist',
        'right.hip','right.knee','right.ankle','right.toe','left.hip','left.knee','left.ankle','left.toe','grip','blade_tip']


def extract(source,output,url,limit=2000,allow_untimed=False):
    source=source.resolve();output=output.resolve()
    if output.exists():raise ValueError('Output already exists; use a new study directory')
    output.parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='.reference-',dir=output.parent))
    try:
        frames=[];clock=0
        try:
            image=Image.open(source)
        except Exception:
            image=None
        if image is not None:
            with image:
                for index,frame in enumerate(ImageSequence.Iterator(image)):
                    if index>=limit:raise ValueError('Reference exceeds --max-frames')
                    duration=float(frame.info.get('duration',0))
                    if duration<=0 and not allow_untimed:raise ValueError('Frame duration missing/invalid; no silently invented FPS. Use --allow-untimed only for still-pose study.')
                    path=work/f'{index:04}.png';frame.convert('RGBA').save(path)
                    frames.append({'index':index,'file':path.name,'time_ms':clock,'duration_ms':duration if duration>0 else None,'raw_duration_ms':duration,'timing':'container display duration' if duration>0 else 'unknown display duration'})
                    clock=clock+duration if clock is not None and duration>0 else None
            kind='animated-image'
        else:
            for executable in ['ffmpeg','ffprobe']:
                if not shutil.which(executable):raise ValueError('Required video decoder missing: '+executable)
            metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_streams','-of','json',str(source)]))
            records=metadata['frames']
            if not records or len(records)>limit:raise ValueError('Video empty or exceeds --max-frames')
            timestamps=[float(r['best_effort_timestamp_time'])*1000 for r in records]
            if any(b<=a for a,b in zip(timestamps,timestamps[1:])):raise ValueError('Video timestamps must strictly increase')
            subprocess.run(['ffmpeg','-v','error','-i',str(source),'-map','0:v:0','-fps_mode','passthrough','-start_number','0',str(work/'%04d.png')],check=True)
            for index,record in enumerate(records):
                end=timestamps[index+1] if index+1<len(records) else timestamps[index]+float(record.get('duration_time',record.get('pkt_duration_time','0')))*1000
                duration=end-timestamps[index]
                if duration<=0:raise ValueError('Last video frame duration unavailable; supply a better source container')
                frames.append({'index':index,'file':f'{index:04}.png','time_ms':timestamps[index]-timestamps[0],'duration_ms':duration,'timing':'decoded presentation timestamps; final frame uses reported duration'})
            clock=frames[-1]['time_ms']+frames[-1]['duration_ms'];kind='video'
        with Image.open(work/frames[0]['file']) as first:size=first.size
        for f in frames:
            with Image.open(work/f['file']) as decoded:
                if decoded.size!=size:raise ValueError('Variable canvas: requires explicit registration, no bbox fitting')
        # Same display scale and same top-left origin for all frames; source PNGs remain untouched.
        scale=min(4,256/max(size));display=(round(size[0]*scale),round(size[1]*scale));cell=(display[0]+12,display[1]+34);columns=min(9,len(frames))
        board=Image.new('RGB',(columns*cell[0],((len(frames)+columns-1)//columns)*cell[1]),(35,40,49));draw=ImageDraw.Draw(board)
        for f in frames:
            path=work/f['file'];f['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            x=f['index']%columns*cell[0]+6;y=f['index']//columns*cell[1]+28
            with Image.open(path) as decoded:rgba=decoded.convert('RGBA').resize(display,Image.Resampling.NEAREST)
            board.paste(rgba,(x,y),rgba);draw.text((x,y-24),f"{f['index']} | {f['time_ms'] if f['time_ms'] is not None else '?'}ms\n{f['duration_ms'] if f['duration_ms'] is not None else '?'}ms",fill='white')
        board.save(work/'frames-review.png')
        report={'schema':'timed-reference-capture-v1','source_url':url,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                'decoder':kind,'canvas':size,'frames':frames,'duration_ms':clock,'registration':'Fixed source canvas, no per-frame trim/center/scale',
                'scope':'External motion study only. No extracted character pixels enter original game exports. No inferred hidden joints.'}
        (work/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
        annotations={'schema':'reference-landmark-observations-v1','source_sha256':report['source_sha256'],'anatomical_owner':'unverified',
                     'frames':[{'index':f['index'],'joints':{name:{'xy':None,'visibility':'unannotated','confidence':None} for name in JOINTS}} for f in frames],
                     'rules':'Mark visible observations explicitly. Occluded joints stay unknown or are separately marked estimates; never relabel a 2D estimate as source skeleton.'}
        (work/'landmarks-template.json').write_text(json.dumps(annotations,indent=2)+'\n')
        os.rename(work,output)
        return report
    finally:
        if work.exists():shutil.rmtree(work)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-url',required=True);p.add_argument('--max-frames',type=int,default=2000);p.add_argument('--allow-untimed',action='store_true',help='Retain samples with unknown display durations for pose study; never invent an FPS')
    args=p.parse_args()
    try:
        result=extract(args.source,args.output,args.source_url,args.max_frames,args.allow_untimed)
        print(json.dumps({'output':str(args.output),'frames':len(result['frames']),'duration_ms':result['duration_ms'],'canvas':result['canvas']}))
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as exc:p.exit(2,'ERROR: '+str(exc)+'\n')
