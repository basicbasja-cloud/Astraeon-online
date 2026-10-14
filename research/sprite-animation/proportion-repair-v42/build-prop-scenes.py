from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P/'rig-render-6';ROOT=P.parents[2]
s=json.loads((P/'source/source.json').read_text());b=json.loads((R/'bindings.json').read_text());d=b['display_matrix'];G=np.array(b['whole_bank_rest_matrix']);inv=np.linalg.inv(np.array(s['cameras']['rear']['world_matrix']));scale=512/s['cameras']['rear']['ortho_scale']
def project(v):
 q=inv@np.array([*v,1]);raw=np.array([192+scale*q[0],256-scale*q[1]]);x,y=d[0]*raw+np.array(d[4:6]);return (G@np.array([x,y,1]))[:2]
raw=Image.open(P/'attempt2-raw.png').convert('RGBA');gem=raw.crop((80,388,120,444));gem.save(P/'gem-texture.png');a=np.array(gem.getchannel('A'));yy,xx=np.where(a>=128);center=np.array([(xx.min()+xx.max())/2,(yy.min()+yy.max())/2]);top=project(np.array(s['frames'][0]['object_center'])+[0,0,.075]);bottom=project(np.array(s['frames'][0]['object_center'])-[0,0,.075]);gs=abs(bottom[1]-top[1])/(yy.max()-yy.min());records=[];scenes=[];compare=[]
for i in range(8):
 scene=Image.new('RGBA',(384,512));p=project(s['frames'][i]['object_center']);t=p-gs*center;M=np.array([[gs,0,t[0]],[0,gs,t[1]],[0,0,1]]);I=np.linalg.inv(M);layer=gem.convert('RGBa').transform(scene.size,Image.Transform.AFFINE,tuple(I[:2].flatten()),Image.Resampling.BICUBIC).convert('RGBA') if s['frames'][i]['object_visible'] else Image.new('RGBA',scene.size)
 scene.alpha_composite(layer);scene.alpha_composite(Image.open(R/f'full/{i:02}.png'));folder=R/'scene';folder.mkdir(exist_ok=True);scene.save(folder/f'{i:02}.png');f=R/'prop';f.mkdir(exist_ok=True);layer.save(f/f'{i:02}.png');bg=Image.new('RGBA',scene.size,(45,55,65,255));bg.alpha_composite(scene);scenes.append(bg.convert('RGB'));records.append(dict(index=i,center=p.tolist(),visible=s['frames'][i]['object_visible'],matrix=M[:2].tolist()))
 panel=Image.new('RGBA',(1152,536),(45,55,65,255));dr=ImageDraw.Draw(panel)
 for j,(label,path) in enumerate([('APPROVED v39',P.parent/f'recovery-key-v39/renders/review/full/{i:02}.png'),('REJECTED v41',P.parent/f'forward-pickup-v41/size-locked-review/{i:02}.png'),('v42 RIG / REVIEW CANDIDATE',folder/f'{i:02}.png')]):panel.alpha_composite(Image.open(path).convert('RGBA'),(j*384,24));dr.text((j*384+8,6),label,fill='white')
 compare.append(panel.convert('RGB'))
for name,ds in [('source',[190,180,190,180,190,180,190,600]),('game',[100]*7+[600])]:
 scenes[0].save(R/f'scene-{name}.gif',save_all=True,append_images=scenes[1:],duration=ds,loop=0,disposal=2);compare[0].save(R/f'comparison-{name}.gif',save_all=True,append_images=compare[1:],duration=ds,loop=0,disposal=2)
compare[0].save(R/'neutral-comparison.png');compare[3].save(R/'reach-comparison.png');(R/'prop-bindings.json').write_text(json.dumps(dict(texture_sha256=hashlib.sha256((P/'gem-texture.png').read_bytes()).hexdigest(),crop_from_native_attempt2=[80,388,120,444],texture_raw_sha256=hashlib.sha256((P/'attempt2-raw.png').read_bytes()).hexdigest(),scale=gs,frames=records,scope='Separate world-item layer from actual isolated native gem crop. Source projection/constant scale, item behind actor. Not proven finger force or complete3Docclusion.'),indent=2)+'\n')
