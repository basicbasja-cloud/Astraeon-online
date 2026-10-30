"""Propose source-sweep FX with interpolated art registrations over strike time."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_swordsman_live_sweep_trail as live
from build_long_sweep_sword_trail import bounded_path,path_length,paint
from register_preserved_swordsman import transform

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def mapped_path(samples,annotations):
 if len(samples)!=65 or len(annotations)!=5:raise ValueError('expected five strike keys and 65 samples')
 scales=[];angles=[];translations=[]
 for k,ann in enumerate(annotations):
  row=samples[k*16];g=np.asarray(row['grip'],float);t=np.asarray(row['tip'],float);pg=np.asarray(ann['weapon_grip'],float);pt=np.asarray(ann['weapon_tip'],float);v=t-g;w=pt-pg;vl=np.linalg.norm(v);wl=np.linalg.norm(w)
  if min(vl,wl)<2:raise ValueError('degenerate sword projection')
  scale=wl/vl;angle=math.atan2(w[1],w[0])-math.atan2(v[1],v[0]);matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])*scale
  scales.append(scale);angles.append(angle);translations.append(pg-matrix@g)
 angles=np.unwrap(angles);results=[]
 for i,row in enumerate(samples):
  k=min(i//16,3);f=(i-k*16)/16;scale=math.exp((1-f)*math.log(scales[k])+f*math.log(scales[k+1]));angle=(1-f)*angles[k]+f*angles[k+1];translation=(1-f)*translations[k]+f*translations[k+1];matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])*scale
  results.append(tuple(matrix@np.asarray(row[name],float)+translation for name in ('grip','tip')))
 for k,ann in enumerate(annotations):
  if max(np.linalg.norm(results[k*16][j]-np.asarray(ann['weapon_'+name])) for j,name in enumerate(('grip','tip')))>1e-5:raise ValueError('interpolated key mismatch')
 return results,{'scales':scales,'angles_radians':angles.tolist()}

def build(out, overrides_path=None):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 overrides=json.loads(overrides_path.read_text()) if overrides_path else {};dense=json.loads(live.DENSE.read_text());imports=json.loads(live.IMPORT.read_text());registration=json.loads(live.REG.read_text());timing=json.loads((live.SOURCE/'assembly-audit.json').read_text())['durations_ms']
 if dense.get('status')!='DENSE_SOURCE_PATH_NOT_TRAIL_APPROVAL' or dense['sample_count_per_view']!=65 or len(imports['frames'])!=64:raise ValueError('unexpected source')
 out.mkdir(parents=True);before={};after={};records=[]
 for direction in live.DIRS:
  native=dense['views'][direction];ann=json.loads((live.SOURCE/direction/'annotations.generated.json').read_text())['frames'];mapping=next(x for x in registration['frames'] if x['action']=='BasicAttack' and x['direction']==direction)['frames'];frames={x['index']:x for x in imports['frames'] if x['direction']==direction}
  if len(frames)!=16 or any(abs(v['source_frame']-(11+i/16))>1e-7 for i,v in enumerate(native)):raise ValueError('invalid source path')
  for key,fields in overrides.get(direction,{}).items():
   index=int(key)
   if index not in (5,6,7,8,9) or set(fields)-{'weapon_grip','weapon_tip'}:raise ValueError('invalid annotation override')
   for name,point in fields.items():
    if len(point)!=2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in point):raise ValueError('invalid point')
    ann[index][name]=point
  path,calibration=mapped_path(native,[ann[i] for i in (5,6,7,8,9)]);reference_blade=float(np.linalg.norm(np.asarray(ann[7]['weapon_tip'])-ann[7]['weapon_grip']));cap=2.4*reference_blade;effects={};fxrole='WeaponLightBack' if direction in ('NW','NE') else 'WeaponLightFront'
  for i,opacity in ((7,1.),(8,.55),(9,.15)):
   end={7:32,8:48,9:64}[i];history=bounded_path(path[:end+1],cap);fx=transform(paint(history),mapping[i]['camera_scale'],mapping[i]['canvas_translation'])
   if opacity!=1:fx.putalpha(fx.getchannel('A').point(lambda a:round(a*opacity)))
   bbox=fx.getchannel('A').getbbox()
   if bbox is None or bbox[0]==0 or bbox[1]==0 or bbox[2]==768 or bbox[3]==768:raise ValueError('effect empty or clipped')
   effects[i]=fx;dest=out/direction/fxrole;dest.mkdir(parents=True,exist_ok=True);fx.save(dest/f'{i:03}.png')
   records.append({'direction':direction,'frame':i,'source_end':native[end]['source_frame'],'path_length_author512':path_length(history),'reference_blade_length_author512':reference_blade,'opacity':opacity,'layer':fxrole,'calibration':calibration})
  before[direction]=[];after[direction]=[]
  for i in range(16):
   a=Image.new('RGBA',(768,768));b=Image.new('RGBA',(768,768))
   for role in live.ORDER:
    p=(live.IMPORT.parent/frames[i]['parts'][role]).resolve()
    with Image.open(p) as im:layer=im.convert('RGBA')
    a.alpha_composite(layer);replacement=(effects[i] if i in effects and role==fxrole else Image.new('RGBA',(768,768))) if role.startswith('WeaponLight') else layer;b.alpha_composite(replacement)
   before[direction].append(a);after[direction].append(b)
 boards=[]
 for i in range(16):
  board=Image.new('RGB',(1536,816),'#e7e7e7');draw=ImageDraw.Draw(board)
  for row,data in enumerate((before,after)):
   for k,d in enumerate(live.DIRS):
    x=k*384;y=row*408;frame=data[d][i].resize((384,384),Image.Resampling.LANCZOS);board.paste(frame,(x,y+24),frame);draw.text((x+4,y+5),f'{"existing" if row==0 else "calibrated study"} {d} {i:02}',fill='black')
  boards.append(board)
 boards[0].save(out/'comparison.gif',save_all=True,append_images=boards[1:],duration=timing,loop=0,optimize=False,disposal=2)
 for i in (7,8,9):boards[i].save(out/f'frame{i:02}.png')
 proof={'status':'INTERPOLATED_ART_CALIBRATION_SWEEP_NOT_APPROVED','dense_path_sha256':sha(live.DENSE),'import_manifest_sha256':sha(live.IMPORT),'implementation_sha256':sha(__file__),'annotation_overrides_sha256':sha(overrides_path) if overrides_path else None,'records':records,
        'limitations':['Interpolated 2D fits through painted endpoints are an approximation, not native 3D blade geometry or trajectory.', 'Painted grip/tip annotations, foot/wrist anatomy, trail front/back staging, speed and actual gameplay timing are unverified.', 'Source path is not extrapolated, but width, fade, fixed history cap and draw order are artistic choices.', 'No FX or runtime asset was admitted.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--overrides',type=Path);a=p.parse_args();print(json.dumps(build(a.output,a.overrides)))
