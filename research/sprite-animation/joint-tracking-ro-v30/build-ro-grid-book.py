#!/usr/bin/env python3
"""Bounded illustrative RO grids; exact source frame IDs/clock, fixed scale.
Full raw provider raster caches remain local. No recovered bones, anatomy approval
or original shipping art. Source includes copyrighted game imagery for study.
"""
import hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'ro-action-audit.json').read_text());records=r['requests'];out=ROOT/'ro-grids';out.mkdir(exist_ok=True);boards=[]
def raster(record,index):
 with Image.open(ROOT/record['file']) as im:im.seek(index);return im.convert('RGBA')
for gender in ('male','female'):
 for block in range(13):
  bank=sorted([q for q in records if q['job']==1 and q['gender']==gender and q['block']==block and q['status']=='decoded'],key=lambda q:q['direction']);im=Image.new('RGB',(8*140,4*160),(32,37,47));d=ImageDraw.Draw(im);sample_records=[]
  for col,q in enumerate(bank):
   indices=[round(i*(len(q['frames'])-1)/3) for i in range(4)]
   for row,index in enumerate(indices):
    f=q['frames'][index];x=col*140;y=row*160;image=raster(q,index).resize((128,128),Image.Resampling.NEAREST);im.paste(image,(x+6,y+29),image)
    d.text((x+5,y+3),f"{q['direction_label']} / frame{index}\n{f['source_pts_ms']}ms",fill='white');sample_records.append({'request_id':q['id'],'frame_index':index,'source_pts_ms':f['source_pts_ms'],'duration_ms':f['duration_ms'],'rgba_sha256':f['rgba_sha256'],'diagnostic_scale':.5,'native_canvas':q['canvas']})
  name=f'swordman-{gender}-block{block:02}.png';im.save(out/name);boards.append({'file':'ro-grids/'+name,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'gender':gender,'block':block,'samples':sample_records,'scope':'4 selected exposures per8requested directions, repeated holds retained; no joint truth'})
# Full indexed class-family overview at one facing, all13blocks.
ids=r['class_family_render_ids']
for offset in range(0,len(ids),10):
 page=ids[offset:offset+10];im=Image.new('RGB',(13*100,len(page)*120),(32,37,47));d=ImageDraw.Draw(im)
 for row,job in enumerate(page):
  for block in range(13):
   q=next(q for q in records if q['job']==job and q['gender']=='male' and q['direction']==7 and q['block']==block);x=block*100;y=row*120;d.text((x+3,y+2),f'job{job}\nblock{block}',fill='white')
   if q['status']=='decoded':
    index=(len(q['frames'])-1)//2;image=raster(q,index).resize((88,88),Image.Resampling.NEAREST);im.paste(image,(x+6,y+30),image)
   else:d.text((x+3,y+48),'UNAVAILABLE\nHTTP500',fill='#ff8396')
 name=f'families-{offset//10+1:02}.png';im.save(out/name);boards.append({'file':'ro-grids/'+name,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'class_render_ids':page,'direction':'SE','gender':'male','diagnostic_scale':88/256,'scope':'1selectedframe per13providerblocks; availability and overview only, not all exposures or all directions.'})
(ROOT/'ro-grid-manifest.json').write_text(json.dumps({'boards':boards,'source':'https://assets.latam-tools.com.br','source_provider':'Community renderer, not official client capture','source_clock':'APNG exposures, not all original-client speed rules','full_raster_bank_redistributed':False,'original_game_assets_rejected_in_user_repo_used':False,'production_pass':False},indent=2)+'\n');print(json.dumps({'boards':len(boards),'full_family_pages':math.ceil(len(ids)/10),'no_per_frame_fit':True}))
