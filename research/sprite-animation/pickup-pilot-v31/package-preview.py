"""Fixed-cell extraction/declared row-origin repair, never per-frame fitting."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math
P=Path(__file__).resolve().parent
raw=P/'attempt5-raw.png';im=Image.open(raw).convert('RGBA');assert im.size==(1536,1024)
out=P/'frames';out.mkdir(exist_ok=True);frames=[];source=json.loads((P/'source/source.json').read_text())
# One common authored-row-origin correction, calibrated neutral endpoints.
# It changes all lower-row cells equally, not individual foot/limb placement.
offsets=[0,32];records=[]
for i in range(8):
 x=i%4*384;y=i//4*512;crop=im.crop((x,y,x+384,y+512));dy=offsets[i//4];support=crop.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
 if support and support[3]+dy>512:raise ValueError('Foreground clipping by common row origin')
 frame=Image.new('RGBA',(384,512));frame.alpha_composite(crop,(0,dy));file=out/f'{i:02}.png';frame.save(file)
 frames.append(frame);records.append({'index':i,'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'source_time_seconds':source['frames'][i]['source_time_seconds'],'time_ms':source['frames'][i]['source_time_seconds']*1000,'duration_ms':source['source_duration_ms']/7 if i<7 else 600,'cell_origin_in_raw':[x,y],'authoring_row_translation_px':[0,dy]})
sheet=Image.new('RGBA',(1536,1024))
for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i%4*384,i//4*512))
sheet.save(P/'eight-frames.png')
board=Image.new('RGB',(1536,1104),(34,41,53));d=ImageDraw.Draw(board)
for i,(f,original) in enumerate(zip(records,frames)):
 x=i%4*384;y=i//4*552;board.paste(original,(x,y+40),original)
 for gx in range(0,384,32):d.line((x+gx,y+40,x+gx,y+552),fill=(54,65,78))
 for gy in range(0,512,32):d.line((x,y+40+gy,x+384,y+40+gy),fill=(54,65,78))
 d.text((x+8,y+7),f"frame{i+1} / {f['time_ms']:.2f}ms / REVIEW ONLY",fill='white')
board.save(P/'coordinate-review.png')
# GIF is a repeat-for-inspection of a one-shot, with authored terminal pause.
times=[round(r['time_ms']/10)*10 for r in records];durations=[times[i+1]-times[i] for i in range(7)]+[600]
def preview(images,file):
 rgb=[]
 for image in images:
  b=Image.new('RGB',image.size,(34,41,53));b.paste(image,(0,0),image);rgb.append(b)
 rgb[0].save(file,save_all=True,append_images=rgb[1:],duration=durations,loop=0,optimize=False,disposal=2)
preview([f.resize((192,256),Image.Resampling.LANCZOS) for f in frames],P/'pickup-review.gif')
preview([Image.open(f['path']).convert('RGBA').resize((192,256),Image.Resampling.LANCZOS) for f in source['frames']],P/'source-review.gif')
(P/'packing.json').write_text(json.dumps({'raw_file':str(raw),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'canvas':[384,512],'frames':records,'shared_scale':1,'row_origin_offsets':offsets,'row_origin_calibration_frames':[0,7],'row_origin_basis':'same-source-neutral endpoint placement; common32px lower-row translation, not inferred per-frame foot repair','per_frame_fit':False,'source_active_duration_ms':1300,'authored_terminal_hold_ms':600,'gif_durations_ms':durations,'gif_pts_quantization_ms':10,'loop':'repeat for inspection only; underlying action is one-shot','foreground_guard_alpha':128,'full_raw_preserved':True,'anatomy_pass':False,'contact_pass':False,'modular_parts_complete':False,'production_pass':False},indent=2)+'\n')
print(json.dumps({'frames':8,'gif_ms':sum(durations),'per_frame_fit':False}))
