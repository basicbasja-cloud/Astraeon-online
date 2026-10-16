from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;records=[]
for view in ['S','SW','W','NW','N','NE','E','SE']:
 for mode in ['full','leg-owner']:
  board=Image.new('RGB',(1536,1024),(40,43,48));d=ImageDraw.Draw(board)
  for i in range(8):
   f=P/f'guides/{view}/{mode}/{i:02}.png';im=Image.open(f);board.paste(im,(i%4*384,i//4*512),im);d.text((i%4*384+6,i//4*512+6),f'{view} phase{i}/8',fill='white')
  out=P/f'guides/{view}/{mode}-eight.png';board.save(out);records.append({'view':view,'mode':mode,'file':str(out.relative_to(P)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(P/'source/guide-atlas-receipt.json').write_text(json.dumps({'atlases':records,'scope':'Original motion guide only, not an external reference or approved final sprite','owner_colors':{'orange':'anatomical LEFT','blue':'anatomical RIGHT'}},indent=2)+'\n')
