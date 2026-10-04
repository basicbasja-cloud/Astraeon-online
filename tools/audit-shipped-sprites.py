"""Read shipped atlases and reproduce existing registration for review only.

No normalization, repair, generation or runtime asset writes. Shared preview
canvases reveal existing crop/anchor drift. Bounds are silhouette measurements,
not inferred joints, foot contacts or anatomical approval.
"""
import argparse,json,subprocess,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
code='''global.window={};require('./directional-metadata.js');require('./hero-registration.js');console.log(JSON.stringify({metadata:window.AstraeonDirectionalMetadata,registration:window.AstraeonHeroRegistration}));'''
data=json.loads(subprocess.check_output(['node','-e',code],cwd=ROOT,text=True));manifest=json.loads((ROOT/'world/v3/warrior-painted-locomotion.json').read_text())
directions=manifest['directions'];records=[]
for archetype in ['warrior','mage','ranger']:
    for mode,speed in [('walk',1.3),('run',2.7 if archetype=='warrior' else 3.5),('sprint',4.1 if archetype=='warrior' else 4.6)]:
        clip=manifest['clips'][mode] if archetype=='warrior' else None
        key=clip['clip'] if clip else archetype+'-walk';path=clip['atlas'] if clip else 'assets/'+key+'-v1.webp'
        image=Image.open(ROOT/path).convert('RGBA');meta={'cols':8,'rows':8,'frames':[f['rect'] for f in clip['frames']]} if clip else data['metadata'][key]
        registration={'anchors':[f['anchor'] for f in clip['frames']],'heights':clip['heights']} if clip else data['registration'].get(key)
        cycle=clip['cycleDistance'] if clip else 2.1;duration=1000*cycle/speed/8
        for row,direction in enumerate(directions):
            folder=args.output/archetype/mode/direction;folder.mkdir(parents=True,exist_ok=True);previews=[];frames=[]
            for col in range(8):
                i=row*8+col;rect=meta['frames'][i];x,y,w,h=rect;crop=image.crop((x,y,x+w,y+h));bounds=crop.getchannel('A').getbbox()
                anchor=registration['anchors'][i] if registration else None
                unit=(70*(103/76)/registration['heights'][row]) if registration else 103/(image.width/meta['cols'])
                left=-anchor[0]*unit if anchor else (x-col*image.width/meta['cols']-image.width/meta['cols']/2)*unit
                top=-(anchor[1] if anchor else h)*unit
                # Uniform 3x review magnification of the runtime's existing
                # mapping. It cannot correct or independently align any pose.
                canvas=Image.new('RGBA',(480,480),(34,45,56,255));draw=ImageDraw.Draw(canvas);root=(240,390)
                draw.line((0,390,480,390),fill=(96,119,133,255),width=1);draw.line((240,55,240,435),fill=(70,88,102,255),width=1)
                resized=crop.resize((max(1,round(w*unit*3)),max(1,round(h*unit*3))),Image.Resampling.LANCZOS)
                canvas.alpha_composite(resized,(round(root[0]+left*3),round(root[1]+top*3)))
                draw.text((12,12),f'{archetype} {mode} {direction} / {col} / shared root',fill='white');canvas.save(folder/f'{col:02d}.png');previews.append(canvas.convert('RGB'))
                frames.append({'column':col,'rect':rect,'declaredAnchor':anchor,'unit':unit,'left':left,'top':top,'alphaBounds':bounds,'drawnAlphaBounds':None if not bounds else [left+bounds[0]*unit,top+bounds[1]*unit,left+bounds[2]*unit,top+bounds[3]*unit],'soleMetadata':clip['frames'][i].get('sole') if clip else None})
            previews[0].save(folder/'normal.gif',save_all=True,append_images=previews[1:],duration=round(duration),loop=0)
            previews[0].save(folder/'slow.gif',save_all=True,append_images=previews[1:],duration=round(duration*4),loop=0)
            sheet=Image.new('RGB',(1920,960),(34,45,56))
            for col,picture in enumerate(previews):sheet.paste(picture,(col%4*480,col//4*480))
            sheet.save(folder/'transitions.png')
            records.append({'archetype':archetype,'mode':mode,'direction':direction,'atlas':path,'atlasSize':image.size,'registered':registration is not None,'worldSpeed':speed,'cycleDistance':cycle,'nominalFrameMs':duration,'nominalPoseFps':1000/duration,'frames':frames,'scope':'Existing runtime mapping reproduced; anatomical/contact/stride gates require inspection and gameplay timing.'})
(args.output/'atlas-audit.json').write_text(json.dumps({'installedChanges':False,'newAssetsGenerated':False,'cycles':records},indent=2)+'\n')
print('Wrote read-only registration evidence and normal/quarter-speed previews for',len(records),'shipped cycles')
