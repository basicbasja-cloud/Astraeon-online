#!/usr/bin/env python3
"""Preserve decoded pose samples, source timestamps and one fixed shot crop.

Accept local GIF/APNG/video; source URL records provenance, never fetches it.
Windows select complete exposures by onset, without FPS resampling or centering.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageSequence

JOINTS = ['head','pelvis','right.shoulder','right.elbow','right.wrist','left.shoulder','left.elbow','left.wrist',
          'right.hip','right.knee','right.ankle','right.toe','left.hip','left.knee','left.ankle','left.toe','grip','blade_tip']


def extract(source, output, url, limit=2000, allow_untimed=False, start_ms=None, end_ms=None,
            crop=None, camera_motion='unknown'):
    source = source.resolve(); output = output.resolve()
    if output.exists(): raise ValueError('Output already exists; use a new study directory')
    if limit < 1: raise ValueError('Frame limit must be positive')
    if camera_motion not in ['unknown', 'fixed', 'moving']: raise ValueError('Invalid camera-motion declaration')
    start = Decimal(str(start_ms if start_ms is not None else 0))
    end = Decimal(str(end_ms)) if end_ms is not None else None
    if not start.is_finite() or start < 0 or (end is not None and (not end.is_finite() or end <= start)):
        raise ValueError('Window requires finite 0 <= start < end')
    if crop is not None and (len(crop) != 4 or any(type(v) is not int for v in crop) or
                             min(crop[:2]) < 0 or min(crop[2:]) < 1):
        raise ValueError('Crop requires integer x,y,width,height with positive dimensions')
    output.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='.reference-', dir=output.parent))
    try:
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        frames = []; clock = 0; source_canvas = None
        try: animated = Image.open(source)
        except OSError: animated = None
        if animated is not None:
            with animated:
                source_canvas = animated.size
                for source_index, frame in enumerate(ImageSequence.Iterator(animated)):
                    raw_duration = float(frame.info.get('duration', 0))
                    if raw_duration <= 0 and not allow_untimed:
                        raise ValueError('Frame duration missing/invalid; no silently invented FPS. Use --allow-untimed only for still-pose study.')
                    if (start_ms is not None or end_ms is not None) and (clock is None or raw_duration <= 0):
                        raise ValueError('A timed window requires known display durations')
                    selected = clock is None or (Decimal(str(clock)) >= start and (end is None or Decimal(str(clock)) < end))
                    if selected:
                        if len(frames) >= limit: raise ValueError('Reference exceeds --max-frames')
                        path = work/f'{len(frames):04}.png'; frame.convert('RGBA').save(path)
                        frames.append({'index':len(frames), 'source_index':source_index, 'file':path.name,
                                       'source_pts_ms':clock, 'duration_ms':raw_duration if raw_duration > 0 else None,
                                       'raw_duration_ms':raw_duration, 'timing':'container display duration' if raw_duration > 0 else 'unknown display duration'})
                    clock = clock + raw_duration if clock is not None and raw_duration > 0 else None
            kind = 'animated-image'; tools = {'Pillow':Image.__version__}
        else:
            for executable in ['ffmpeg','ffprobe']:
                if not shutil.which(executable): raise ValueError('Required video decoder missing: '+executable)
            metadata = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_streams','-of','json',str(source)]))
            records = metadata['frames']
            if not records: raise ValueError('Video empty')
            timestamps = [Decimal(r['best_effort_timestamp_time'])*1000 for r in records]
            if any(b <= a for a,b in zip(timestamps,timestamps[1:])): raise ValueError('Video timestamps must strictly increase')
            selected = [i for i,t in enumerate(timestamps) if t-timestamps[0] >= start and (end is None or t-timestamps[0] < end)]
            if not selected or len(selected) > limit: raise ValueError('Window empty or exceeds --max-frames')
            source_canvas = (int(metadata['streams'][0]['width']),int(metadata['streams'][0]['height']))
            # Select decoded ordinal, not an imprecise seek; preserve every duplicate and VFR exposure.
            filter_arg = f'select=between(n\\,{selected[0]}\\,{selected[-1]})'
            subprocess.run(['ffmpeg','-v','error','-noautorotate','-i',str(source),'-map','0:v:0','-vf',filter_arg,
                            '-fps_mode','passthrough','-start_number','0',str(work/'%04d.png')],check=True)
            for index, source_index in enumerate(selected):
                record = records[source_index]
                finish = timestamps[source_index+1] if source_index+1 < len(records) else timestamps[source_index]+Decimal(record.get('duration_time',record.get('pkt_duration_time','0')))*1000
                duration = finish-timestamps[source_index]
                if duration <= 0: raise ValueError('Last video frame duration unavailable; supply a better source container')
                frames.append({'index':index,'source_index':source_index,'file':f'{index:04}.png',
                               'source_pts_ms':float(timestamps[source_index]),'source_elapsed_ms':float(timestamps[source_index]-timestamps[0]),
                               'duration_ms':float(duration),'timing':'decoded PTS delta; source final frame uses reported duration'})
            kind = 'video'; tools = {t:subprocess.check_output([t,'-version'],text=True).splitlines()[0] for t in ['ffmpeg','ffprobe']}
        if not frames: raise ValueError('Window empty')
        if len(list(work.glob('[0-9]*.png'))) != len(frames): raise ValueError('Decoded frame count differs from source sample count')
        if crop and (crop[0]+crop[2] > source_canvas[0] or crop[1]+crop[3] > source_canvas[1]):
            raise ValueError('Fixed crop exceeds source canvas; no padding/clamping')
        first_pts = frames[0]['source_pts_ms']
        for f in frames:
            f['time_ms'] = f['source_pts_ms']-first_pts if f['source_pts_ms'] is not None and first_pts is not None else None
            path = work/f['file']
            with Image.open(path) as decoded:
                if decoded.size != tuple(source_canvas): raise ValueError('Variable canvas: requires explicit registration, no bbox fitting')
                if crop:
                    x,y,w,h = crop; decoded.crop((x,y,x+w,y+h)).save(path)
            f['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        size = tuple(crop[2:]) if crop else source_canvas
        scale = min(4,256/max(size)); display = (round(size[0]*scale),round(size[1]*scale)); cell = (display[0]+12,display[1]+34)
        # Every frame appears, at one common scale. Paginate to keep inspection readable.
        boards = []
        for offset in range(0,len(frames),72):
            page = frames[offset:offset+72]; columns = min(8,len(page))
            board = Image.new('RGB',(columns*cell[0],((len(page)+columns-1)//columns)*cell[1]),(35,40,49)); draw = ImageDraw.Draw(board)
            for j,f in enumerate(page):
                x = j%columns*cell[0]+6; y = j//columns*cell[1]+28
                with Image.open(work/f['file']) as decoded: rgba = decoded.convert('RGBA').resize(display,Image.Resampling.NEAREST)
                board.paste(rgba,(x,y),rgba)
                pts = f['source_pts_ms']; label = f'{pts:.3f}' if pts is not None else '?'
                draw.text((x,y-24),f"{f['index']} / src {f['source_index']}\nPTS {label}ms",fill='white')
            name = 'frames-review.png' if offset == 0 else f'frames-review-{offset//72+1:02}.png'
            board.save(work/name); boards.append(name)
        duration = frames[-1]['time_ms']+frames[-1]['duration_ms'] if frames[-1]['time_ms'] is not None and frames[-1]['duration_ms'] is not None else None
        report = {'schema':'timed-reference-capture-v2','source_url':url,'source_sha256':source_hash,'decoder':kind,'tools':tools,
                  'source_canvas':source_canvas,'canvas':size,'fixed_crop_xywh':crop,'source_xy_to_study_xy':{'subtract_xy':crop[:2] if crop else [0,0],'scale':1},
                  'requested_window_ms':[float(start),float(end) if end is not None else None],
                  'window_policy':'Select complete source exposures by onset in [start,end), relative to first source PTS; last exposure is not truncated',
                  'camera_motion':camera_motion,'camera_motion_evidence':'Operator declaration; not measured or compensated',
                  'frames':frames,'duration_ms':duration,'review_boards':boards,
                  'registration':'One fixed shot crop; no per-frame trim/center/scale; video autorotation disabled',
                  'scope':'External motion study only. No extracted character pixels enter original game exports. No inferred hidden joints.'}
        (work/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
        annotations = {'schema':'reference-landmark-observations-v1','source_sha256':source_hash,'anatomical_owner':'unverified',
                       'frames':[{'index':f['index'],'joints':{name:{'xy':None,'visibility':'unannotated','confidence':None} for name in JOINTS}} for f in frames],
                       'rules':'Study coordinates. Mark visible observations explicitly. Occluded joints stay unknown or separately marked estimates; never relabel a 2D estimate as source skeleton.'}
        (work/'landmarks-template.json').write_text(json.dumps(annotations,indent=2)+'\n')
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash: raise ValueError('Source changed during capture')
        os.rename(work,output); return report
    finally:
        if work.exists(): shutil.rmtree(work)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('--output',type=Path,required=True); p.add_argument('--source-url',required=True)
    p.add_argument('--max-frames',type=int,default=2000); p.add_argument('--allow-untimed',action='store_true')
    p.add_argument('--start-ms',type=float); p.add_argument('--end-ms',type=float)
    p.add_argument('--crop',type=int,nargs=4,metavar=('X','Y','WIDTH','HEIGHT')); p.add_argument('--camera-motion',choices=['unknown','fixed','moving'],default='unknown')
    args = p.parse_args()
    try:
        result = extract(args.source,args.output,args.source_url,args.max_frames,args.allow_untimed,args.start_ms,args.end_ms,args.crop,args.camera_motion)
        print(json.dumps({'output':str(args.output),'frames':len(result['frames']),'duration_ms':result['duration_ms'],'canvas':result['canvas']}))
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as exc: p.exit(2,'ERROR: '+str(exc)+'\n')
