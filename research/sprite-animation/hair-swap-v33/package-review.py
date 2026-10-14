"""Format actual browser frames and bind every counterfactual head pass."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OLD=P.parent/'pickup-modular-v32'
def bound(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
clock=json.loads((OLD/'frames.json').read_text());styles=['original','silver','auburn','bald'];case={'canvas':[384,512],'styles':{},'baseline_frames':clock['frames'],'poses':bound(P/'poses.json'),'baseline_poses':bound(OLD/'poses.json'),'head_previews':{s:bound(P/('head-'+s+'.png')) for s in styles},'protected_eye_roi':[133,240,167,256],'scope':'Same original v32 body/poses/clock; generated separate head/front/rear hair, one fixed camera.'}
case.update(bindings=bound(P/'bindings.json'),baseline_bindings=bound(OLD/'rig-bind-review.json'),registration=bound(P/'registration.json'),parts=bound(P/'parts.json'))
for style in styles:
 arr=[Image.open(P/'frames'/style/f'{i:02}.png').convert('RGBA') for i in range(8)];case['styles'][style]=[{'index':i,**bound(P/'frames'/style/f'{i:02}.png'),'head_pass':bound(P/'head-masks'/style/f'{i:02}.png'),'source_time_seconds':clock['frames'][i]['source_time_seconds'],'time_ms':clock['frames'][i]['time_ms'],'duration_ms':clock['frames'][i]['duration_ms']} for i in range(8)]
 for name,durations in [('game-clock',clock['game_clock_gif_ms']),('source-clock',clock['source_clock_gif_ms'])]:
  rgb=[]
  for im in arr:
   resized=im.resize((192,256),Image.Resampling.LANCZOS);back=Image.new('RGB',(192,256),(32,42,56));back.paste(resized,(0,0),resized);rgb.append(back)
  rgb[0].save(P/(style+'-'+name+'.gif'),save_all=True,append_images=rgb[1:],duration=durations,loop=0,disposal=2,optimize=False)
 sheet=Image.new('RGBA',(1536,1024))
 for i,im in enumerate(arr):sheet.alpha_composite(im,(i%4*384,i//4*512))
 sheet.save(P/(style+'-eight-frames.png'))
compare=Image.new('RGB',(768,296),(32,42,56));draw=ImageDraw.Draw(compare)
for i,style in enumerate(styles):
 im=Image.open(P/'frames'/style/'00.png').convert('RGBA').resize((192,256),Image.Resampling.LANCZOS);compare.paste(im,(i*192,40),im);draw.text((i*192+8,12),style,fill='white')
compare.save(P/'swap-comparison.png')
animated_compare=[]
for i in range(8):
 back=Image.new('RGB',(384,256),(32,42,56))
 for k,style in enumerate(['silver','auburn']):
  im=Image.open(P/'frames'/style/f'{i:02}.png').convert('RGBA').resize((192,256),Image.Resampling.LANCZOS);back.paste(im,(k*192,0),im)
 animated_compare.append(back)
animated_compare[0].save(P/'hair-swap-compare.gif',save_all=True,append_images=animated_compare[1:],duration=clock['game_clock_gif_ms'],loop=0,disposal=2,optimize=False)
allposes=Image.new('RGB',(1536,1104),(32,42,56));draw=ImageDraw.Draw(allposes)
for row,style in enumerate(['silver','auburn']):
 for i in range(8):
  im=Image.open(P/'frames'/style/f'{i:02}.png').convert('RGBA').resize((192,256),Image.Resampling.LANCZOS);allposes.paste(im,(i*192,row*552+40),im);draw.text((i*192+6,row*552+12),style+' / '+str(i+1),fill='white')
  base=Image.open(P/'frames/bald'/f'{i:02}.png').convert('RGBA').resize((192,256),Image.Resampling.LANCZOS);allposes.paste(base,(i*192,row*552+296),base)
allposes.save(P/'hair-and-hidden-head-review.png')
(P/'swap-case.json').write_text(json.dumps(case,indent=2)+'\n');print('HAIR_REVIEW_PACKAGE')
