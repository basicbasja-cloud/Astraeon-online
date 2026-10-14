"""INPUT ONLY; inherited strip plus source-arm guide and repaired existing key."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
P=Path(__file__).resolve().parent;raw=Image.open(P/'attempt1-raw.png').convert('RGBA');atlas=Image.new('RGBA',raw.size)
# Reviewed removal windows cover wrong visible arms; native redraw required.
rois={1:[(80,230,190,373),(235,215,291,303)],2:[(67,290,180,422),(165,300,242,359)],4:[(70,278,186,406),(165,289,241,365)],5:[(83,220,185,333),(231,211,284,301)],6:[(97,206,176,315),(244,198,300,289)]}
for i in range(8):
 base=raw.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512))
 if i==3:base=Image.open(P/'goal-normalized.png').convert('RGBA')
 elif i in rois:
  src=Image.open(P/f'guide-rear/{i:02}.png').convert('RGBA');owner=Image.open(P/f'guide-owner/{i:02}.png').convert('RGBA');a=np.array(owner);r,g,b=a[:,:,:3].transpose(2,0,1);colored=(((r>240)&(g>70)&(g<190)&(b<65))|((b>200)&(r<35)&(g<80)))&(a[:,:,3]>100);mask=Image.fromarray(np.where(colored,255,0).astype('uint8')).filter(ImageFilter.MaxFilter(13));d=ImageDraw.Draw(mask)
  for roi in rois[i]:d.rectangle(roi,fill=255)
  base.paste(src,(0,0),mask);owner.putalpha(Image.fromarray(np.where(colored,a[:,:,3],0).astype('uint8')));base.alpha_composite(owner)
 if i==7:base=raw.crop((0,0,384,512)) # input-only endpoint pose repetition; not final copy
 atlas.paste(base,(i%4*384,i//4*512))
atlas.save(P/'attempt2-guide.png');(P/'attempt2-guide-authoring.json').write_text(json.dumps(dict(scope='INPUT ONLY: old wrong arms replaced by actual thin source and colored ownership; existing deepest-key native repair inserted; native neutral0 repeated in input7 because source bones identical. No final art patches/warps/fits.',removal_rois=rois,goal_native_key=3),indent=2)+'\n')
