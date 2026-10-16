"""Repeat an explicitly saved neutral-only affine over the entire native bank."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
P=Path(__file__).resolve().parent;view=sys.argv[1];d=json.loads((P/(view+'-key-normalization.json')).read_text());raw=P/'raw'/f'{view}-empty-body-attempt1.png';assert hashlib.sha256(raw.read_bytes()).hexdigest()==d['raw_sha256'];im=Image.open(raw).convert('RGBA');s=d['scale'];tx,ty=d['translation'];out=P/'key-textures'/view;out.mkdir(parents=True,exist_ok=True);board=Image.new('RGBA',(1536,1024))
for i in range(8):
 c=im.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));a=c.transform((384,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);a.save(out/f'{i:02}.png');board.alpha_composite(a,(i%4*384,i//4*512))
board.save(P/'inputs'/f'{view}-normalized-key-bank.png');bg=Image.new('RGBA',board.size,(40,43,48,255));bg.alpha_composite(board);bg.convert('RGB').save(P/'inputs'/f'{view}-normalized-key-preview.png')
