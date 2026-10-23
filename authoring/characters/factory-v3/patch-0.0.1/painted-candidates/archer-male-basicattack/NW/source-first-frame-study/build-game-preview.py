from pathlib import Path
import sys,json,shutil
from PIL import Image,ImageDraw
sys.path.insert(0,'tools/character_factory_v3');from build_fixed_grid_sequence_review import gif
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'painted-candidates/archer-male-basicattack/NW/source-first-frame-study';seq=p/'sequence';source=json.load(open(b/'research/archer-contact-motion-audit.json'))['preview_durations_ms'];durations=[max(10,round(d/sum(source)*100)*10)for d in source];durations[-1]+=1000-sum(durations)
receipt={'status':'PROPOSED_RPG_RETIMING_PREVIEW_NOT_RUNTIME_METADATA','normal_duration_ms':sum(durations),'durations_ms':durations,'source_durations_ms':source,'source_release_frame':10,'release_time_ms':sum(durations[:10]),'sampling_unchanged':True,'pose_interpolation':False,'runtime_admitted':False};(p/'proposed-game-preview-timing.json').write_text(json.dumps(receipt,indent=2)+'\n')
for name,size,folder in [('detail',768,'detail'),('game-scale',240,'runtime')]:
 frames=[Image.open(seq/folder/f'{i:03d}.png').convert('RGBA')for i in range(16)];gif(frames,p/(name+'-normal.gif'),durations);gif(frames,p/(name+'-slow.gif'),[d*3 for d in durations]);frames[0].save(p/(name+'-lossless.webp'),save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True)
from build_fixed_grid_sequence_review import frames_from_sheet
old=p/'previous-strip';frames_from_sheet(b/'painted-candidates/archer-male-basicattack/NW/current-guide-rear-locked/master-sheet.png',old/'detail',768);comparison=[]
for i in range(16):
 frame=Image.new('RGBA',(960,520),'#e8e8e8');d=ImageDraw.Draw(frame);d.text((10,10),f'Frame{i}: old strip / source-first redraw (same viewport, no per-frame fitting)',fill='black')
 for x,path in [(0,old/'detail'/f'{i:03d}.png'),(480,seq/'detail'/f'{i:03d}.png')]:frame.alpha_composite(Image.open(path).resize((480,480)),(x,40))
 comparison.append(frame)
gif(comparison,p/'before-after-normal.gif',durations)

print(json.dumps(receipt))
