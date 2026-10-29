"""Apply the existing SAM2 head-mask study to the separately drawn SW16 pose."""
import argparse,json
from pathlib import Path
import propose_pickup_sw08_sam_head as base
base.SOURCE=base.ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw16-single-20261029/generated.png'
base.CROP=(690,560,930,780);base.BOX=(750,590,900,750)
base.POINTS=((820,655),(785,715),(773,681),(735,675));base.LABELS=(1,1,1,0)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path,default=base.SOURCE);a=p.parse_args();base.SOURCE=a.source;print(json.dumps(base.build(a.checkpoint,a.output)))
