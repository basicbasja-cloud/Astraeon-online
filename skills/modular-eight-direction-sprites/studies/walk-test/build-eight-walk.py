"""Package immutable W and seven fresh facing drafts with honest review gates."""
import base64, gzip, hashlib, importlib.util, json, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[4];STUDY=ROOT/'research/sprite-animation/eight-walk-factory-v20';VIEWS=['S','SE','E','NE','N','NW','W','SW']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def module(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def clip(folder,frames,dt,name):
 ims=[Image.open(p).convert('RGBA') for p in frames];ims[0].save(folder/(name+'.png'),save_all=True,append_images=ims[1:],duration=dt,loop=0,disposal=0,blend=0)
 opaque=[];strip=Image.new('RGB',(512*len(ims),512),'#272727')
 for i,im in enumerate(ims):
  bg=Image.new('RGBA',im.size,'#272727');bg.alpha_composite(im);opaque.append(bg.convert('RGB'));strip.paste(opaque[-1],(i*512,0))
 palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);gif=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in opaque];times=[round((i+1)*dt/10)*10-round(i*dt/10)*10 for i in range(len(ims))]
 gif[0].save(folder/(name+'.gif'),save_all=True,append_images=gif[1:],duration=times,loop=0,disposal=2,optimize=False)
 rows=[]
 for suffix in ['png','gif']:
  p=folder/(name+'.'+suffix)
  with Image.open(p) as im:
   ts=[]
   for i in range(im.n_frames):im.seek(i);ts.append(im.info['duration'])
   assert im.n_frames==len(frames) and abs(sum(ts)-len(frames)*dt)<1e-6
   rows.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'frames':im.n_frames,'decoded_duration_ms':ts})
 return rows
