"""Reproduce exact actual direct input plates; never substitute guides for final art."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parent
def square(im):
    can=Image.new('RGBA',(1024,1024));can.paste(im.resize((768,1024)),(128,0));return can
def run():
    s=json.loads((P/'source/source.json').read_text());out=Image.new('RGB',(1536,1080),'#293746');d=ImageDraw.Draw(out)
    for i in range(8):
        im=Image.open(P/f'source/{i:02}.png').convert('RGBA');x=i%4*384;y=i//4*540;out.paste(im,(x,y+25),im);d.text((x+8,y+5),f'{i+1} / {1.3*i/7:.3f}s',fill='white')
    out.save(P/'source-guide.png')
    board=Image.new('RGBA',(1536,1024));d=ImageDraw.Draw(board);S=1.65
    pairs=[('head','chest'),('chest','pelvis')]
    for side in ['left','right']:pairs += [(side+'.shoulder',side+'.elbow'),(side+'.elbow',side+'.wrist'),(side+'.hip',side+'.knee'),(side+'.knee',side+'.ankle'),(side+'.ankle',side+'.toe')]
    for i,f in enumerate(s['frames']):
        x=i%4*384;y=i//4*512;pts={k:((v['xy'][0]-192)*S+192+x,(v['xy'][1]-425)*S+480+y) for k,v in f['points'].items()}
        for a,b in pairs:d.line([pts[a],pts[b]],fill=('#ff943b' if a.startswith('left') else '#389bff' if a.startswith('right') else '#b5becb'),width=9)
        for k,xy in pts.items():d.ellipse((xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4),fill='white')
        hx,hy=pts['head'];d.ellipse((hx-50,hy-100,hx+50,hy+1),outline='#b5becb',width=2);d.line([(x,511+y),(x+383,511+y)],fill='#647180')
    board.save(P/'pose-guide.png')
    im=Image.open(P/'body-attempt2-raw.png').crop((0,0,384,512)).convert('RGBA');im.save(P/'neutral-failed-reference.png');square(im).save(P/'neutral-clean-input.png')
    raw=Image.open(P/'neutral-clean-raw.png').convert('RGBA');w,h=raw.size;raw.transform((384,512),Image.Transform.AFFINE,(w/512,0,w/8,0,h/512,0),Image.Resampling.BICUBIC).save(P/'neutral-canonical.png')
    for name,i in [('repair-rest',7),('repair-key1',1)]:square(Image.open(P/f'body-canonical/{i:02}.png')).save(P/(name+'.png'))
    for key,dx,dy in [(1,-7,-10),(4,0,16)]:
        im=Image.open(P/f'body-canonical/{key:02}.png').convert('RGBA');a=np.asarray(im).astype(float)/255;a[:,:,:3]*=a[:,:,3:4];yy,xx=np.mgrid[:512,:384];fade=np.clip((434-yy)/100,0,1);uvx=xx-dx*fade;uvy=yy-dy*fade
        o=np.stack([map_coordinates(a[:,:,k],[uvy,uvx],order=1,mode='constant',cval=0) for k in range(4)],-1);o[:,:,:3]=np.divide(o[:,:,:3],o[:,:,3:4],out=np.zeros_like(o[:,:,:3]),where=o[:,:,3:4]>0);guide=Image.fromarray(np.uint8(np.clip(o,0,1)*255+.5));square(guide).save(P/f'repair-key{key}-guide.png')
        if key==4:square(im).save(P/'repair-key4-before.png')
if __name__=='__main__':run()
