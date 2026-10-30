"""Propose per-pose trails from real source samples; never mutate imported assets."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from build_long_sweep_sword_trail import bounded_path,path_length,paint
from register_preserved_swordsman import transform
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'
DENSE=P/'research/swordsman-attack-dense-path-11-15-20261030/receipt.json'
IMPORT=P/'imports/swordsman-long-dense-basicattack-20261024/import-manifest.json'
REG=P/'review/preserved-swordsman-canonical-cutouts-20261023/receipt.json'
DIRS=('SW','NW','NE','SE');ORDER=('WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def map_points(samples,annotation):
 g=np.asarray(samples[-1]['grip'],float);t=np.asarray(samples[-1]['tip'],float);pg=np.asarray(annotation['weapon_grip'],float);pt=np.asarray(annotation['weapon_tip'],float)
 v=t-g;w=pt-pg;vl=float(np.linalg.norm(v));wl=float(np.linalg.norm(w))
 if min(vl,wl)<2:raise ValueError('degenerate sword projection')
 angle=math.atan2(w[1],w[0])-math.atan2(v[1],v[0]);matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])*wl/vl
 result=[tuple(matrix@(np.asarray(row[key],float)-g)+pg for key in ('grip','tip')) for row in samples]
 if np.linalg.norm(result[-1][0]-pg)>1e-6 or np.linalg.norm(result[-1][1]-pt)>1e-6:raise ValueError('endpoint mapping mismatch')
 return result,wl

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 dense=json.loads(DENSE.read_text());imports=json.loads(IMPORT.read_text());registration=json.loads(REG.read_text());guide=json.loads((SOURCE/'source-guides/manifest.json').read_text());timing=json.loads((SOURCE/'assembly-audit.json').read_text())['durations_ms']
 if dense.get('status')!='DENSE_SOURCE_PATH_NOT_TRAIL_APPROVAL' or dense['sample_count_per_view']!=65 or len(imports['frames'])!=64:raise ValueError('unexpected inputs')
 clips={v['clip']:v for v in guide['clips']};out.mkdir(parents=True);all_original={};all_candidate={};records=[]
 for direction in DIRS:
  native=dense['views'][direction];ann=json.loads((SOURCE/direction/'annotations.generated.json').read_text())['frames'];mapping=next(x for x in registration['frames'] if x['action']=='BasicAttack' and x['direction']==direction)['frames'];frames={x['index']:x for x in imports['frames'] if x['direction']==direction}
  if len(frames)!=16 or len(native)!=65 or any(abs(v['source_frame']-(11+i/16))>1e-7 for i,v in enumerate(native)):raise ValueError('invalid path or import')
  before=[];after=[];effects={}
  for i,opacity in ((7,1.),(8,.55),(9,.15)):
   idx={7:32,8:48,9:64}[i];samples=native[:idx+1];path,blade=map_points(samples,ann[i]);history=bounded_path(path,2.4*blade);length=path_length(history)
   if length>2.4*blade+1e-4:raise ValueError('source-history cap exceeded')
   params=mapping[i];fx=transform(paint(history),params['camera_scale'],params['canvas_translation'])
   if opacity!=1:fx.putalpha(fx.getchannel('A').point(lambda a:round(a*opacity)))
   bbox=fx.getchannel('A').getbbox()
   if bbox is None:raise ValueError('empty trail')
   if bbox[0]==0 or bbox[1]==0 or bbox[2]==768 or bbox[3]==768:raise ValueError('trail touches canvas edge')
   fxrole='WeaponLightBack' if direction in ('NW','NE') else 'WeaponLightFront';effects[i]=(fxrole,fx)
   records.append({'direction':direction,'frame':i,'source_end':samples[-1]['source_frame'],'history_start_source_interval':[samples[max(0,len(samples)-len(history))]['source_frame'],samples[min(len(samples)-1,max(0,len(samples)-len(history))+1)]['source_frame']],'source_sample_count':len(samples),'retained_points':len(history),'path_length_author512':length,'blade_length_author512':blade,'opacity':opacity,'layer':fxrole,'endpoint_mapping_error_author512':max(float(np.linalg.norm(path[-1][0]-np.asarray(ann[i]['weapon_grip']))),float(np.linalg.norm(path[-1][1]-np.asarray(ann[i]['weapon_tip']))))})
   dest=out/direction/fxrole;dest.mkdir(parents=True,exist_ok=True);fx.save(dest/f'{i:03}.png')
  for i in range(16):
   record=frames[i];layers={k:(IMPORT.parent/record['parts'][k]).resolve() for k in ORDER};original=Image.new('RGBA',(768,768));proposal=Image.new('RGBA',(768,768))
   for role in ORDER:
    with Image.open(layers[role]) as im:layer=im.convert('RGBA')
    original.alpha_composite(layer)
    if role.startswith('WeaponLight'):
     replacement=effects[i][1] if i in effects and effects[i][0]==role else Image.new('RGBA',(768,768))
    else:replacement=layer
    proposal.alpha_composite(replacement)
   before.append(original);after.append(proposal)
  all_original[direction]=before;all_candidate[direction]=after
 boards=[]
 for i in range(16):
  board=Image.new('RGB',(1536,816),'#e7e7e7');draw=ImageDraw.Draw(board)
  for row,data in enumerate((all_original,all_candidate)):
   for k,d in enumerate(DIRS):
    x=k*384;y=row*408;frame=data[d][i].resize((384,384),Image.Resampling.LANCZOS);board.paste(frame,(x,y+24),frame);draw.text((x+4,y+5),f'{"existing" if row==0 else "per-frame study"} {d} {i:02}',fill='black')
  boards.append(board)
 boards[0].save(out/'comparison.gif',save_all=True,append_images=boards[1:],duration=timing,loop=0,optimize=False,disposal=2)
 for i in (7,8,9):boards[i].save(out/f'frame{i:02}.png')
 proof={'status':'PER_FRAME_SOURCE_SWEEP_PROPOSAL_NOT_APPROVED','dense_path_sha256':sha(DENSE),'import_manifest_sha256':sha(IMPORT),'source_guide_sha256':sha(SOURCE/'source-guides/manifest.json'),'registration_sha256':sha(REG),'implementation_sha256':sha(__file__),'effect_indices':[7,8,9],'records':records,
        'limitations':['Each frame uses a different 2D similarity fit to annotated grip/tip; mappings can change and cannot reconstruct true 3D blade depth.', 'Painted annotations and grip, original motion, occlusion and trail direction remain unverified.', 'No extrapolation of sampled centerline, but painted FX width/depth and gameplay timing remain artistic choices.', 'Candidate FX is not imported, not a completed attack, and not runtime-approved.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
