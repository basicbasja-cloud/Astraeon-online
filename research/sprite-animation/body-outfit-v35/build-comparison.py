"""Static full-character review at equal height; never animation normalization."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
refs=[('Original W appearance',P.parent/'registered-walk-attack-v21/walk/W/frames/00.png'),('v34 articulated cutouts',P.parent/'pickup-view-v34/frames/original/00.png'),('v35 coherent body + outfit',P/'preview/original.png')]
b=Image.new('RGB',(1536,600),(29,41,53));d=ImageDraw.Draw(b);rows=[]
for i,(name,f) in enumerate(refs):
 im=Image.open(f).convert('RGBA');box=im.getbbox();crop=im.crop(box);scale=430/crop.height;size=(round(crop.width*scale),430);crop=crop.resize(size,Image.Resampling.LANCZOS);xy=(i*512+(512-size[0])//2,100)
 d.text((i*512+18,18),name,fill='white');d.text((i*512+18,565),'Same visible height for comparison; views/poses differ',fill='#c3d0e1')
 for y in range(100,531,50):d.line((i*512,y,(i+1)*512,y),fill='#546170',width=1)
 b.paste(crop,xy,crop)
 rows.append(dict(label=name,path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_alpha_bbox=box,comparison_scale=scale,comparison_height_px=430,normalization='static review only: one uniform scale and translation per complete character; no source change',automated_anatomical_ratio_claim=False))
b.save(P/'proportion-comparison.png');(P/'comparison-inputs.json').write_text(json.dumps(dict(images=rows,view_pose_difference_caveat='Original profile walking, v34 opposite front-quarter neutral, v35 front-quarter neutral. Do not score shoulder width as a matched-camera anatomical metric.'),indent=2)+'\n')
sizeboard=Image.new('RGB',(1024,580),(29,41,53));d=ImageDraw.Draw(sizeboard)
for i,(name,file) in enumerate([('Before / head scale .45',P/'preview/head-size-before.png'),('After / head scale .40 (-11.1%)',P/'preview/original.png')]):
 im=Image.open(file).convert('RGBA');sizeboard.paste(im,(i*512,35),im);d.text((i*512+18,12),name,fill='white');d.text((i*512+18,552),'Same body pixels, same neck mount, same canvas',fill='#c3d0e1')
sizeboard.save(P/'head-size-comparison.png')
