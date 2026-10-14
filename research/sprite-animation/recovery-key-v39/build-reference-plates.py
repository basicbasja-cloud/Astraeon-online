"""Exact square plates used for the isolated existing-key edit."""
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;V=P.parent/'coherent-motion-v38'
raw=Image.open(V/'attempt2-raw.png').convert('RGBA');guide=Image.open(V/'near-rest-pose-guide.png').convert('RGBA')
for name,im in [('standing-reference',raw.crop((1152,512,1536,1024))),('near-rest-reference',guide.crop((768,512,1152,1024)))]:
    out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((768,1024),Image.Resampling.NEAREST),(128,0));out.save(P/f'{name}.png')
