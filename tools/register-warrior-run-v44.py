"""Normalize complete painted cycles and record visible boot soles, not rig guesses."""
from pathlib import Path
import json,shutil,math
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'authoring/characters/painted-v44';out.mkdir(parents=True,exist_ok=True)
manifest_path=ROOT/'world/v3/warrior-painted-locomotion.json';manifest=json.loads(manifest_path.read_text())
def components(path,rows):
    image=Image.open(path).convert('RGBA');a=np.array(image);labels,n=ndimage.label(a[:,:,3]>100);result={};found=[]
    for k,s in enumerate(ndimage.find_objects(labels),1):
        if s is None or np.sum(labels[s]==k)<700:continue
        ys,xs=s;x0,x1,y0,y1=xs.start,xs.stop,ys.start,ys.stop
        found.append((k,x0,y0,x1,y1))
    assert len(found)==rows*8,(path,len(found))
    ordered=sorted(found,key=lambda p:p[2])
    for row in range(rows):
        strip=sorted(ordered[row*8:row*8+8],key=lambda p:p[1])
        for col,p in enumerate(strip):result[row,col]=p
    assert len(result)==rows*8,(path,len(result))
    return image,a,labels,result
main=out/'warrior-run-seven-directions-source.png';west=out/'warrior-run-W-source.png'
main_data=components(main,7);west_data=components(west,1)
atlas=Image.new('RGBA',(2560,2560));frames=[]
# One scale per source strip; the shorter passing/flight silhouettes are preserved.
main_scale=145/np.median([v[4]-v[2] for v in main_data[3].values()]);west_scale=145/np.median([v[4]-v[2] for v in west_data[3].values()])
for row,direction in enumerate(manifest['directions']):
    image,a,labels,parts=west_data if row==6 else main_data
    source_row=0 if row==6 else 6 if row==7 else row
    scale=west_scale if row==6 else main_scale
    baseline=float(np.median([parts[source_row,col][4] for col in range(8)]))
    for col in range(8):
        k,x0,y0,x1,y1=parts[source_row,col];x0-=3;y0=max(0,y0-3);x1+=3;y1+=3
        body=a[y0:y1,x0:x1].copy();mask=ndimage.binary_dilation(labels[y0:y1,x0:x1]==k,iterations=2);body[:,:,3]=np.where(mask,body[:,:,3],0)
        sprite=Image.fromarray(body).resize((round((x1-x0)*scale),round((y1-y0)*scale)),Image.Resampling.LANCZOS)
        head=(labels[y0:y1,x0:x1]==k)&(np.indices(mask.shape)[0]<(y1-y0)*.18);yy,xx=np.nonzero(head);center=float(np.mean(xx))
        left=round(160-center*scale);top=round(264-(baseline-y0)*scale)
        assert left>=0 and top>=0 and left+sprite.width<=320 and top+sprite.height<=320,(direction,col,sprite.size,left,top)
        atlas.alpha_composite(sprite,(row*0+col*320+left,row*320+top))
        frames.append({'direction':direction,'phase':col/8,'rect':[col*320,row*320,320,320],'anchor':[160,264],'sourceRect':[x0,y0,x1-x0,y1-y0],'sourceFile':str((out/('warrior-run-W-source.png' if row==6 else 'warrior-run-seven-directions-source.png')).relative_to(ROOT)).replace('\\','/')})
atlas_path=ROOT/'assets/warrior-run-v5.webp';temporary=atlas_path.with_suffix('.tmp.webp');atlas.save(temporary,quality=95,method=6);temporary.replace(atlas_path)
manifest['clips']['run'].update(clip='warrior-run-v5',atlas='assets/warrior-run-v5.webp',frames=frames,scale=round(main_scale,5),source='authoring/characters/painted-v44/warrior-run-seven-directions-source.png')

