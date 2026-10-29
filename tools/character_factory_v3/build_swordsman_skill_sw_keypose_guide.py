"""Build the fixed-crop guide contact sheet for eight sampled SW skill poses."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]
GUIDES = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/guides/f07ff44e6704e195ae4f/SW'
POSES = (0, 4, 8, 12, 16, 20, 24, 31)

def build(path):
 if path.exists() or path.is_symlink(): raise ValueError('choose fresh output')
 board=Image.new('RGB',(1536,768),'white'); draw=ImageDraw.Draw(board)
 for n,i in enumerate(POSES):
  with Image.open(GUIDES/f'{i:03}.png') as im:
   im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,'white'); bg.alpha_composite(im)
   tile=bg.crop((420,520,1116,1216)).resize((384,384)).convert('RGB')
  board.paste(tile,((n%4)*384,(n//4)*384)); draw.text(((n%4)*384+5,(n//4)*384+5),str(i),fill='black')
 board.save(path)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
