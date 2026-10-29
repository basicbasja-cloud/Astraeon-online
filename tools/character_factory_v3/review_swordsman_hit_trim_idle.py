"""Review an experimental trimmed Hit clip with a joint-space Idle transition."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
DIRECTIONS=('S','SW','W','NW','N','NE','E','SE')

def make(source,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 manifest=json.loads((source/'manifest.json').read_text());job=manifest['job']
 if manifest.get('experimental_status')!='OBJECT_TRANSFORM_FREEZE_STUDY_NOT_APPROVED' or set(manifest['views'])!=set(DIRECTIONS) or job['frames'] not in (16,20) or job.get('source_ranges',{}).get('Hit_Chest')!=[0,9] or job.get('exit_transition',{}).get('action')!='Idle_Sword':raise ValueError('unexpected study')
 out.mkdir(parents=True);panels=[];metrics={}
 for direction in DIRECTIONS:
  f=manifest['views'][direction]['frames'];seq=[]
  for index in range(1,len(f)):
   def diff(a,b):return math.dist(a,b)*240/768
   seq.append({'from':index-1,'to':index,'head_runtime_px':diff(f[index-1]['landmarks']['head'],f[index]['landmarks']['head']),
               'hand_r_runtime_px':diff(f[index-1]['landmarks']['hand_r'],f[index]['landmarks']['hand_r']),
               'tip_runtime_px':diff(f[index-1]['weapon_guide']['tip'],f[index]['weapon_guide']['tip'])})
  metrics[direction]=seq
 for index in range(job['frames']):
  board=Image.new('RGB',(768,416),'white');draw=ImageDraw.Draw(board)
  for k,direction in enumerate(DIRECTIONS):
   with Image.open(source/direction/f'{index:03}.png') as im:
    if im.size!=(768,768):raise ValueError('expected 768px source')
    rgba=im.convert('RGBA');bg=Image.new('RGBA',rgba.size,'white');bg.alpha_composite(rgba)
    x=(k%4)*192;y=(k//4)*208;board.paste(bg.crop((224,260,544,600)).resize((192,192),Image.Resampling.LANCZOS).convert('RGB'),(x,y+16))
    draw.text((x+3,y+1),f'{direction} {index:02} '+('idle blend' if index>=12 else 'hit'),fill='black')
  panels.append(board)
 for name,duration in (('normal.gif',80),('slow.gif',160)):
  panels[0].save(out/name,save_all=True,append_images=panels[1:],duration=[duration]*(len(panels)-1)+[duration*5],loop=0,optimize=False)
 for index in (0,11,12,job['frames']-1):panels[index].save(out/f'frame{index:02}.png')
 result={'status':'TRIMMED_JOINT_TRANSITION_SOURCE_STUDY_NOT_APPROVED','source_manifest_sha256':hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest(),
         'source_frames':job['frames'],'source_ranges':job['source_ranges'],'exit_transition':job['exit_transition'],'metrics':metrics,
         'limitations':['Metrics describe projected guide landmarks, not visual quality or validated physical contacts.',
                        'A joint-space blend is an authored experiment; no proof of a natural reaction, grip or exact gameplay idle transition.',
                        'GIF repeats a one-shot and its timing is illustrative. No paint, cutout or runtime admission.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.source,a.output)))