def url(p):return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
def main():
 import os;os.chdir(ROOT);source_path=STUDY/'source-phase12/source-index.json';source=json.loads(source_path.read_text());evidence=STUDY/'evidence';formats=[];banks=[];reports=[];sheets=Image.new('RGB',(2048,8*536),'#272727');sd=ImageDraw.Draw(sheets)
 for v,view in enumerate(VIEWS):
  folder=STUDY/'candidates'/view;fp=folder/'frames';fp.mkdir(parents=True,exist_ok=True);records=[r for r in source['records'] if r['facing']==view];frames=[];source_clock=[]
  if view=='W':
   feedback=json.loads((ROOT/'research/sprite-animation/reverse-paintover-v19/evidence/user-eight-key-smoothness-feedback.json').read_text())
   for i,f in enumerate(feedback['frames']):
    src=ROOT/f['path'];assert sha(src)==f['sha256'];dest=fp/f'{i:02}.png';shutil.copyfile(src,dest);frames.append(dest)
   pack={'mode':'EXACT_EXISTING_W_KEYS','source_feedback_sha256':sha(ROOT/'research/sprite-animation/reverse-paintover-v19/evidence/user-eight-key-smoothness-feedback.json'),'artwork_changed':False,'user_feedback':'Animation looks better, but still bounces slightly. No zero-bounce acceptance.'}
  else:
   raw=STUDY/'raw'/(view+'-attempt1.png');im=Image.open(raw).convert('RGBA');assert im.size==(1536,1024)
   for i in range(8):
    x=i%4*384;y=i//4*512;cell=im.crop((x,y,x+384,y+512));a=np.array(cell)[:,:,3]
    if max(a[0].max(),a[-1].max(),a[:,0].max(),a[:,-1].max())>64:raise ValueError('Foreground cut at '+view+str(i))
    f=Image.new('RGBA',(512,512));f.paste(cell,(64,0));p=fp/f'{i:02}.png';f.save(p);frames.append(p)
   pack={'mode':'SHARED_FIXED_GRID','raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),'shared_scale':1,'shared_padding':[64,0],'per_frame_fit':False,'source_conditioning_phase_offset':4,'new_pixels_approved':False}
  save(folder/'pack.json',pack);formats+=clip(folder,frames,75,'walk-600ms');formats+=clip(folder,frames,100,'walk-uniform-800ms')
  history_path=evidence/'review-history.json'
  if view=='S':save(history_path,{'schema':'source-context-image-issue-history-v1','issues':[{'image_sha256':sha(frames[6]),'facing':'S','source_key16':records[6]['source_key16'],'confirmed':True,'kind':'phase_discrepancy','reviewer':'assistant actual source/art image inspection','description':'For this assigned front contact phase7, source leads screen-left but painted frame again leads screen-right. Pixel-bound review survives removal/relabeling of local frame flags.'}]})
  fs=[]
  for i,p in enumerate(frames):
   issues=[]
   if view=='S' and i==6:issues=[{'confirmed':True,'kind':'phase_discrepancy','description':'Front source contact phase7 leads screen-left, but this drawing again leads screen-right like phase3. This is visible lead-pattern evidence, not recovered hidden hip coordinates.'}]
   fs.append({'key':i,'image':str(p.relative_to(ROOT)),'sha256':sha(p),'duration_ms':75,'source_key16':records[i]['source_key16'],
    'anatomical_review':{'status':'unconfirmed','r':{'kind':'unknown','trace_xy':[]},'l':{'kind':'unknown','trace_xy':[]}},
    'logical_root_observed_xy':None,'contact_review':'unknown','review_issues':issues})
  case={'schema':'sprite-motion-case-v1','facing':view,'canvas':[512,512],'loop':True,'frames':fs,
   'source':{'path':str(source_path.relative_to(ROOT)),'sha256':sha(source_path),'correspondence':'approximate_RO_pose_comparison_rechecked_phase12'},
   'review_history':{'path':str(history_path.relative_to(ROOT)),'sha256':sha(history_path)},
   'palette_patch_probe':{'roi':[80,0,400,245],'max_hsv_saturation_255':110,'min_hsv_value_255':75,'min_blue_green_ratio':.88,'min_red_green_ratio':.88,'minimum_pixels':100},
   'budgets':{'max_horizontal_step_px':20,'max_vertical_step_px':8,'max_vertical_range_px':12},
   'budget_scope':'Provisional512px head-surface warnings after user reports residual bounce; not naturalness or identity accuracy.',
   'flow_settings':{'diagnostic_size':256,'max_forward_backward_error_px':1.5,'minimum_consistent_fraction':.5},'complete_parts_adapter':None}
  save(evidence/(view+'-motion-case.json'),case);report=module('sprite-motion-audit').audit(case);save(evidence/(view+'-motion-report.json'),report);reports.append(report)
  mini=Image.new('RGBA',(2048,1024))
  for i,p in enumerate(frames):mini.alpha_composite(Image.open(p).convert('RGBA'),(i%4*512,i//4*512))
  mini=mini.resize((1024,512),Image.Resampling.LANCZOS);sheets.paste(mini,(0,v*536+24),mini);sd.text((8,v*536+5),view+' / eight painted drafts; '+report['status'],fill='white')
  # Put genuine source owner samples beside that direction's art bank.
  for i,r in enumerate(records):
   im=Image.open(r['paths']['dressed-owner']).convert('RGBA').resize((256,256));sheets.paste(im,(1024+i%4*256,v*536+24+i//4*256),im)
  ro=ROOT/'research/sprite-animation/motion-reference-v6/ro'/('walk-'+view);cap=json.loads((ro/'capture.json').read_text())
  banks.append({'facing':view,'art':[url(p) for p in frames],'owner':[url(r['paths']['dressed-owner']) for r in records],
    'cutaway':[url(r['paths']['cutaway-owner']) for r in records],'RO':[url(ro/f['file']) for f in cap['frames']],
    'bones':[r['bones'] for r in records],'metrics':report['surface_axis_metrics'],'blockers':report['blockers'],'status':report['status']})
 sheets.save(evidence/'paint-source-all-64.png');save(evidence/'decoded-format-clocks.json',formats)
 save(evidence/'summary.json',{'views':[{'facing':r['facing'],'status':r['status'],'max_vertical_step_px':r['surface_axis_metrics']['max_vertical_step_px'] if r['surface_axis_metrics'] else None,'vertical_range_px':r['surface_axis_metrics']['vertical_range_px'] if r['surface_axis_metrics'] else None,'blockers':r['blockers']} for r in reports],'frames':64,'production_ready':False,'W_original_pixels_preserved':True})
 mosaic=[]
 for i in range(8):
  b=Image.new('RGBA',(1024,560),'#272727');d=ImageDraw.Draw(b)
  for v,view in enumerate(VIEWS):
   im=Image.open(STUDY/'candidates'/view/'frames'/f'{i:02}.png').resize((256,256),Image.Resampling.LANCZOS);b.alpha_composite(im,(v%4*256,v//4*280+24));d.text((v%4*256+8,v//4*280+6),view,fill='white')
  mosaic.append(b)
 mosaic[0].save(STUDY/'eight-directions-600ms.png',save_all=True,append_images=mosaic[1:],duration=75,loop=0,disposal=0,blend=0)
 strip=Image.new('RGB',(1024*8,560))
 for i,b in enumerate(mosaic):strip.paste(b.convert('RGB'),(i*1024,0))
 pal=strip.quantize(colors=256);g=[b.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE) for b in mosaic]
 g[0].save(STUDY/'eight-directions-uniform-800ms.gif',save_all=True,append_images=g[1:],duration=100,loop=0,optimize=False,disposal=2)
 raw=json.dumps(banks,ensure_ascii=False,indent=2).encode();archive=evidence/'viewer-data.json.gz';archive.write_bytes(gzip.compress(raw,mtime=0))
 save(evidence/'viewer-data-archive.json',{'archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive),'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'lossless':True})
 print('EIGHT_WALK 64real artframes/64sourceposes; W preserved; unresolved/confirmed issues retained')

if __name__=='__main__':main()
