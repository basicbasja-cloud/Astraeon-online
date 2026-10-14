"""Format actual exported frames; no redraw, anchor fitting or motion invention."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
poses=json.loads((P/'poses.json').read_text());times=[round(p['source_time_seconds']*100)*10 for p in poses];clocks={'game':[100]*7+[600],'source':[times[i+1]-times[i] for i in range(7)]+[600]};records={}
allboard=Image.new('RGB',(1536,1536),(29,41,53))
for si,style in enumerate(['original','silver','bald']):
 frames=[Image.open(P/f'frames/{style}/{i:02}.png').convert('RGBA') for i in range(8)];records[style]=[];board=Image.new('RGB',(1536,1104),(29,41,53));d=ImageDraw.Draw(board)
 for i,f in enumerate(frames):
  x=i%4*384;y=i//4*552;board.paste(f,(x,y+40),f);d.text((x+8,y+8),f'{style} / {i+1} / {poses[i]["source_time_seconds"]:.3f}s',fill='white')
  small=f.resize((192,256),Image.Resampling.LANCZOS);allboard.paste(small,(i*192,si*512+30),small)
  file=P/f'frames/{style}/{i:02}.png';records[style].append(dict(index=i,path=str(file.relative_to(ROOT)),sha256=sha(file),source_time_seconds=poses[i]['source_time_seconds'],time_ms=poses[i]['source_time_seconds']*1000,duration_ms=1300/7 if i<7 else 600))
 board.save(P/(style+'-eight-frames.png'))
 for clock,durations in clocks.items():
  rgb=[]
  for f in frames:
   small=f.resize((192,256),Image.Resampling.LANCZOS);bg=Image.new('RGB',small.size,(29,41,53));bg.paste(small,(0,0),small);rgb.append(bg)
  rgb[0].save(P/f'{style}-{clock}-clock.gif',save_all=True,append_images=rgb[1:],duration=durations,loop=0,disposal=2,optimize=False)
allboard=allboard.crop((0,0,1536,1310));allboard.save(P/'appearance-review.png')
compare=[]
for i in range(8):
 b=Image.new('RGB',(768,552),(29,41,53));d=ImageDraw.Draw(b);d.text((8,8),'Original view A / unchanged v32',fill='white');d.text((392,8),'Physical view B / new drawing',fill='white')
 for x,file in [(0,P.parent/f'pickup-modular-v32/frames/{i:02}.png'),(384,P/f'frames/original/{i:02}.png')]:
  f=Image.open(file).convert('RGBA');b.paste(f,(x,40),f)
 compare.append(b.resize((576,414),Image.Resampling.LANCZOS))
compare[0].save(P/'two-view-compare.gif',save_all=True,append_images=compare[1:],duration=clocks['game'],loop=0,disposal=2,optimize=False)
(P/'frames.json').write_text(json.dumps(dict(canvas=[384,512],styles=records,clocks=clocks,loop=False,preview_replays_after_terminal_hold=True,terminal_hold_ms=600,provider_video=False,per_frame_fitting=False),indent=2)+'\n')
print('PACKAGED_24_REAL_FRAMES')
