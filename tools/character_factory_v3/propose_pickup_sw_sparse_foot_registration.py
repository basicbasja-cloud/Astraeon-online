"""Propose full-frame Y registration of sparse SW Pickup paint drafts.

Uses a reviewed-looking brown boot ROI as a proxy, not a proven sole landmark.
One scale is shared; no part is moved independently or imported.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1';C=P/'painted-candidates/swordsman-pickup-sw-inbetweens-20261029'
SOURCES={2:C/'002.png',4:C/'004.png',6:C/'006.png',8:P/'painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png',16:P/'review/swordsman-pickup-sw16-head-repair-bounded-20261029/candidate.png'}
GUIDES={2:C/'guide-002.png',4:C/'guide-004.png',6:C/'guide-006.png',8:P/'painted-candidates/swordsman-pickup-sw08-single-20261029/guide.png',16:P/'painted-candidates/swordsman-pickup-sw16-single-20261029/guide.png'}
FRAMES=(2,4,6,8,16);BASE_Y=17;ROI=(210,230,270,350)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def boot_probe(im):
 a=np.array(im.convert('RGB'),dtype=np.int16);y,x=np.indices(a.shape[:2]);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];sel=(x>=ROI[0])&(x<ROI[2])&(y>ROI[1])&(y<ROI[3])&(r-g>15)&(g-b>7)&(r<240);yy,xx=np.where(sel)
 if not len(xx):raise ValueError('No brown foot proxy in fixed ROI')
 low=int(yy.max());return {'bottom_y':low,'bottom_x_mean':float(xx[yy>=low-1].mean()),'pixels':int(len(xx))}
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 tiles={i:Image.open(SOURCES[i]).convert('RGB').resize((384,384),Image.Resampling.LANCZOS)for i in FRAMES};measures={i:boot_probe(tile)for i,tile in tiles.items()};target=measures[8]['bottom_y'];out.mkdir(parents=True);(out/'frames').mkdir();board=Image.new('RGB',(384*5,816),'white');draw=ImageDraw.Draw(board);rows=[]
 for col,i in enumerate(FRAMES):
  delta=target-measures[i]['bottom_y']
  if abs(delta)>25:raise ValueError('Foot proxy registration exceeds study bound')
  tile=Image.new('RGB',(384,384),'white');tile.paste(tiles[i],(0,BASE_Y+delta));tile.save(out/'frames'/f'{i:03}.png');guide=Image.open(GUIDES[i]).convert('RGB')
  board.paste(guide,(col*384,24));board.paste(tile,(col*384,432));draw.text((col*384+4,4),f'Guide {i:02}',fill='black');draw.text((col*384+4,412),f'Draft {i:02} / extra Y {delta:+d}',fill='black')
  rows.append({'frame':i,'paint_sha256':sha(SOURCES[i]),'guide_sha256':sha(GUIDES[i]),'proxy_before_base_y':measures[i],'shared_y':BASE_Y,'additional_y':delta,'sole_proxy_after_y':measures[i]['bottom_y']+BASE_Y+delta,'proxy_x_mean':measures[i]['bottom_x_mean']})
 board.save(out/'comparison.png');report={'status':'SPARSE_FULL_FRAME_Y_REGISTRATION_PROPOSAL_NOT_APPROVED','frames':rows,'reference_frame':8,'shared_tile_resize':[384,384],'brown_foot_proxy_roi':ROI,'baseline_y':BASE_Y,'horizontal_translation':0,'source_modified':False,'runtime_admitted':False,'limitations':['Brown pixels in the ROI are not a validated anatomical sole feature; boot shape and occlusion can change.','X drift, body proportions, sword alignment, foot contact, intermediate frames and gameplay remain unverified.','Only five nonadjacent frames in one direction; cannot be used as animation.']};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
