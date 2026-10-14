"""Preserve every actually decoded external CMU preview frame and container PTS.
No generated character video, interpolation, time warp or AMC synchronization.
"""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;movie=P/'reference/26_09.mpg';out=P/'reference/video-frames';out.mkdir(exist_ok=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pts_time,pkt_dts_time,duration_time,pkt_duration_time,key_frame,pict_type','-of','json',str(movie)],text=True))
subprocess.run(['ffmpeg','-y','-v','error','-i',str(movie),'-fps_mode','passthrough','-start_number','0',str(out/'%04d.png')],check=True)
files=sorted(out.glob('*.png'));frames=probe['frames'];assert len(files)==len(frames),(len(files),len(frames));records=[]
for i,(path,frame) in enumerate(zip(files,frames)):
 im=Image.open(path).convert('RGBA');records.append(dict(index=i,path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),width=im.width,height=im.height,container_pts_seconds=float(frame['pts_time']) if 'pts_time' in frame else None,decoder_best_effort_seconds=float(frame['best_effort_timestamp_time']) if 'best_effort_timestamp_time' in frame else None,packet_dts_seconds=float(frame['pkt_dts_time']) if 'pkt_dts_time' in frame else None,frame_duration_seconds=float(frame.get('duration_time',frame.get('pkt_duration_time'))) if 'duration_time' in frame or 'pkt_duration_time' in frame else None,clock_status='DIRECT_PTS' if 'pts_time' in frame else 'DECODER_BEST_EFFORT' if 'best_effort_timestamp_time' in frame else 'UNKNOWN',picture_type=frame.get('pict_type')))
pts=[f['decoder_best_effort_seconds'] for f in records];known=[t for t in pts if t is not None];assert all(b>a for a,b in zip(known,known[1:]));receipt=dict(kind='Actual external CMU26_09 source video decode, NOT generated character video',source_movie_sha256=hashlib.sha256(movie.read_bytes()).hexdigest(),decoded_frame_count=len(records),source_clock='Raw PTS, decoder best_effort and DTS distinguished. Missing clocks stay null; no mean-FPS replacement or interpolation.',unknown_clock_frames=[f['index'] for f in records if f['clock_status']=='UNKNOWN'],source_amc_alignment='UNVERIFIED;120HzAMC and this video preview do not have established common clock/offset',frames=records,production_pass=False)
(P/'reference/video-frame-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
ids=[round(i*(len(files)-1)/15) for i in range(16)];sheet=Image.new('RGB',(1408,1040),(28,36,44));draw=ImageDraw.Draw(sheet)
for j,i in enumerate(ids):
 x=j%4*352;y=j//4*260;sheet.paste(Image.open(files[i]).convert('RGB'),(x,y+20));stamp=f'{pts[i]:.6f}s' if pts[i] is not None else 'UNKNOWN';draw.text((x+4,y+4),f'DECODED {i} / clock {stamp}',fill='white')
sheet.save(P/'reference/video-native-pts-sheet.png');print(len(records),'actual external video frames; no invented synchronization')
