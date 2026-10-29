"""Propose SAM2 head masks for sparse independently painted SW poses."""
import argparse,json
from pathlib import Path
import propose_pickup_sw08_sam_head as base
DIR=base.ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw-inbetweens-20261029'
SETTINGS={
 2:{'crop':(550,230,790,450),'box':(590,250,750,430),'points':((650,320),(655,390),(580,360)),'labels':(1,1,0)},
 4:{'crop':(620,310,870,540),'box':(670,340,840,510),'points':((750,400),(735,475),(700,438),(650,425)),'labels':(1,1,1,0)},
 6:{'crop':(690,420,930,650),'box':(750,440,900,620),'points':((820,500),(795,570),(773,539),(725,525)),'labels':(1,1,1,0)} }
def build(index,checkpoint,out,source=None):
 if index not in SETTINGS:raise ValueError('Unsupported sparse frame')
 cfg=SETTINGS[index];base.SOURCE=source or DIR/f'{index:03}.png';base.CROP=cfg['crop'];base.BOX=cfg['box'];base.POINTS=cfg['points'];base.LABELS=cfg['labels'];return base.build(checkpoint,out)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frame',type=int,required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path);a=p.parse_args();print(json.dumps(build(a.frame,a.checkpoint,a.output,a.source)))
