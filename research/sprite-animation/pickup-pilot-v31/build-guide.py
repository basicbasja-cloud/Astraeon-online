from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
p=Path(__file__).resolve().parent;s=json.loads((p/'source/source.json').read_text());sheet=Image.new('RGBA',(1536,1024));board=Image.new('RGB',(1536,1104),(35,39,48));d=ImageDraw.Draw(board)
for f in s['frames']:
 i=f['index'];x=i%4*384;y=i//4*512
 with Image.open(f['path']) as im:rgba=im.convert('RGBA');assert list(im.size)==s['canvas'];assert hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256'];sheet.alpha_composite(rgba,(x,y));board.paste(rgba,(x,y+40),rgba)
 d.text((x+12,y+12),f"{i+1} / {f['source_time_seconds']:.3f}s",fill='white')
sheet.save(p/'source-guide.png');board.save(p/'source-review.png');print('GUIDE_READY')
