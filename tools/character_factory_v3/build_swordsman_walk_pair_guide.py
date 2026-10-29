"""Build two fixed-scale SW Walk guide pairs from original source renders."""
import argparse
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/SW'
CROP=(420,520,1116,1216)

def build(start,out):
 if start not in (0,2):raise ValueError('Only the two documented pairs are supported')
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 if CROP[2]-CROP[0]!=CROP[3]-CROP[1]:raise ValueError('crop must be square')
 board=Image.new('RGB',(1536,768),'white')
 for j,index in enumerate((start,start+1)):
  with Image.open(GUIDE/f'{index:03}.png') as im:
   if im.size!=(1536,1536):raise ValueError('unexpected guide size')
   rgba=im.convert('RGBA');bbox=rgba.getchannel('A').getbbox()
   if bbox is None or bbox[0]<CROP[0] or bbox[1]<CROP[1] or bbox[2]>CROP[2] or bbox[3]>CROP[3]:raise ValueError('crop clips guide')
   bg=Image.new('RGBA',rgba.size,'white');bg.alpha_composite(rgba);board.paste(bg.crop(CROP).resize((768,768),Image.Resampling.LANCZOS).convert('RGB'),(j*768,0))
 board.save(out)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--start',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.start,a.output)
