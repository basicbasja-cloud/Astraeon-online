"""Compare a new full-sheet Hit draft against the retained square-crop guide."""
import argparse
from pathlib import Path
import review_swordsman_hit_sw_sheet as original
original.P=original.ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw-endpoint-wholesheet-20261103'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);original.review(p.parse_args().output)
