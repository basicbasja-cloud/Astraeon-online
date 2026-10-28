"""Diagnostic pair only: fixed canvas, no pose fitting or approved animation."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
root=Path(__file__).resolve().parents[6]
base=Path(__file__).resolve().parent
out=root/'docs/character-factory/review/patch001-mage-landmark-pair-20261028'
guide_root=root/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-female-single-frame-trace-20261027'
out.mkdir(parents=True,exist_ok=True)
canvas=1024; page=Image.new('RGB',(1200,900),'#ddd');draw=ImageDraw.Draw(page); preview=[]; hashes={}
for row,index in enumerate((2,3)):
 raw=base/f'frame{index:03d}-raw.png'; guide_path=guide_root/f'guide{index:03d}.png'
 for path in (raw,guide_path):hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
 g=Image.open(guide_path).convert('RGBA');source=Image.open(raw).convert('RGBA');a=source.resize((canvas,canvas),Image.Resampling.LANCZOS)
 overlay=Image.new('RGBA',(canvas,canvas),'#ddd');overlay.alpha_composite(g); layer=a.copy();layer.putalpha(layer.getchannel('A').point(lambda x:x//2));overlay.alpha_composite(layer)
 for col,im in enumerate((g,a,overlay)):
  tile=Image.new('RGBA',(400,400),'#ddd');tile.alpha_composite(im.resize((400,400),Image.Resampling.LANCZOS));page.paste(tile.convert('RGB'),(col*400,row*450+30))
 draw.text((0,row*450),f'frame {index:03d}: guide / paint / overlay',fill='black')
 frame=Image.new('RGBA',(canvas,canvas),'#ddd');frame.alpha_composite(a);preview.append(frame.convert('RGB').resize((512,512),Image.Resampling.LANCZOS))
page.save(out/'guide-comparison.jpg',quality=95)
preview[0].save(out/'pair-diagnostic.gif',save_all=True,append_images=preview[1:],duration=[500,500],loop=0,disposal=2)
for path in (base/'prompt002.txt',base/'prompt003.txt',base/'review.py',root/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-consistent-four-pose-sheet-20261028/identity.png'):
 hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
(out/'receipt.json').write_text(json.dumps({'status':'REJECTED_INCOMPLETE_TWO_POSE_DIAGNOSTIC','source_hashes':hashes,'canvas':1024,'resize':'shared full-canvas 1254-to-1024; no per-frame translation','limitations':['two adjacent poses only; not a complete animation','body proportions, head, costume and free-hand position differ across adjacent frames','foot-to-guide anatomy not certified','no semantic cutout or game admission'],'art_approved':False,'runtime_admitted':False},indent=2)+'\n')
