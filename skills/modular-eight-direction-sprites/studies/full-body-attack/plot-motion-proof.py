"""Scientific projection of the original joint motion; not character repainting."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image

OUT = Path(__file__).parent
data = json.loads((OUT / 'motion-proof-poses.json').read_text())

def diagram(ax, pose, title=False):
    ax.set_xlim(0,384); ax.set_ylim(512,0); ax.set_aspect('equal');ax.axis('off')
    def p(v):return (180+v[0]*200,400+v[1]*200)
    q=pose['projected']
    def line(points,color,width=7):
        pts=[p(v) for v in points];ax.plot([v[0] for v in pts],[v[1] for v in pts],color=color,linewidth=width,solid_capstyle='round')
    ax.scatter([180],[400],c='#84909c',s=15,marker='+')
    for side,color in [('left','#2472a3'),('right','#c56d31')]:
        f=q['feet'][side];line([f['heel'],f['toe']],color,9)
        l=q['legs'][side];line([l['start'],l['joint'],l['end']],color,10)
        for point in [l['joint'],f['ankle']]:ax.add_patch(Circle(p(point),5,color=color,zorder=4))
        ax.scatter(*p(f['toe']),color='#2a9351',s=35,zorder=5)
    shoulder=[sum(q['arms'][s]['start'][i] for s in ['right','left'])/2 for i in range(3)]
    line([q['hip'],shoulder],'#8492a2',24)
    line([q['legs']['right']['start'],q['legs']['left']['start']],'#5d607b',13)
    line([q['arms']['right']['start'],q['arms']['left']['start']],'#667689',15)
    for side,color in [('left','#2472a3'),('right','#c56d31')]:
        a=q['arms'][side];line([a['start'],a['joint'],a['end']],color,10)
        ax.add_patch(Circle(p(a['joint']),5,color=color,zorder=4))
    line([q['arms']['right']['end'],q['swordTip']],'#49adad',5)
    ax.add_patch(Circle(p(q['head']),48,facecolor='#cad1df',edgecolor='#65758a',linewidth=2,zorder=3))
    # Forward-facing marker; independent of torso's winding/untwisting.
    h=q['head'];ax.add_patch(Circle((p(h)[0]+16,p(h)[1]+9),4,color='#41525b',zorder=4))
    if title:ax.text(192,497,pose['phase'].replace('_',' ')+' · '+str(pose['duration_ms'])+' ms',ha='center',fontsize=8,color='#3f4852')

fig,axes=plt.subplots(2,4,figsize=(15.36,10.24),dpi=100)
for ax,p in zip(axes.flat,data['directions'][1]):diagram(ax,p)
fig.subplots_adjust(left=0,right=1,bottom=0,top=1,wspace=0,hspace=0)
fig.savefig(OUT/'SE-pose-guide.png',dpi=100,facecolor='white');plt.close(fig)
fig,axes=plt.subplots(2,4,figsize=(15.36,10.24),dpi=100)
for ax,p in zip(axes.flat,data['directions'][1]):diagram(ax,p,True)
fig.subplots_adjust(left=0,right=1,bottom=0,top=1,wspace=0,hspace=0)
fig.savefig(OUT/'SE-pose-study-labelled.png',dpi=100,facecolor='white');plt.close(fig)
fig,axes=plt.subplots(8,8,figsize=(20.48,27.30),dpi=100)
for direction,row in enumerate(axes):
    for ax,p in zip(row,data['directions'][direction]):diagram(ax,p)
fig.subplots_adjust(left=0,right=1,bottom=0,top=1,wspace=0,hspace=0)
fig.savefig(OUT/'eight-directions-motion-proof.png',dpi=100,facecolor='white');plt.close(fig)
guide=Image.open(OUT/'SE-pose-guide.png').convert('RGB')
frames=[guide.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512)).resize((192,256),Image.Resampling.LANCZOS) for i in range(8)]
frames[0].save(OUT/'SE-motion-proof.gif',save_all=True,append_images=frames[1:],duration=[p['duration_ms'] for p in data['keys']],loop=0,disposal=2)
print('Saved eight-view projection study, SE guide and timed blocking GIF.')
