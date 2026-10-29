"""Compare three real Pickup guide frames and separately painted drafts.

One shared placement is used. Missing in-between frames are not synthesized.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
PAINT=[P/'review/swordsman-pickup-sw00-short-repair-20261029/candidate.png',P/'painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png',P/'painted-candidates/swordsman-pickup-sw16-single-20261029/generated.png']
GUIDE=[P/'painted-candidates/swordsman-pickup-sw00-repair-20261029/guide.png',P/'painted-candidates/swordsman-pickup-sw08-single-20261029/guide.png',P/'painted-candidates/swordsman-pickup-sw16-single-20261029/guide.png']
FRAMES=(0,8,16);OFFSET=(0,17)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bbox(im):
 a=np.asarray(im.convert('RGB'));y,x=np.where(np.min(a,axis=2)<230)
 if not len(x):raise ValueError('Empty image')
 return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 board=Image.new('RGB',(1152,816),'white');d=ImageDraw.Draw(board);rows=[]
 for col,(frame,g,p) in enumerate(zip(FRAMES,GUIDE,PAINT)):
  guide=Image.open(g).convert('RGB');paint=Image.open(p).convert('RGB')
  if guide.size!=(384,384) or paint.size!=(1254,1254):raise ValueError('Unexpected source canvas')
  tile=Image.new('RGB',(384,384),'white');tile.paste(paint.resize((384,384),Image.Resampling.LANCZOS),OFFSET);gb=bbox(guide);pb=bbox(tile)
  board.paste(guide,(col*384,24));board.paste(tile,(col*384,432));d.text((col*384+5,4),f'Guide frame {frame:02}',fill='black');d.text((col*384+5,412),f'Draft frame {frame:02} / common placement',fill='black')
  rows.append({'frame':frame,'guide_bbox':gb,'draft_bbox':pb,'edge_delta':[b-a for a,b in zip(gb,pb)],'guide_sha256':sha(g),'paint_sha256':sha(p)})
 out.mkdir(parents=True);board.save(out/'keyposes.png');report={'status':'THREE_SEPARATELY_GENERATED_KEY_POSES_NOT_A_SEQUENCE','fixed_tile_size':[384,384],'shared_offset_px':OFFSET,'foreground_threshold':'minimum RGB <230','frames':rows,'source_modified':False,'runtime_admitted':False,'limitations':['Foreground bounds include costume, hair and sword; not anatomical or contact landmarks.','Frames were generated independently; visual and temporal consistency are not established.','No in-betweens, accepted cutouts, variants or gameplay.']};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
