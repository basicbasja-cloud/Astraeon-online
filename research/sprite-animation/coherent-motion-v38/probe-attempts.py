"""Fixed visible surface probes; missing/ROI-clipped support stays unknown."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,hashlib
P=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for attempt in [1,2,3,4]:
    path=P/f'attempt{attempt}-raw.png'
    if not path.exists():continue
    image=Image.open(path).convert('RGBA');assert image.size==(1536,1024)
    rows=[];board=Image.new('RGB',(1200,600),'#263443');draw=ImageDraw.Draw(board)
    for i in range(8):
        a=np.array(image.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512)))
        hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2HSV)
        mask=((hsv[:,:,0]<13)&(hsv[:,:,1]>40)&(hsv[:,:,1]<170)&(hsv[:,:,2]>180)&(a[:,:,3]>240)).astype('uint8')
        mask[:65]=0;mask[325:]=0;mask[:,:65]=0;mask[:,270:]=0
        n,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
        ids=[j for j in range(1,n) if stats[j,cv2.CC_STAT_AREA]>50]
        center=None if not ids else centers[min(ids,key=lambda j:stats[j,cv2.CC_STAT_TOP])].tolist()
        surfaces={}
        for name,roi in [('far',[100,435,175,479]),('near',[70,477,275,506])]:
            x0,y0,x1,y1=roi;yy,xx=np.nonzero(a[y0:y1,x0:x1,3]>=128)
            surfaces[name]=dict(roi=roi,status='UNKNOWN_NO_VISIBLE_SURFACE') if not len(xx) else dict(roi=roi,toe_x=int(xx.min()+x0),sole_y=int(yy.max()+y0),status='UNKNOWN_ROI_CLIPPED' if xx.min()==0 or yy.max()==y1-y0-1 else 'VISIBLE_PROXY')
        rows.append(dict(index=i,skin_stub_surface_centroid=center,supports=surfaces))
        if center:
            cx,cy=center;left,top=round(cx)-40,round(cy)-28
            patch=Image.new('RGBA',(80,72),'#344351');patch.alpha_composite(Image.fromarray(a).crop((left,top,left+80,top+72)));patch=patch.convert('RGB').resize((240,216))
            bx,by=i%4*300,i//4*300
            board.paste(patch,(bx+30,by+35));draw.text((bx+6,by+4),f'Key{i+1} / origin({left},{top})',font=font,fill='white')
            for u in range(0,80,10):
                draw.line((bx+30+u*3,by+35,bx+30+u*3,by+251),fill='#71828c');draw.text((bx+30+u*3,by+252),str(left+u),font=font,fill='white')
            for v in range(0,72,10):
                draw.line((bx+30,by+35+v*3,bx+270,by+35+v*3),fill='#71828c');draw.text((bx,by+35+v*3),str(top+v),font=font,fill='white')
    report=dict(image=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),observations=rows,
                scope='Topmost warm visible component and fixed forefoot bands. Advisory surface proposals only; no anatomical detection or ownership approval.')
    (P/f'attempt{attempt}-probe.json').write_text(json.dumps(report,indent=2)+'\n');board.save(P/f'attempt{attempt}-neck-observations.png')
    print(attempt,json.dumps(rows))
