"""Compare frozen and historical Hit guides; no artwork or acceptance implied."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/97bca857f2dea9909fa2'
DIRECTIONS=('S','SW','W','NW','N','NE','E','SE')

def tile(path,crop,size):
 with Image.open(path) as im:
  im=im.convert('RGBA').resize((768,768),Image.Resampling.LANCZOS)
  bg=Image.new('RGBA',(768,768),'white');bg.alpha_composite(im)
  return bg.crop(crop).resize(size,Image.Resampling.LANCZOS).convert('RGB')

def build(source,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 manifest=json.loads((source/'manifest.json').read_text())
 if manifest.get('experimental_status')!='OBJECT_TRANSFORM_FREEZE_STUDY_NOT_APPROVED':raise ValueError('not frozen study')
 if set(manifest['views'])!=set(DIRECTIONS) or manifest['frame_count']!=12:raise ValueError('expected 8 views x 12 frames')
 out.mkdir(parents=True);pair=[];views=[];dist=[]
 for i in range(12):
  board=Image.new('RGB',(736,438),'white');d=ImageDraw.Draw(board)
  for k,(folder,label) in enumerate(((OLD,'historical SW'),(source,'frozen SW'))):
   img=tile(folder/'SW'/f'{i:03}.png',(200,200,568,608),(368,408));board.paste(img,(k*368,30));d.text((k*368+4,6),f'{label} frame {i:02}',fill='black')
  pair.append(board)
  board2=Image.new('RGB',(768,416),'white');d=ImageDraw.Draw(board2)
  for k,direction in enumerate(DIRECTIONS):
   img=tile(source/direction/f'{i:03}.png',(224,260,544,600),(192,192));x=(k%4)*192;y=(k//4)*208;board2.paste(img,(x,y+16));d.text((x+4,y+1),f'{direction} {i:02}',fill='black')
   f=manifest['views'][direction]['frames'][i];dist.append(math.dist(f['landmarks']['hand_r'],f['weapon_guide']['grip']))
  views.append(board2)
 for name,frames in [('sw-before-after.gif',pair),('eight-view-guide.gif',views)]:
  frames[0].save(out/name,save_all=True,append_images=frames[1:],duration=[100]*11+[450],loop=0,optimize=False)
 pair[5].save(out/'sw-frame05-before-after.png')
 receipt={'status':'SOURCE_GUIDE_EXPERIMENT_NOT_ACCEPTED','views':8,'frames_per_view':12,'source_manifest_sha256':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),'projected_hand_bone_to_grip_author_px_min_max':[min(dist),max(dist)],'limitations':['Bone origin and finger midpoint are not proof of a closed grasp.','Repeating one-shot GIF is for review, not an idle transition.','No full-body painted master, cutouts, FX, runtime or contact acceptance.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.source,a.output)))
