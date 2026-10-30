"""Compare 32- and 56-sample rig guides for the Swordsman SkillAction."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/f07ff44e6704e195ae4f'
DIRS=('SW','NW','NE','SE');CROP=(120,220,648,748)

def metrics(manifest):
 size=manifest['job']['resolution'];result={}
 for d in DIRS:
  f=manifest['views'][d]['frames'];steps=[]
  for i in range(1,len(f)):
   a,b=f[i-1],f[i];steps.append({'from':i-1,'to':i,'head_runtime_px':math.dist(a['landmarks']['head'],b['landmarks']['head'])*240/size,'hand_runtime_px':math.dist(a['landmarks']['hand_r'],b['landmarks']['hand_r'])*240/size,'tip_runtime_px':math.dist(a['weapon_guide']['tip'],b['weapon_guide']['tip'])*240/size})
  result[d]=steps
 return result

def build(dense,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 baseline=json.loads((BASE/'manifest.json').read_text());new=json.loads((dense/'manifest.json').read_text())
 if baseline['frame_count']!=32 or new['frame_count']!=56 or set(new['views'])!=set(DIRS) or new['job']['source_actions']!=['Sword_Regular_B','Sword_Regular_B_Rec'] or baseline['job']['source_sha256']!=new['job']['source_sha256']:raise ValueError('unexpected source contract')
 out.mkdir(parents=True)
 for folder,manifest,name,duration in ((BASE,baseline,'baseline-32.gif',70),(dense,new,'dense-56.gif',40)):
  frames=[];size=manifest['job']['resolution']
  for i in range(manifest['frame_count']):
   board=Image.new('RGB',(1024,280),'white');d=ImageDraw.Draw(board)
   for k,direction in enumerate(DIRS):
    with Image.open(folder/direction/f'{i:03}.png') as im:
     im=im.convert('RGBA')
     if im.size!=(size,size):raise ValueError('unexpected guide size')
     if size!=768:im=im.resize((768,768),Image.Resampling.LANCZOS)
     box=im.getchannel('A').getbbox()
     if box is None or box[0]<CROP[0] or box[1]<CROP[1] or box[2]>CROP[2] or box[3]>CROP[3]:raise ValueError(f'crop clips {direction} {i}')
     bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);board.paste(bg.crop(CROP).resize((256,256),Image.Resampling.LANCZOS).convert('RGB'),(k*256,24))
    d.text((k*256+3,5),f'{direction} {i:02} / {manifest["frame_count"]}',fill='black')
   frames.append(board)
  frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[duration]*(len(frames)-1)+[duration*5],loop=0,optimize=False)
  if name=='dense-56.gif':
   for i in (0,20,24,28,47,55):frames[i].save(out/f'dense-frame{i:02}.png')
 result={'status':'DENSE_SOURCE_GUIDE_STUDY_NOT_APPROVED','baseline_manifest_sha256':hashlib.sha256((BASE/'manifest.json').read_bytes()).hexdigest(),'dense_manifest_sha256':hashlib.sha256((dense/'manifest.json').read_bytes()).hexdigest(),'baseline':metrics(baseline),'dense':metrics(new),
         'preview_timing_ms':{'baseline_per_frame':70,'dense_per_frame':40,'last_frame_hold_multiplier':5},
         'limitations':['Different sampled phases and per-frame duration mean per-step changes do not prove equal velocity, natural motion or gameplay timing.', 'Props are rig guides; wrist, closed grip, blade width, contact, FX and movement between samples remain unverified.', 'No full-body painted masters, same-frame cutouts, variants or runtime admission.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dense',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.dense,a.output)))
