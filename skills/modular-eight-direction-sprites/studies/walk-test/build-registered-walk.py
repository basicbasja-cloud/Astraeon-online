"""New review bank from preserved v20 masters; recompute after registration."""
import copy, hashlib, importlib.util, json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OLD=ROOT/'research/sprite-animation/eight-walk-factory-v20';OUT=ROOT/'research/sprite-animation/registered-walk-attack-v21';VIEWS=['S','SE','E','NE','N','NW','W','SW']
def module(name):
 p=ROOT/'skills/modular-eight-direction-sprites/scripts'/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clip(out,images,times,loop=True):
 images[0].save(out.with_suffix('.png'),save_all=True,append_images=images[1:],duration=times,loop=0 if loop else 1,disposal=0,blend=0)
 opaque=[]
 for im in images:
  b=Image.new('RGBA',im.size,'#272727');b.alpha_composite(im);opaque.append(b.convert('RGB'))
 strip=Image.new('RGB',(opaque[0].width*len(opaque),opaque[0].height))
 for i,im in enumerate(opaque):strip.paste(im,(i*im.width,0))
 pal=strip.quantize(colors=256);g=[im.quantize(palette=pal,dither=Image.Dither.NONE) for im in opaque];kw={'loop':0} if loop else {};edges=[0]
 for t in times:edges.append(edges[-1]+t)
 gif_times=[round(edges[i+1]/10)*10-round(edges[i]/10)*10 for i in range(len(times))];g[0].save(out.with_suffix('.gif'),save_all=True,append_images=g[1:],duration=gif_times,optimize=False,disposal=2,**kw)
def main():
 import os;os.chdir(ROOT);source=json.loads((OLD/'source-phase12/source-index.json').read_text());summary=[];history={'schema':'source-context-image-issue-history-v1','issues':[]};pending=[]
 for view in VIEWS:
  p=OLD/'evidence'/(view+'-motion-case.json');case=json.loads(p.read_text());case['case_path']=str(p.relative_to(ROOT));old=json.loads((OLD/'evidence'/(view+'-motion-report.json')).read_text());records=[r for r in source['records'] if r['facing']==view];folder=OUT/'walk'/view
  if view=='S':
   raw=OUT/'raw/S-attempt2.png';sheet=Image.open(raw).convert('RGBA');assert sheet.size==(1536,1024)
   for i,f in enumerate(case['frames']):
    im=Image.new('RGBA',(512,512));im.paste(sheet.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512)),(64,0));dest=folder/'before-registration'/f'{i:02}.png';dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest);f['image']=str(dest.relative_to(ROOT));f['sha256']=sha(dest);f['review_issues']=[]
   case.pop('case_path');input_case=OUT/'evidence/S-repaint-input-case.json';save(input_case,case);case['case_path']=str(input_case.relative_to(ROOT));old=module('sprite-motion-audit').audit(case);old['case_sha256']=sha(input_case);save(OUT/'evidence/S-repaint-input-report.json',old)
  reg=module('sprite-registration').register(case,records,old,folder/'frames');save(folder/'registration.json',reg)
  new=copy.deepcopy(case);new.pop('case_path');new['budgets']['max_horizontal_step_px']=3;new['budgets']['max_vertical_step_px']=3;new['budgets']['max_vertical_range_px']=6;new['budget_scope']='Strict calibrated head-surface registration warnings at512px; physical contacts/owners remain separate unresolved gates.'
  for f,row in zip(new['frames'],reg['rows']):
   f['image']=row['output'];f['sha256']=row['output_sha256'];f['registration_parent_sha256']=row['input_sha256']
   # Never erase a known rejected pose merely because it was translated.
   for issue in old['confirmed_image_issues']:
    if issue['key']==f['key']:
     inherited={k:v for k,v in issue.items() if k not in ['key','image_sha256']};inherited.update(image_sha256=f['sha256'],facing=view,source_key16=f['source_key16'],registration_parent_sha256=row['input_sha256']);history['issues'].append(inherited);f['review_issues'].append({'confirmed':True,'kind':inherited['kind'],'description':'Inherited unchanged-pose rejection after rigid registration: '+inherited['description']})
  pending.append((view,folder,new,old))
 history_path=OUT/'evidence/review-history.json';save(history_path,history)
 for view,folder,case,old in pending:
  case['review_history']={'path':str(history_path.relative_to(ROOT)),'sha256':sha(history_path)};cp=OUT/'evidence'/(view+'-motion-case.json');save(cp,case);report=module('sprite-motion-audit').audit(case);report['case_sha256']=sha(cp);save(OUT/'evidence'/(view+'-motion-report.json'),report)
  summary.append({'view':view,'before_vertical_step_px':old['surface_axis_metrics']['max_vertical_step_px'],'after_vertical_step_px':report['surface_axis_metrics']['max_vertical_step_px'],'after_horizontal_step_px':report['surface_axis_metrics']['max_horizontal_step_px'],'after_vertical_range_px':report['surface_axis_metrics']['vertical_range_px'],'status':report['status'],'contact_status':'UNKNOWN','anatomy_status':'UNRESOLVED','calibrated_surface_warning_count':len(report['surface_axis_metrics']['warnings']),'calibrated_surface_range_warning':report['surface_axis_metrics']['vertical_range_warning']})
  images=[Image.open(f['image']).convert('RGBA') for f in case['frames']];clip(folder/'walk-uniform-800ms',images,[100]*8);clip(folder/'walk-reference-600ms',images,[75]*8)
  sheet=Image.new('RGBA',(2048,1024))
  for i,im in enumerate(images):sheet.alpha_composite(im,(i%4*512,i//4*512))
  sheet.save(folder/'eight-frames.png')
 mosaics=[];comparison=[]
 for i in range(8):
  b=Image.new('RGBA',(1024,560),'#272727');d=ImageDraw.Draw(b);c=Image.new('RGBA',(1024,544),'#272727');cd=ImageDraw.Draw(c)
  for n,v in enumerate(VIEWS):
   im=Image.open(OUT/'walk'/v/'frames'/f'{i:02}.png').resize((256,256));b.alpha_composite(im,(n%4*256,n//4*280+24));d.text((n%4*256+8,n//4*280+5),v,fill='white')
  for n,v in enumerate(['W','SE','NE','SW']):
   for row,path in enumerate([OLD/'candidates'/v/'frames'/f'{i:02}.png',OUT/'walk'/v/'frames'/f'{i:02}.png']):c.alpha_composite(Image.open(path).convert('RGBA').resize((256,256)),(n*256,row*272+16));cd.text((n*256+6,row*272+2),v+(' BEFORE' if row==0 else ' REGISTERED'),fill='white')
  mosaics.append(b);comparison.append(c)
 clip(OUT/'walk-eight-directions',mosaics,[100]*8);clip(OUT/'walk-before-after',comparison,[100]*8);save(OUT/'evidence/walk-registration-summary.json',{'views':summary,'artwork_pose_changed_views':['S'],'registered_without_pose_edit_views':VIEWS[1:],'root_or_contact_pass':False,'new_approval':False})
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
