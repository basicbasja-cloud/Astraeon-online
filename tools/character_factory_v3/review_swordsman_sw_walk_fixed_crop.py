"""Build a guide/draft preview from two existing 4x4 SW walk sheets."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-fixed-crop-20261029'

def bbox(tile):
 a=np.asarray(tile.convert('RGB'));y,x=np.where(np.min(a,axis=2)<230)
 if not len(x):raise ValueError('Empty frame')
 return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 paths=[SOURCE/'guide-contact.png',SOURCE/'generated-sheet.png'];sheets=[Image.open(p).convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS) for p in paths];frames=[];measure=[]
 for i in range(16):
  x=i%4*384;y=i//4*384;tiles=[s.crop((x,y,x+384,y+384)) for s in sheets];box=[bbox(t) for t in tiles]
  board=Image.new('RGB',(768,416),'white');board.paste(tiles[0],(0,32));board.paste(tiles[1],(384,32));draw=ImageDraw.Draw(board);draw.text((5,8),f'Guide SW {i:02}',fill='black');draw.text((389,8),f'Paint draft SW {i:02}',fill='black');frames.append(board)
  measure.append({'frame':i,'guide_bbox':box[0],'draft_bbox':box[1],'edge_delta':[b-a for a,b in zip(*box)]})
 out.mkdir(parents=True);frames[0].save(out/'comparison.gif',save_all=True,append_images=frames[1:],duration=85,loop=0,optimize=False)
 receipt={'status':'DRAFT_NOT_ACCEPTED','guide_crop_source_px':[420,520,1116,1216],'grid_slot_px':384,'uniform_sheet_resize':[1536,1536],'duration_ms_diagnostic':85,'foreground_threshold':'RGB minimum < 230','measurements':measure,'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'limitations':['Foreground bounding boxes include weapon and clothing, not anatomical landmarks.','Generated white background has not been extracted to usable alpha.','No temporal, contact, semantic cutout or runtime approval.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
