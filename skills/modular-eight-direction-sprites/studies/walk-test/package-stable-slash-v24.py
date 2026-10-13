"""Lossless animated masters + shared-palette GIF review and a separate FX bank."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/stable-hand-sweep-v24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def background(im):
    out=Image.new('RGB',im.size,'#272727');out.paste(im,(0,0),im);return out
def palette(images):
    size=128;cols=6;rows=(len(images)+cols-1)//cols;sheet=Image.new('RGB',(cols*size,rows*size),'#272727')
    for i,im in enumerate(images):sheet.paste(background(im).resize((size,size)),(i%cols*size,i//cols*size))
    return sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
def save(images,durations,path,loop=False):
    pal=palette(images);rgb=[background(im).quantize(palette=pal,dither=Image.Dither.NONE) for im in images]
    kwargs={'save_all':True,'append_images':rgb[1:],'duration':durations,'disposal':2,'optimize':False}
    if loop:kwargs['loop']=0
    rgb[0].save(path.with_suffix('.gif'),**kwargs)
    images[0].save(path.with_suffix('.png'),save_all=True,append_images=images[1:],duration=durations,disposal=0,blend=0,loop=0 if loop else 1)
def main():
    bank=json.loads((OUT/'evidence/selected-bank.json').read_text());body=[Image.open(ROOT/f['path']).convert('RGBA') for f in bank['frames']]
    durations=[f['duration_ms'] for f in bank['frames']];save(body,durations,OUT/'body-only')
    cap=OUT/'capture';main=[Image.open(cap/f'main-{t:04}.png').convert('RGBA') for t in range(0,720,20)];save(main,[20]*36,OUT/'attack')
    save(main+[body[0]],[20]*36+[800],OUT/'attack-loop-demo',True)
    comparisons=[]
    for t in range(0,720,20):
        im=Image.new('RGBA',(1536,512))
        for j,kind in enumerate(['source','body','main']):im.paste(Image.open(cap/f'{kind}-{t:04}.png').convert('RGBA'),(j*512,0))
        comparisons.append(im)
    save(comparisons,[20]*36,OUT/'comparison')
    fx=[]
    for t in range(0,720,20):
        p=OUT/'fx'/f'{t:04}.png';im=Image.open(p).convert('RGBA');fx.append({'time_ms':t,'duration_ms':20,'file':p.name,'sha256':sha(p),'nonempty':im.getchannel('A').getbbox() is not None})
    assert all(260<=f['time_ms']<440 for f in fx if f['nonempty']);assert not fx[-1]['nonempty']
    (OUT/'fx/manifest.json').write_text(json.dumps({'canvas':[512,512],'duration_ms':720,'scope':'Separate effect exposures on the same body clock; not36new character poses.','frames':fx},indent=2)+'\n')
    board=Image.new('RGB',(2048,1104),'#272727');draw=ImageDraw.Draw(board)
    for i,t in enumerate([0,100,200,260,320,400,500,600]):
        im=main[t//20];x=i%4*512;y=i//4*552;board.paste(im,(x,y+40),im);draw.text((x+8,y+8),f'{i+1} / {t}ms',fill='white')
    board.save(OUT/'attack-eight-poses.png')
    decoded=[]
    for name,expected in [('body-only',720),('attack',720),('attack-loop-demo',1520),('comparison',720)]:
        for ext in ['gif','png']:
            p=OUT/(name+'.'+ext);im=Image.open(p);timing=[]
            for i in range(im.n_frames):im.seek(i);timing.append(im.info.get('duration',0));im.convert('RGBA').load()
            assert abs(sum(timing)-expected)<.001,(p,timing)
            decoded.append({'file':p.name,'sha256':sha(p),'decoded_frames':im.n_frames,'decoded_durations_ms':timing,'duration_ms':sum(timing),'loop':im.info.get('loop'),
                'scope':'Container may merge exact adjacent holds; underlying body bank has8entries/7unique drawings. GIFuses one palette and has quantized color; APNGpreservesRGBA.'})
    (OUT/'evidence/decoded-formats.json').write_text(json.dumps(decoded,indent=2)+'\n');print('ANIMATED_FORMATS_VERIFIED',len(decoded),'720ms action /1520ms loop demo')
if __name__=='__main__':main()