def boot_candidates(cell):
    a=np.array(cell);rgb=a[:,:,:3].astype(float);opaque=a[:,:,3]>100;yy,xx=np.nonzero(opaque)
    top,bottom=min(yy),max(yy);ygrid=np.indices(opaque.shape)[0]
    brown=opaque&(ygrid>top+(bottom-top)*.68)&(rgb[:,:,0]>rgb[:,:,2]+12)&(rgb[:,:,1]>rgb[:,:,2]+5)&(rgb[:,:,0]<190)
    brown=ndimage.binary_closing(brown,iterations=1);labels,n=ndimage.label(brown);points=[]
    for k,s in enumerate(ndimage.find_objects(labels),1):
        if s is None or np.sum(labels[s]==k)<28:continue
        ys,xs=np.nonzero(labels==k);low=max(ys);xs=xs[ys>=low-2];point=[float(np.median(xs)),float(low)]
        # Bronze sword details/cape trim are not boot contacts. Boots occupy the
        # lower central body; keep their substantial connected painted area.
        if len(ys)>=80 and abs(point[0]-160)<82 and low>bottom-(bottom-top)*.2:points.append(point)
    if points:
        # Weapon/cape tips can satisfy the brown component test, especially in
        # rear views. Ground support comes from the lowest substantial boot,
        # not the furthest forward brown pixel. Keep only that bottom band.
        lowest=max(p[1] for p in points);points=[p for p in points if p[1]>=lowest-5]
    if not points:points=[[float(np.median(xx[yy>=bottom-2])),float(bottom)]]
    return points
review=Image.new('RGB',(2560,2560),'#b7c5c7')
for mode,clip in manifest['clips'].items():
    clip['duty']={'walk':.56,'run':.375,'sprint':.25}[mode]
    image=Image.open(ROOT/clip['atlas']).convert('RGBA')
    for row in range(8):
        angle=math.pi/2-row*math.pi/4;forward=np.array([math.cos(angle),math.sin(angle)])
        previous=None
        for col in range(8):
            f=clip['frames'][row*8+col];cell=image.crop(tuple([f['rect'][0],f['rect'][1],f['rect'][0]+320,f['rect'][1]+320]));candidates=boot_candidates(cell)
            if col%4==0 or previous is None:point=max(candidates,key=lambda p:float(np.dot(np.array(p)-np.array(f['anchor']),forward)))
            else:point=min(candidates,key=lambda p:math.hypot(p[0]-previous[0],p[1]-previous[1]))
            previous=point;f['sole']=[round(v,2) for v in point]
            # Individual directions have different aerial source poses: the W
            # run passing frames and two sprint frames visibly lift both boots.
            # Do not force those raised poses into a planted support phase.
            timed_stance=mode=='walk' or col%4<(2 if mode=='sprint' else 3)
            f['stance']=bool(timed_stance and (mode=='walk' or point[1]>=f['anchor'][1]-12));f['support']=col//4
            # Reviewed sprint source: W and SW tuck both boots in these poses;
            # SE switches to the other visible boot before the half-cycle.
            if mode=='sprint':
                if (row==0 and col==5) or (row in (6,7) and col in (1,5)):f['stance']=False
                if row==1 and col==1:f['support']=1
            if mode=='run':
                c=Image.new('RGBA',(320,320),'#b7c5c7');c.alpha_composite(cell);d=ImageDraw.Draw(c);x,y=point;d.ellipse((x-4,y-4,x+4,y+4),fill='#ff5544');review.paste(c.convert('RGB'),(col*320,row*320))
manifest['visibleContacts']='Measured brown-boot sole coordinates in registered complete frames. Runtime contact locking translates the complete body, never individual limbs.'
manifest['northwestRepair']['modes']=['walk','sprint']
temporary=manifest_path.with_suffix('.json.tmp');temporary.write_text(json.dumps(manifest,indent=2)+'\n');temporary.replace(manifest_path)
review.resize((1280,1280)).save(out/'warrior-run-contacts.jpg',quality=95)
print('Registered 64 complete run frames and visible contact metadata for all 192 movement frames')
