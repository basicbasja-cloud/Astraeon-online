"""Reconstruct script-declared exposures without pretending to capture gameplay.

Copies fixed atlas cells at native resolution. Retains repeated IDs and terminal
holds; never executes downloaded game scripts or invents a duration for a hold.
"""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(contract,output):
 c=json.loads(Path(contract).read_text());out=Path(output)
 if out.exists():raise ValueError('Fresh output required')
 if sha(c['image_path'])!=c['image_sha256'] or sha(c['descriptor_path'])!=c['descriptor_sha256']:raise ValueError('Changed atlas/descriptor')
 im=Image.open(c['image_path']).convert('RGBA');cols=c['columns'];rows=c['rows']
 if type(cols)!=int or type(rows)!=int or min(cols,rows)<1 or im.width%cols or im.height%rows:raise ValueError('Exact native grid required')
 w=im.width//cols;h=im.height//rows;records=[];images=[];clock=0
 if not c['exposures']:raise ValueError('Empty sequence')
 for i,e in enumerate(c['exposures']):
  n=e['id'];d=e['duration_ms']
  if type(n)!=int or not 0<=n<cols*rows:raise ValueError('Atlas ID outside grid')
  if d is None:
   if c['loop'] or i!=len(c['exposures'])-1 or e.get('hold')!='until_state_change':raise ValueError('Only declared terminal one-shot hold may be untimed')
  elif not isinstance(d,(int,float)) or not math.isfinite(d) or d<=0:raise ValueError('Positive finite native exposure required')
  x=n%cols*w;y=n//cols*h;cell=im.crop((x,y,x+w,y+h));images.append(cell);records.append({'index':i,'source_atlas_id':n,'source_rect':[x,y,w,h],'time_ms':clock,'duration_ms':d,'hold':e.get('hold'),'file':f'{i:04}.png'});clock=None if d is None else clock+d
 out.mkdir(parents=True)
 for f,cell in zip(records,images):
  cell.save(out/f['file']);f['sha256']=sha(out/f['file'])
 scale=min(4,256/max(w,h));dw=round(w*scale);dh=round(h*scale);boardcols=min(8,len(images));board=Image.new('RGB',(boardcols*(dw+12),math.ceil(len(images)/boardcols)*(dh+44)),'#272727');draw=ImageDraw.Draw(board)
 for i,(f,cell) in enumerate(zip(records,images)):
  x=i%boardcols*(dw+12)+6;y=i//boardcols*(dh+44)+38;preview=cell.resize((dw,dh),Image.Resampling.NEAREST);board.paste(preview,(x,y),preview);draw.text((x,y-32),f"{i} / atlas {f['source_atlas_id']}\n{f['duration_ms'] if f['duration_ms'] is not None else 'terminal HOLD'} ms",fill='white')
 board.save(out/'frames-review.png');result={'schema':'script-atlas-reference-v1','contract_sha256':sha(contract),'source_url':c['source_url'],'image_sha256':c['image_sha256'],'descriptor_sha256':c['descriptor_sha256'],'canvas':[w,h],'grid':[cols,rows],'loop':c['loop'],'frames':records,'finite_duration_ms':sum(f['duration_ms'] or 0 for f in records),'duration_ms':clock,'registration':'Exact native atlas cells, no bbox fitting, no mirroring','camera_motion':'unknown','scope':'Configured asset/script reconstruction only; not captured engine playback, world-root/contact evidence, or recovered skeleton.'};(out/'capture.json').write_text(json.dumps(result,indent=2)+'\n');return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=extract(a.contract,a.output);print('ATLAS_REFERENCE',len(r['frames']),r['duration_ms'],'ms; finite prefix',r['finite_duration_ms'])
if __name__=='__main__':main()
