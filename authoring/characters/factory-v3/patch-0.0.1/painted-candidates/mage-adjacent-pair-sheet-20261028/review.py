"""Two-cell diagnostic; no artwork, motion or runtime acceptance."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parents[6];base=Path(__file__).resolve().parent
out=root/'docs/character-factory/review/patch001-mage-adjacent-pair-sheet-20261028';out.mkdir(parents=True,exist_ok=True)
guides=root/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-female-single-frame-trace-20261027'
raw=base/'raw.png';sheet=Image.open(raw).convert('RGBA');assert sheet.width==2*sheet.height
page=Image.new('RGB',(1200,900),'#ddd');draw=ImageDraw.Draw(page);anim=[]; hashes={}
for row,index in enumerate((2,3)):
 path=guides/f'guide{index:03d}.png'; g=Image.open(path).convert('RGBA');w=sheet.height
 a=sheet.crop((row*w,0,(row+1)*w,w)).resize(g.size,Image.Resampling.LANCZOS)
 ov=Image.new('RGBA',g.size,'#ddd');ov.alpha_composite(g);layer=a.copy();layer.putalpha(layer.getchannel('A').point(lambda x:x//2));ov.alpha_composite(layer)
 for col,im in enumerate((g,a,ov)):
  tile=Image.new('RGBA',(400,400),'#ddd');tile.alpha_composite(im.resize((400,400),Image.Resampling.LANCZOS));page.paste(tile.convert('RGB'),(col*400,row*450+30))
 draw.text((0,row*450),f'frame {index:03d}: guide / paint / overlay',fill='black')
 bg=Image.new('RGBA',g.size,'#ddd');bg.alpha_composite(a);anim.append(bg.convert('RGB').resize((512,512),Image.Resampling.LANCZOS))
 hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
for path in (raw,base/'prompt.txt',base/'review.py',root/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-landmark-pair-20261028/frame003-raw.png'):hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
page.save(out/'guide-comparison.jpg',quality=95);anim[0].save(out/'pair-diagnostic.gif',save_all=True,append_images=anim[1:],duration=[500,500],loop=0,disposal=2)
(out/'receipt.json').write_text(json.dumps({'status':'REJECTED_TWO_POSE_SOURCE_ALIGNMENT_NOT_PASSED','source_hashes':hashes,'sheet_size':list(sheet.size),'inspection_canvas':1024,'fit':'identical full-cell resampling; no per-frame translation','visual_approved':False,'runtime_admitted':False},indent=2)+'\n')
