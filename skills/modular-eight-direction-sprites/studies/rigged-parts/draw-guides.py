"""Render guide-only and actual-frame overlays at one shared canvas scale."""
import json,os,runpy
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('SPRITE_OUTPUT_ROOT',str(HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'))).resolve()
compositor=runpy.run_path(str(HERE/'compose-proof.py'))
manifest=json.loads((OUT/'rig-manifest.json').read_text())
data=json.loads((OUT/'pose-guides.json').read_text());dest=OUT/'guides';dest.mkdir(exist_ok=True)
COLORS={'right':(75,160,255,255),'left':(255,151,64,255),'torso':(233,234,239,255),'weapon':(255,229,80,255),'contacts':(101,237,161,255)}
board=Image.new('RGB',(8*256,8*284),(27,32,40))
for pose in data['poses']:
 guide=Image.new('RGBA',(128,128));draw=ImageDraw.Draw(guide);p=pose['joints_native_px']
 chains=[('torso',['root','pelvis','chest','head']),('weapon',['grip','blade_tip'])]
 for side in ['right','left']:
  chains.extend([(side,[side+'.shoulder',side+'.elbow',side+'.wrist']),(side,[side+'.hip',side+'.knee',side+'.ankle']),(side,[side+'.heel',side+'.ankle',side+'.toe'])])
 for color,names in chains:
  draw.line([tuple(p[name]) for name in names],fill=COLORS[color],width=1)
  for name in names:
   x,y=p[name];draw.ellipse((x-1,y-1,x+1,y+1),fill=COLORS[color])
 for pair in [('right.shoulder','left.shoulder'),('right.hip','left.hip')]:draw.line([tuple(p[n]) for n in pair],fill=COLORS['torso'])
 for side,contact in pose['contacts'].items():
  names=['toe','heel'] if contact=='sole' else ['toe']
  for name in names:
   x,y=p[side+'.'+name];draw.rectangle((x-2,y+1,x+2,y+3),fill=COLORS['contacts'])
 # Hand orientation frame: short cross, kept separate from the limb chain.
 for axis,end in pose['right_hand_axes_px'].items():draw.line([tuple(p['right.wrist']),tuple(end)],fill=(190,210,255,180))
 directory=dest/pose['direction'];directory.mkdir(exist_ok=True)
 guide.save(directory/f"{pose['index']:02}-skeleton.png")
 actual=compositor['native'](compositor['compose'](manifest['default'],pose['direction'],pose['index'],packed=True))
 assert actual.size==(128,128),actual.size
 overlay=Image.alpha_composite(actual,guide);overlay.save(directory/f"{pose['index']:02}-overlay.png")
 preview=Image.new('RGBA',(128,128),(38,44,55,255));preview.alpha_composite(overlay)
 x=pose['index']*256;y=data['poses'].index(pose)//8*284
 board.paste(preview.convert('RGB').resize((256,256),Image.Resampling.NEAREST),(x,y+28))
 if pose['index']==7:compositor['CACHE'].clear()
 ImageDraw.Draw(board).text((x+5,y+5),f"{pose['direction']} / {pose['index']} / {pose['time_ms']}ms",fill='white')
board.save(OUT/'pose-guide-review.png')
print('DRAWN_GUIDES',len(data['poses']),'fixed shared 128px canvas')
