"""Apply the existing bounded head/neck repair to the distinct SW06 master."""
import argparse,json
from pathlib import Path
import propose_pickup_sw16_head_repair as base

def build(output, donor=None):
 old = base.INITIAL, base.DONOR, base.ROI
 try:
  base.INITIAL=base.P/'swordsman-pickup-sw-inbetweens-20261029/006.png'
  base.DONOR=donor or base.P/'swordsman-pickup-sw06-head-repair-20261029/donor.png'
  base.ROI=(700,400,950,690)
  return base.build(output)
 finally:
  base.INITIAL, base.DONOR, base.ROI = old

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--donor',type=Path);a=p.parse_args();print(json.dumps(build(a.output,a.donor)))
