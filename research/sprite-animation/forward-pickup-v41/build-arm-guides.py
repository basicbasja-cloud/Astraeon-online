"""Guide-only arm removal/owner projection. Never use these pixels as final art."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
P=Path(__file__).resolve().parent
raw=Image.open(P/'attempt1-raw.png').convert('RGBA');atlas=Image.new('RGBA',(1536,1024))
near=[[(105,176),(170,176),(180,232),(161,300),(111,306),(98,250)],[(105,200),(161,199),(161,274),(98,347),(53,344),(49,304),(91,252)],[(110,260),(160,260),(156,330),(105,402),(53,407),(43,369),(91,315)],[(115,288),(161,290),(164,354),(132,407),(114,436),(73,434),(68,403),(100,351)],[(110,285),(174,285),(170,332),(116,372),(64,369),(56,330)],[(115,202),(172,203),(176,263),(150,310),(103,305),(96,257)],[(112,180),(168,181),(175,237),(162,286),(112,280),(102,236)],[(105,176),(170,176),(180,232),(161,300),(111,306),(98,250)]]
far=[[245,165,330,264],[240,153,328,268],[228,195,321,291],[235,232,326,331],[225,201,324,307],[245,158,331,279],[245,145,330,276],[245,165,330,264]]
prop_centers=[[103,400],[107,400],[89,400],[112,417],[91,332],[140,276],[141,232],None]
S=1.04;TX=-3;TY=-29;inverse=(1/S,0,-TX/S,0,1/S,-TY/S)
for i in range(8):
    base=raw.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512))
    reference=Image.open(P/f'source/rear/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC)
    owner=Image.open(P/f'source/owner/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC)
    mask=Image.new('L',(384,512));d=ImageDraw.Draw(mask);d.polygon(near[i],fill=255);d.rectangle(far[i],fill=255)
    if prop_centers[i]:x,y=prop_centers[i];d.rectangle([x-28,y-29,x+28,y+29],fill=255)
    base.paste(reference,(0,0),mask)
    a=np.array(owner);r,g,b=a[:,:,:3].transpose(2,0,1);m=((r>240)&(g>70)&(g<190)&(b<65))|((b>200)&(r<35)&(g<80));o=owner.copy();alpha=np.array(o.getchannel('A'));o.putalpha(Image.fromarray(np.where(m,alpha,0).astype('uint8')));base.alpha_composite(o);atlas.paste(base,(i%4*384,i//4*512))
    if i==3:
        for name,image in [('goal-edit-guide',base),('goal-owner-reference',owner),('goal-normal-reference',reference)]:
            square=Image.new('RGBA',(1024,1024));square.paste(image.resize((768,1024)),(128,0));square.save(P/(name+'.png'))
atlas.save(P/'painted-owner-guide.png')
(P/'arm-guide-authoring.json').write_text(json.dumps(dict(scope='Guide-only patches remove known wrong arms from an existing draft, then project actual occlusion-aware source arm colors. A native repaint must supply final coherent drawings. This is not a final cutout rig, recoloring approval or recovered image skeleton.',source_to_painted_guide_matrix=[S,0,0,S,TX,TY],near_removal_polygons=near,far_removal_rois=far,prop_cleanup_centers=prop_centers),indent=2)+'\n')
