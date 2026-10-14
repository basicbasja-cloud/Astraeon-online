"""Export bounded rear-view study from actual Canvas pixels and fixed clocks."""
import hashlib,json,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
os.environ.setdefault('MPLCONFIGDIR','/tmp/astraeon-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;D=json.loads((P/'motion-contract.json').read_text());Q=json.loads((P/'motion-qa.json').read_text())
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
def frame(p):
    im=Image.open(p).convert('RGBA');o=Image.new('RGBA',im.size,'#344351');o.alpha_composite(im);return o.convert('RGB')
def savegif(path,frames,durations):
    atlas=Image.new('RGB',(frames[0].width,frames[0].height*len(frames)))
    for i,f in enumerate(frames):atlas.paste(f,(0,i*f.height))
    palette=atlas.quantize(colors=255);items=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    items[0].save(path,save_all=True,append_images=items[1:],duration=durations,loop=0,optimize=False,disposal=1)
    decoded=Image.open(path);clock=[]
    for i in range(decoded.n_frames):decoded.seek(i);clock.append(decoded.info['duration'])
    assert clock==durations,(path,clock,durations)
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),encoded_frames=decoded.n_frames,decoded_durations_ms=clock,total_ms=sum(clock))
board=Image.new('RGB',(1536,1100),'#1d2935');bd=ImageDraw.Draw(board);necks=Image.new('RGB',(1280,520),'#1d2935');nd=ImageDraw.Draw(necks)
current=[];views=[];repairs=[];source_comparison=[]
for i,row in enumerate(D['variants']['review']):
    im=frame(P/f'renders/review/full/{i:02}.png');current.append(im.copy());ImageDraw.Draw(current[-1]).text((8,8),'DRAFT / guide fidelity REJECTED',font=FONT,fill='#ffc482');x=i%4*384;y=i//4*550;board.paste(im,(x,y+30));bd.text((x+8,y+5),f'Rear key{i+1} / source {row["source_time_seconds"]:.3f}s',font=FONT,fill='white')
    cx,cy=row['observed_receiver_surface_xy'];crop=im.crop((int(cx)-40,int(cy)-45,int(cx)+40,int(cy)+65)).resize((160,220));x=i%4*320;y=i//4*260;necks.paste(crop,(x+80,y+30));nd.text((x+8,y+5),f'Key{i+1}',font=FONT,fill='white')
    for target,left,label in [(views,P.parent/f'recovery-key-v39/renders/review/full/{i:02}.png','USER accepted v39 / front'),(repairs,P/f'renders/raw8/full/{i:02}.png','Rear before two key repairs'),(source_comparison,P/f'source/{i:02}.png','External source / physical rear camera')]:
        pair=Image.new('RGB',(768,570),'#1d2935');pair.paste(frame(left),(0,32));pair.paste(im,(384,32));pd=ImageDraw.Draw(pair);pd.text((8,6),label,font=FONT,fill='white');pd.text((392,6),'NEW rear / REJECTED guide fidelity',font=FONT,fill='white');pd.text((8,550),f'Key{i+1} / same source clock; art has authored proportions',font=FONT,fill='#c5d8e5');target.append(pair)
board.save(P/'motion-contact-sheet.png');necks.save(P/'motion-neck-detail.png');receipts={}
for clock,durations in D['clocks'].items():
    for name,frames in [('review',current),('two-view',views),('before-after',repairs),('source-vs-art',source_comparison)]:
        filename=f'{name}-{clock}.gif';receipts[filename]=savegif(P/filename,frames,durations)
(P/'playback-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
fig,axes=plt.subplots(1,4,figsize=(20,4.5),layout='constrained');t=[r['source_time_seconds'] for r in D['variants']['review']]
for j,axis in enumerate(['X','Y']):
    after=Q['variants']['review']['projected_phase'];before=Q['variants']['raw8']['projected_phase'];axes[j].plot(t,np.array(after['source_normalized'])[:,j],'--',label='External projected source');axes[j].plot(t,np.array(before['observed_normalized'])[:,j],'o-',label='Before repaired keys');axes[j].plot(t,np.array(after['observed_normalized'])[:,j],'o-',label='New rear visible skin cap');axes[j].set(title=f'{axis} phase / calibration0,3 / six held out',xlabel='Source seconds',ylabel='Normalized projected excursion');axes[j].legend(fontsize=8);axes[j].grid(alpha=.2)
values=[];labels=[]
for side,r in Q['variants']['review']['support'].items():
    for axis,value in zip(['X','Y'],r['rendered_range_px']):values.append(value);labels.append(side+' '+axis)
g=Q['variants']['review']['guide_fidelity'];expected=np.array(g['expected_displacement_xy']);actual=np.array(g['observed_displacement_xy']);axes[2].plot(expected[:,0],expected[:,1],'o--',label='Declared source-to-guide displacement');axes[2].plot(actual[:,0],actual[:,1],'o-',label='Actual painted surface displacement');axes[2].invert_yaxis();axes[2].set_aspect('equal');axes[2].set(title=f'REJECTED: {g["maximum_error_px"]:.2f}px guide error',xlabel='Delta X pixels',ylabel='Delta Y pixels');axes[2].legend(fontsize=7);axes[2].grid(alpha=.2)
axes[3].bar(labels,values);axes[3].axhline(6,color='red',linestyle='--',label='Unchanged6px budget');axes[3].set(title='Actual raster boot surface ranges',ylabel='Pixels');axes[3].tick_params(axis='x',rotation=25);axes[3].legend(fontsize=8);fig.savefig(P/'motion-diagnostics.png',dpi=150);plt.close(fig)
print('EXPORTED_REAR_AND_EXACT_ACCEPTED_FRONT_COMPARISONS')
