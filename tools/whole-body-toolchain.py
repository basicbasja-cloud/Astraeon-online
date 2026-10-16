"""Reuse audited local sprite tools without pose fitting, limb deformation or art auto-approval."""
from pathlib import Path
from PIL import Image,PngImagePlugin
import argparse,hashlib,json,subprocess,sys,importlib.util,contextlib,io
ROOT=Path(__file__).resolve().parents[1];SKILLS=ROOT/'.agents/skills';SLOTS={'body','head','weapon','trail'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def clip_input(path):
 path=path.resolve();d=json.loads(path.read_text());assert d['bodyPolicy']=='complete-posed-body-raster';assert d['frames']
 for f in d['frames']:
  assert isinstance(f['duration_ms'],int)and 0<f['duration_ms']<=65535
  assert set(f['slots'])==SLOTS and set(f['order'])==SLOTS and len(f['order'])==4
  assert f['slots']['body']and f['slots']['head']
  for s in f['slots'].values():
   if s:
    assert set(s)=={'asset','sha256'}
    p=(path.parent/s['asset']).resolve();assert p.is_file()and sha(p)==s['sha256'];assert list(Image.open(p).size)==d['canvas']
 return path,d
def gate(out,reference):
 tool=SKILLS/'img2game2d/forge';state=out/'.img2game2d/state.json'
 if not state.exists():
  subprocess.run([sys.executable,str(tool/'state.py'),'init','--state',str(state),'--reference',str(reference),'--profile','character'],check=True,capture_output=True,text=True)
 result=subprocess.run([sys.executable,str(tool/'next.py'),'--state',str(state)],capture_output=True,text=True)
 (out/'next-step.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,'img2game2d state does not allow work; inspect next-step.txt'
def pack(a):
 source,d=clip_input(a.clip);out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);frames=sorted(a.frames.resolve().glob('*.png'));assert len(frames)==len(d['frames']);assert not(out/'atlas').exists(),'Choose a fresh output directory'
 for f in frames:assert list(Image.open(f).size)==d['canvas']
 # Match full figures to the actual slot composition before packing.
 import numpy as np
 for i,f in enumerate(frames):
  full=Image.open(f).convert('RGBA');comp=Image.new('RGBA',full.size)
  for name in d['frames'][i]['order']:
   s=d['frames'][i]['slots'][name]
   if s:comp.alpha_composite(Image.open(source.parent/s['asset']).convert('RGBA'))
  x=np.array(full);y=np.array(comp);visible=x[:,:,3]>0;assert np.array_equal(x[:,:,3],y[:,:,3])and np.array_equal(x[visible],y[visible]),f
 gate(out,frames[0]);file=SKILLS/'img2game2d/forge/stage5_atlas/generate_spritesheet.py';spec=importlib.util.spec_from_file_location('atlas',file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 with contextlib.redirect_stdout(io.StringIO()):result=m.generate_spritesheet(str(a.frames.resolve()),str(out/'atlas'),padding=2,scale=1)
 assert len(result)==1;r=next(iter(result.values()));meta_path=Path(r['json_path']);meta=json.loads(meta_path.read_text());atlas_path=Path(r['sheet_path']);sheet=Image.open(atlas_path).convert('RGBA')
 for i,(f,r)in enumerate(zip(frames,meta['frames'])):
  assert sheet.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h'])).tobytes()==Image.open(f).convert('RGBA').tobytes(),f
  r['duration_ms']=d['frames'][i]['duration_ms'];r['source_sha256']=sha(f)
 meta['fps']=None;meta['timing_source']='Explicit source clip duration_ms, preserved per exposure';meta['source_clip_sha256']=sha(source);save(meta_path,meta)
 report={'technical_pack_pass':True,'frames':len(frames),'exact_rgba_cells':len(frames),'durations_ms':[f['duration_ms']for f in d['frames']],'total_ms':sum(f['duration_ms']for f in d['frames']),'per_frame_transform_applied':False,'art_approval_granted':False,'source_art_status':d.get('art_status','not_provided'),'source_head_status':d.get('head_extraction_status','not_provided'),'source_declared_production_pass':d.get('production_pass',False),'source_clip_sha256':sha(source),'patched_packer_sha256':sha(file),'atlas_sha256':sha(atlas_path)}
 save(out/'pack-review.json',report);print(json.dumps(report,indent=2))
def editable(a):
 source,d=clip_input(a.clip);out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);target=out/'pickup-four-slots.aseprite';assert not target.exists(),'Choose a fresh output directory';orders={tuple(f['order'])for f in d['frames']};assert len(orders)==1,'Changing equipment depth needs explicitly authored physical passes';order=list(orders.pop());events=[]
 def call(command,payload):
  payload={'aseprite':str(a.aseprite.resolve()),**payload};proc=subprocess.run([str(a.spa.resolve()),*command.split(),'--input-json','-'],input=json.dumps(payload),capture_output=True,text=True);result=json.loads(proc.stdout);events.append({'command':command,'status':result.get('status'),'result':result});save(out/'spa-operations.json',events);assert proc.returncode==0 and result.get('status')=='success',result;return result
 def mutation():return {'source_sprite_file':str(target),'target_sprite_file':str(target),'in_place':True,'overwrite':True}
 prepared={};profile_rows=[]
 for frame in d['frames']:
  for slot in frame['slots'].values():
   if slot and slot['asset']not in prepared:
    original=source.parent/slot['asset'];image=Image.open(original).convert('RGBA');info=Image.open(original).info;assert not info.get('icc_profile'),'ICC-tagged input needs an explicit matching profile adapter'
    dest=out/'import'/f'{len(prepared):02}.png';dest.parent.mkdir(exist_ok=True);metadata=PngImagePlugin.PngInfo();metadata.add(b'sRGB',bytes([info.get('srgb',0)]));image.save(dest,pnginfo=metadata);assert Image.open(dest).convert('RGBA').tobytes()==image.tobytes()
    prepared[slot['asset']]=dest;profile_rows.append({'source_asset':slot['asset'],'source_sha256':sha(original),'prepared_asset':str(dest.relative_to(out)),'prepared_sha256':sha(dest),'exact_source_RGBA':True,'operation':'Assign sRGB PNG metadata for native import; no pixel conversion, recoloring, fitting or canvas change.'})
 save(out/'import-profile-assignment.json',profile_rows)
 call('sprite create',{'width':d['canvas'][0],'height':d['canvas'][1],'color_mode':'rgb','initial_layer':{'kind':'transparent'},'target_sprite_file':str(target),'overwrite':False})
 call('layer set',{**mutation(),'target':{'layer_path':[1]},'properties':{'name':order[0]}})
 for name in order[1:]:call('layer add',{**mutation(),'kind':'transparent','name':name})
 call('frame set',{**mutation(),'frame_number':1,'duration_ms':d['frames'][0]['duration_ms']})
 for i,f in enumerate(d['frames'][1:],2):call('frame add',{**mutation(),'frame_number':i,'duration_ms':f['duration_ms']})
 for i,f in enumerate(d['frames'],1):
  for name in order:
   s=f['slots'][name]
   if s:call('image import',{**mutation(),'raster_file':str(prepared[s['asset']]),'target':{'layer':{'layer_name':name},'frame_number':i},'position':{'x':0,'y':0}})
 call('tag add',{**mutation(),'name':'pickup_candidate_NOT_APPROVED','from_frame':1,'to_frame':len(d['frames']),'direction':'forward','repeats':0})
 inspection=call('sprite get',{'sprite_file':str(target),'inspection_scope':['frames','layers','tags','cels']});save(out/'native-inspection.json',inspection);assert [f['duration_ms']for f in inspection['frames']]==[f['duration_ms']for f in d['frames']];assert [x['name']for x in sorted(inspection['layers'],key=lambda x:x['path'])]==order
 validation=call('sprite validate',{'sprite_file':str(target),'expected':{'width':d['canvas'][0],'height':d['canvas'][1],'color_mode':'rgb','frame_count':len(d['frames'])}});save(out/'native-validation.json',validation);assert validation['valid']and not validation['findings'],validation
 (out/'export').mkdir(exist_ok=True)
 for i in range(len(d['frames'])):call('export image',{'source_sprite_file':str(target),'frame_number':i+1,'export_image_area':{'kind':'canvas'},'layer_composition':{'mode':'visible'},'composition_color_mode':'preserve','color_mode':'preserve','color_profile':'preserve','transparency':'preserve','destination':{'path':str(out/'export'/f'{i:02}.png'),'if_exists':'fail'}})
 save(out/'editable-provenance.json',{'native_file_sha256':sha(target),'source_clip_sha256':sha(source),'durations_ms':[f['duration_ms']for f in d['frames']],'layers_bottom_to_top':order,'art_approval_granted':False,'source_art_status':d.get('art_status'),'source_head_status':d.get('head_extraction_status'),'source_declared_production_pass':d.get('production_pass',False),'scope':'Native editable copy; verify exported pixels and saved durations separately.'});print('Created native editable candidate:',target)
def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
 q=sub.add_parser('pack');q.add_argument('--clip',type=Path,required=True);q.add_argument('--frames',type=Path,required=True);q.add_argument('--out',type=Path,required=True);q.set_defaults(run=pack)
 q=sub.add_parser('editable');q.add_argument('--clip',type=Path,required=True);q.add_argument('--out',type=Path,required=True);q.add_argument('--aseprite',type=Path,default=ROOT/'work/tool-runtime/aseprite-build/bin/aseprite');q.add_argument('--spa',type=Path,default=ROOT/'work/tool-runtime/spa-env/bin/spa');q.set_defaults(run=editable)
 a=p.parse_args();a.run(a)
if __name__=='__main__':main()
