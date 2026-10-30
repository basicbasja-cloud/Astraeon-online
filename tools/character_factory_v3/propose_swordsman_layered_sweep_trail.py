"""Propose residual existing trail plus per-pose native sweep continuation."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_swordsman_live_sweep_trail as live
from build_long_sweep_sword_trail import bounded_path,path_length,paint
from register_preserved_swordsman import transform

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 dense=json.loads(live.DENSE.read_text());imports=json.loads(live.IMPORT.read_text());registration=json.loads(live.REG.read_text());timing=json.loads((live.SOURCE/'assembly-audit.json').read_text())['durations_ms']
 if dense.get('status')!='DENSE_SOURCE_PATH_NOT_TRAIL_APPROVAL' or dense['sample_count_per_view']!=65 or len(imports['frames'])!=64:raise ValueError('unexpected source')
 out.mkdir(parents=True);views_before={};views_after={};records=[]
 for direction in live.DIRS:
  native=dense['views'][direction];annotations=json.loads((live.SOURCE/direction/'annotations.generated.json').read_text())['frames'];mapping=next(x for x in registration['frames'] if x['action']=='BasicAttack' and x['direction']==direction)['frames'];frames={x['index']:x for x in imports['frames'] if x['direction']==direction}
  if len(frames)!=16 or len(native)!=65 or any(abs(v['source_frame']-(11+i/16))>1e-7 for i,v in enumerate(native)):raise ValueError('invalid source path')
  role='WeaponLightBack' if direction in ('NW','NE') else 'WeaponLightFront';effects={};previous_new=None
  for i,opacity in ((8,.55),(9,.15)):
   lo,hi=(32,48) if i==8 else (48,64);samples=native[lo:hi+1];path,blade=live.map_points(samples,annotations[i]);history=bounded_path(path,2.4*blade)
   fx=transform(paint(history),mapping[i]['camera_scale'],mapping[i]['canvas_translation']);fx.putalpha(fx.getchannel('A').point(lambda a:round(a*opacity)))
   bbox=fx.getchannel('A').getbbox()
   if bbox is None or bbox[0]==0 or bbox[1]==0 or bbox[2]==768 or bbox[3]==768:raise ValueError('new effect empty or clipped')
   original=(live.IMPORT.parent/frames[i]['parts'][role]).resolve()
   with Image.open(original) as im:combined=im.convert('RGBA')
   if i==9 and previous_new is not None:
    residual=previous_new.copy();residual.putalpha(residual.getchannel('A').point(lambda a:round(a*.25)));combined.alpha_composite(residual)
   combined.alpha_composite(fx);effects[i]=combined
   if i==8:previous_new=fx
   dest=out/direction/role;dest.mkdir(parents=True,exist_ok=True);combined.save(dest/f'{i:03}.png');fx.save(dest/f'{i:03}-new-segment.png')
   records.append({'direction':direction,'frame':i,'new_segment_source_range':[samples[0]['source_frame'],samples[-1]['source_frame']],'source_samples':len(samples),'history_length_author512':path_length(history),'blade_length_author512':blade,'new_segment_opacity':opacity,'layer':role,'old_effect_retained':True,'previous_new_residual_fraction':.25 if i==9 else 0})
  before=[];after=[]
  for i in range(16):
   original=Image.new('RGBA',(768,768));proposal=Image.new('RGBA',(768,768))
   for part in live.ORDER:
    path=(live.IMPORT.parent/frames[i]['parts'][part]).resolve()
    with Image.open(path) as im:layer=im.convert('RGBA')
    original.alpha_composite(layer);proposal.alpha_composite(effects[i] if i in effects and part==role else layer)
   before.append(original);after.append(proposal)
  views_before[direction]=before;views_after[direction]=after
 boards=[]
 for i in range(16):
  board=Image.new('RGB',(1536,816),'#e7e7e7');draw=ImageDraw.Draw(board)
  for row,data in enumerate((views_before,views_after)):
   for k,d in enumerate(live.DIRS):
    x=k*384;y=row*408;frame=data[d][i].resize((384,384),Image.Resampling.LANCZOS);board.paste(frame,(x,y+24),frame);draw.text((x+4,y+5),f'{"existing" if row==0 else "layered proposal"} {d} {i:02}',fill='black')
  boards.append(board)
 boards[0].save(out/'comparison.gif',save_all=True,append_images=boards[1:],duration=timing,loop=0,optimize=False,disposal=2)
 for i in (7,8,9):boards[i].save(out/f'frame{i:02}.png')
 result={'status':'RESIDUAL_PLUS_SOURCE_SEGMENT_PROPOSAL_NOT_APPROVED','dense_path_sha256':sha(live.DENSE),'import_manifest_sha256':sha(live.IMPORT),'implementation_sha256':sha(__file__),'records':records,
         'limitations':['Retained FX is artist-staged; new segments use frame-specific 2D similarity fits to unverified painted grip/tip annotations.', 'Old and new history may overlap or flicker; occlusion, blade width, direction, natural force and gameplay timing are not certified.', 'Only FX proposal: no production or runtime asset changed.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
