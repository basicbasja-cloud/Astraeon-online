"""All native exposures for two selected RO blocks; shared crop and exact clocks."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;rows=json.loads((ROOT/'ro-action-audit.json').read_text())['requests'];manifest=[]
for block in (1,5):
 bank=sorted([r for r in rows if r['job']==1 and r['gender']=='male' and r['block']==block],key=lambda r:r['direction']);boxes=[f['bbox'] for r in bank for f in r['frames'] if f['bbox']];box=[min(b[0] for b in boxes)-6,min(b[1] for b in boxes)-6,max(b[2] for b in boxes)+6,max(b[3] for b in boxes)+6];w=(box[2]-box[0])*2;h=(box[3]-box[1])*2;cellw=max(w,140);cellh=h+40;im=Image.new('RGB',(cellw*8,cellh*max(len(r['frames']) for r in bank)),(29,35,47));d=ImageDraw.Draw(im);samples=[]
 for col,r in enumerate(bank):
  with Image.open(ROOT/r['file']) as src:
   for index,f in enumerate(r['frames']):
    src.seek(index);rgba=src.convert('RGBA').crop(box).resize((w,h),Image.Resampling.NEAREST);x=col*cellw;y=index*cellh;im.paste(rgba,(x+(cellw-w)//2,y+38),rgba);d.text((x+4,y+3),f"{r['direction_label']} / {index}\n{f['source_pts_ms']}ms",fill='white');samples.append({'request_id':r['id'],'frame':index,'rgba_sha256':f['rgba_sha256'],'time_ms':f['source_pts_ms'],'duration_ms':f['duration_ms']})
 name=f'ro-grids/swordman-male-full-block{block:02}.png';im.save(ROOT/name);manifest.append({'file':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'block':block,'fixed_shared_crop':box,'fixed_scale':2,'per_frame_fitting':False,'samples':samples})
(ROOT/'ro-full-frame-manifest.json').write_text(json.dumps({'boards':manifest,'skeleton_recovered':False,'clock_authority':'community APNG','production_pass':False},indent=2)+'\n');print(json.dumps({'boards':len(manifest),'all_selected_exposures':sum(len(r['samples']) for r in manifest)}))
