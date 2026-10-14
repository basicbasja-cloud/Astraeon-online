"""Review exports from actual browser pixels, no art/pose registration edits."""
import hashlib,json,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
os.environ.setdefault('MPLCONFIGDIR','/tmp/astraeon-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P=Path(__file__).resolve().parent
D=json.loads((P/'motion-contract.json').read_text())
old=P.parent/'neck-motion-v36'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)

def image(path):
    im=Image.open(path).convert('RGBA');out=Image.new('RGBA',im.size,'#344351');out.alpha_composite(im);return out.convert('RGB')

def gif(path,frames,durations):
    # Shared palette is sampled across the whole clip rather than first pose only.
    strip=Image.new('RGB',(frames[0].width,len(frames)*frames[0].height))
    for i,f in enumerate(frames):strip.paste(f,(0,i*f.height))
    palette=strip.quantize(colors=255)
    q=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    q[0].save(path,save_all=True,append_images=q[1:],duration=durations,loop=0,optimize=False,disposal=1)
    decoded=Image.open(path);actual=[]
    for i in range(decoded.n_frames):decoded.seek(i);actual.append(decoded.info['duration'])
    assert sum(actual)==sum(durations)
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),logical_exposures=8,
                encoded_frames=decoded.n_frames,decoded_durations_ms=actual,total_ms=sum(actual),
                terminal_hold_ms=600,production_pass=False)

board=Image.new('RGB',(1536,1100),'#1d2935');bd=ImageDraw.Draw(board)
necks=Image.new('RGB',(1280,520),'#1d2935');nd=ImageDraw.Draw(necks)
current=[];comparisons=[]
for i,row in enumerate(D['variants']['review']):
    im=image(P/f'renders/review/full/{i:02}.png');current.append(im)
    x,y=i%4*384,i//4*550
    board.paste(im,(x,y+30));bd.text((x+8,y+6),f'Key{i+1} / source {row["source_time_seconds"]:.3f}s',font=font,fill='white')
    if i==6:bd.text((x+8,y+520),'REVIEW: unintended left reversal',font=font,fill='#ffc482')
    cx,cy=row['observed_receiver_surface_xy'];crop=im.crop((int(cx)-40,int(cy)-48,int(cx)+40,int(cy)+62)).resize((160,220))
    xx,yy=i%4*320,i//4*260;necks.paste(crop,(xx+80,yy+30));nd.text((xx+8,yy+5),f'Key{i+1}',font=font,fill='white')
    pair=Image.new('RGB',(768,570),'#1d2935');pd=ImageDraw.Draw(pair);pair.paste(image(old/f'renders/review/full/{i:02}.png'),(0,35));pair.paste(im,(384,35));pd.text((10,8),'v36 / 6 drawings + early rest',font=font,fill='white');pd.text((394,8),'v38 / 7 drawings; lateral QA fails',font=font,fill='white');pd.text((10,550),f'One shared source clock / key{i+1}',font=font,fill='#c4d4e0');comparisons.append(pair)
board.save(P/'motion-contact-sheet.png');necks.save(P/'motion-neck-detail.png')
receipts={}
for clock,durations in D['clocks'].items():
    for name,frames in [('review',current),('before-after',comparisons)]:
        filename=f'{name}-{clock}.gif';receipts[filename]=gif(P/filename,frames,durations)
(P/'playback-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')

before=json.loads((P/'before-spacing.json').read_text())['review']
after=json.loads((P/'spacing-qa.json').read_text())['review']
q=json.loads((P/'motion-qa.json').read_text())['variants']['review']
oq=json.loads((old/'motion-qa.json').read_text())['variants']['review']
fig,axes=plt.subplots(1,3,figsize=(15,4.7),layout='constrained')
t=after['source_times_seconds']
axes[0].plot(t,after['source_normalized_phase'],'--',color='#657993',label='External source head-Y phase')
axes[0].plot(t,before['observed_normalized_phase'],'o-',label='v36 collar surface / early rest')
axes[0].plot(t,after['observed_normalized_phase'],'o-',label='v38 collar surface / new key')
axes[0].invert_yaxis();axes[0].set(xlabel='Source time (seconds)',ylabel='Normalized descent',title='Vertical phase improves; this is not all acting')
axes[0].legend(fontsize=8)
xy=np.array(after['observed_receiver_surface_xy']);axes[1].plot(xy[:,0],xy[:,1],'.-',color='#228866')
for i,(x,y) in enumerate(xy):axes[1].annotate(str(i+1),(x,y),xytext=(5,4),textcoords='offset points')
axes[1].plot(xy[5:7,0],xy[5:7,1],color='#cc5533',linewidth=3)
axes[1].invert_yaxis();axes[1].set_aspect('equal');axes[1].set(xlabel='Actual observed collar X (px)',ylabel='Actual observed collar Y (px)',title='Key6 to7 reverses left: NOT PASSED')
labels=['Far X native','Far X raster','Near X native','Near X raster'];oldvalues=[];newvalues=[]
for side in ['far','near']:
    oldvalues.extend([oq['support'][side]['raw_range_at_display_scale_px'][0],oq['support'][side]['rendered_range_px'][0]])
    newvalues.extend([q['support'][side]['raw_range_at_display_scale_px'][0],q['support'][side]['rendered_range_px'][0]])
x=np.arange(4);axes[2].bar(x-.18,oldvalues,.36,label='v36');axes[2].bar(x+.18,newvalues,.36,label='v38');axes[2].axhline(6,color='#c34b35',linestyle='--',label='Unchanged 6px budget');axes[2].set_xticks(x,labels,rotation=30,ha='right');axes[2].set(ylabel='Range at display scale (px)',title='Forefoot proxies: measurable improvement');axes[2].legend(fontsize=8)
for ax in axes:ax.grid(alpha=.2)
fig.savefig(P/'motion-diagnostics.png',dpi=150);plt.close(fig)
print('EXPORTED_TIMED_ACTUAL_PIXELS_WITH_FAILURE_VISIBLE')
