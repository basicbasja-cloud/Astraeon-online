from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
b=Path('authoring/characters/factory-v3/patch-0.0.1/review');o=b/'archer-NW-head-semantic-repair-20261027';r=Path('docs/character-factory/review/patch001-archer-head-ownership-20261027');records=[]
for sex in ['male','female']:
 previews=[];headpreviews=[]
 for i in range(16):
  master=Image.open(b/'archer-coherent-recovery-masters-v2-20261026'/sex/'NW/Master'/f'{i:03d}.png').convert('RGBA');parts={role:Image.open(o/sex/'cutouts'/role/f'{i:03d}.png').convert('RGBA')for role in ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']};combined=Image.new('RGBA',(512,512))
  for p in parts.values():combined.alpha_composite(p)
  if master.tobytes()!=combined.tobytes():raise ValueError('Master changed')
  frame=Image.new('RGBA',(1000,358),'#ddd');panels={'Master':master,**parts}
  for col,(name,im) in enumerate(panels.items()):frame.alpha_composite(im.crop((150,90,350,420)),(col*200,28));ImageDraw.Draw(frame).text((col*200+5,5),f'{sex} {i:02d} {name}',fill='black')
  previews.append(frame.convert('RGB'));h=Image.new('RGBA',(600,330),'#ddd')
  for col,source in enumerate([Image.open(b/'archer-NW-authoring-cutouts-v4-20261026'/sex/'HeadHair'/f'{i:03d}.png'),parts['HeadHair']]):h.alpha_composite(source.crop((190,95,290,205)).resize((300,330),Image.Resampling.NEAREST),(col*300,0))
  ImageDraw.Draw(h).text((5,5),f'{sex} {i:02d} previous / repaired',fill='black');headpreviews.append(h.convert('RGB'))
  records.append({'sex':sex,'frame':i,'recomposition_mismatches':0,'master_sha256':hashlib.sha256((b/'archer-coherent-recovery-masters-v2-20261026'/sex/'NW/Master'/f'{i:03d}.png').read_bytes()).hexdigest(),'hand_occluder_pixels':sum(1 for x in parts['WeaponHandOccluder'].getchannel('A').getdata()if x)})
 for label,factor in [('normal',1),('slow',3)]:previews[0].save(r/f'{sex}-parts-{label}.gif',save_all=True,append_images=previews[1:],duration=[80*factor]*15+[240*factor],loop=0,disposal=2)
 headpreviews[0].save(r/f'{sex}-head-before-after.gif',save_all=True,append_images=headpreviews[1:],duration=[160]*15+[480],loop=0,disposal=2)
 shutil.copy2(o/sex/'heads-light.jpg',r/f'{sex}-heads-light.jpg');shutil.copy2(o/sex/'heads-dark.jpg',r/f'{sex}-heads-dark.jpg')
(r/'same-frame-proof.json').write_text(json.dumps({'frames':records,'all_master_rgba_unchanged':True,'runtime_admitted':False,'timing':'80ms review sampling and240ms terminal hold; not gameplay timing'},indent=2)+'\n');shutil.copy2(o/'head-ownership-proof.json',r/'head-ownership-proof.json');shutil.copy2(__file__,r/'preview-source.py')
