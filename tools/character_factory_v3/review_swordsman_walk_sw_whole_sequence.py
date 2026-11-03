"""Review the 16-frame SW walk draft against its fixed-crop guide."""
import argparse
from pathlib import Path
import audit_swordsman_walk_sw_loop as review

review.SOURCE = review.ROOT / 'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-whole-sequence-20261103'

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    review.build(args.output)
