"""Rebuild the fixed-grid SW skill study guide from its retained Blender capture."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image
INDICES=(0,4,7,11,15,18,22,26,29,33,37,40,44,48,51,55)
CROP=(140,200,630,690)
EXPECTED_SOURCE='406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def build(capture, output):
 if output.exists() or output.is_symlink(): raise ValueError('choose fresh output')
 m=json.loads((capture/'manifest.json').read_text())
 if m['job']['source_sha256']!=EXPECTED_SOURCE or m['frame_count']!=56: raise ValueError('unexpected capture provenance')
 frames=m['views']['SW']['frames']
 if len(frames)!=56 or [x['frame'] for x in frames]!=list(range(56)):raise ValueError('unexpected pose indices')
 board=Image.new('RGB',(1536,1536),'white'); pins={}
 for i,n in enumerate(INDICES):
  rel=frames[n]['image'];path=(capture/rel).resolve()
  if not path.is_relative_to(capture.resolve()) or rel!=f'SW/{n:03}.png': raise ValueError('unexpected image path')
  with Image.open(path) as image:
   if image.size!=(768,768):raise ValueError('unexpected canvas size')
   rgba=image.convert('RGBA');box=rgba.getchannel('A').getbbox()
   if box is None or box[0]<CROP[0] or box[1]<CROP[1] or box[2]>CROP[2] or box[3]>CROP[3]:raise ValueError(f'pose {n} is empty or clipped')
   bg=Image.new('RGBA',rgba.size,'white');bg.alpha_composite(rgba)
   board.paste(bg.crop(CROP).resize((384,384)).convert('RGB'),((i%4)*384,(i//4)*384))
  pins[rel]=digest(path)
 output.mkdir(parents=True);board.save(output/'guide.png')
 (output/'receipt.json').write_text(json.dumps({'status':'SOURCE_GUIDE_NOT_PAINTED','indices':INDICES,'crop':CROP,'source_sha256':EXPECTED_SOURCE,'manifest_sha256':digest(capture/'manifest.json'),'inputs':pins,'output_sha256':digest(output/'guide.png'),'script_sha256':digest(Path(__file__))},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.capture,a.output)
