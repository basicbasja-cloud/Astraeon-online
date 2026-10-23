from PIL import Image
from pathlib import Path
import sys,json
sys.path.insert(0,'tools/character_factory_v3');from build_fixed_grid_sequence_review import gif
s=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study');p=s/'tight-viewport-action-study';out=p/'sequence-review';out.mkdir(exist_ok=True);frames=[];pair=[];records=[]
timing=json.loads((s/'proposed-game-preview-timing.json').read_text())['durations_ms']
for i in range(16):
 d=p/f'batch-{i//4:02}';f=Image.open(d/'frames'/f'{i:03}.png').convert('RGBA');g=Image.open(d/f'guide-{i:03}.png').convert('RGBA');frames.append(f)
 c=Image.new('RGBA',(1536,768),'white');c.alpha_composite(g,(0,0));c.alpha_composite(f,(768,0));pair.append(c.resize((768,384)))
 records.append({'frame':i,'source_pose_index':i,'paint':str(d/'frames'/f'{i:03}.png'),'source':str(d/f'guide-{i:03}.png')})
small=[]
for index,f in enumerate(frames):
 master=Image.new('RGBA',(768,768));master.alpha_composite(f.convert('RGBa').resize((390,390),Image.Resampling.LANCZOS).convert('RGBA'),(189,227));small.append(master.resize((240,240),Image.Resampling.LANCZOS));(out/'Master').mkdir(exist_ok=True);master.save(out/'Master'/f'{index:03d}.png');gif(small,out/'normal.gif',timing);gif(small,out/'slow.gif',[t*3 for t in timing]);gif(pair,out/'source-vs-paint.gif',[t*3 for t in timing]);contact=Image.new('RGBA',(1536,1536),'#e8e8e8')
for i,f in enumerate(frames):contact.alpha_composite(f.resize((384,384)),((i%4)*384,(i//4)*384))
contact.save(out/'contact.png');(out/'receipt.json').write_text(json.dumps({'status':'FULL_ACTION_REPAINT_STUDY_NOT_ACCEPTED','frames':records,'timing':'Preview only, existing proposal retained; no runtime admission','source_pose_holds_applied':False,'per_frame_figure_fit':False,'known_failures':['Lower-row source framing differs in some batches.','Grip, nock, source component positions and loop seam need review.'],'runtime_admitted':False},indent=2)+'\n')
