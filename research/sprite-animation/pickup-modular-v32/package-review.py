"""Format exported actual rig-render frames; analysis sheets/GIF, no art fixes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
import json,hashlib
P=Path(__file__).resolve().parent;frames=[Image.open(P/f'frames/{i:02}.png').convert('RGBA') for i in range(8)];poses=json.loads((P/'poses.json').read_text());sheet=Image.new('RGBA',(1536,1024));board=Image.new('RGB',(1536,1104),(32,42,56));d=ImageDraw.Draw(board);records=[]
for i,im in enumerate(frames):
 x=i%4*384;y=i//4*512;sheet.alpha_composite(im,(x,y));board.paste(im,(x,y+i//4*40+40),im)
 d.text((x+8,y+i//4*40+7),f"frame{i+1} / source{poses[i]['source_time_seconds']:.3f}s",fill='white')
 f=P/f'frames/{i:02}.png';records.append({'index':i,'path':str(f.relative_to(P.parents[2])),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'time_ms':poses[i]['source_time_seconds']*1000,'source_time_seconds':poses[i]['source_time_seconds'],'duration_ms':1300/7 if i<7 else 600})
sheet.save(P/'eight-frames.png');board.save(P/'eight-frame-review.png')
def gif(name,durations):
 rgb=[]
 for f in frames:
  im=f.resize((192,256),Image.Resampling.LANCZOS);b=Image.new('RGB',im.size,(32,42,56));b.paste(im,(0,0),im);rgb.append(b)
 rgb[0].save(P/name,save_all=True,append_images=rgb[1:],duration=durations,loop=0,disposal=2,optimize=False)
times=[round(p['source_time_seconds']*100)*10 for p in poses];native=[times[i+1]-times[i] for i in range(7)]+[600]
gif('pickup-source-clock.gif',native);gif('pickup-game-clock.gif',[100]*7+[600])
(P/'frames.json').write_text(json.dumps({'canvas':[384,512],'frames':records,'pose_source':'actual Canvas modular rig renders, no per-frame translation/scale/warp','source_active_ms':1300,'source_clock_gif_ms':native,'game_clock_gif_ms':[100]*7+[600],'game_clock_policy':'explicit uniform speed-up to700ms active action, same8poses/order, not source-native time','terminal_hold_ms':600,'original_RGBA_preserved':True},indent=2)+'\n')
print('BUNDLE_READY')
