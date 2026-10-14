"""QA figure: source bones stay on source; manual image observations on art.
No registration/hidden-joint detection or final-art repair is performed.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).resolve().parent;c=json.loads((P/'painted-owner-contract.json').read_text());s=json.loads((P/'source/source.json').read_text());m=json.loads((P/'guide-bind.json').read_text())['whole_bank_matrix'];atlas=Image.open(P/'paint/NW-attempt4.png').convert('RGBA');sheet=Image.new('RGBA',(1536,570),(35,43,53,255));d=ImageDraw.Draw(sheet)
for row,i in enumerate([3,4]):
 x=row*768;source=Image.open(P/f'review-skin/NW/{i:02}.png').convert('RGBA');paint=atlas.crop(tuple(c['frames'][i]['atlas_box']));sheet.alpha_composite(source,(x,30));sheet.alpha_composite(paint,(x+384,30));d.text((x+8,8),'SOURCE '+str(i+1)+' / RIGHT collects',fill='white');d.text((x+392,8),'PAINT '+str(i+1)+' / '+('RIGHT observed' if i==3 else 'LEFT observed: REJECT'),fill=(120,230,190) if i==3 else (255,130,130))
 for side,col in [('left',(255,155,35)),('right',(50,160,255))]:
  def point(name):
   q=s['frames'][i]['points'][side+'.'+name]['xy']['NW'];return (x+m[0]*q[0]+m[4],30+m[3]*q[1]+m[5])
  d.line([point(k) for k in ['shoulder','elbow','wrist','palm','grip']],fill=col,width=3)
 obs=c['frames'][i]['review']['visible_chain'];near=[p for p in obs if p['label'].startswith('near')];far=[p for p in obs if p['label'].startswith('far')]
 for chain,col in [(near,(255,155,35)),(far,(50,160,255))]:
  pts=[(x+384+p['xy'][0],30+p['xy'][1]) for p in chain]
  if len(pts)>1:d.line(pts,fill=col,width=3)
  for px,py in pts:d.ellipse((px-3,py-3,px+3,py+3),fill=col)
d.text((8,548),'SOURCE: projected known bones. PAINT: manually traced CURRENT visible cuff/glove pixels; not automatically detected. No image registration.',fill='white');sheet.convert('RGB').save(P/'holding-owner-image-comparison.png')
