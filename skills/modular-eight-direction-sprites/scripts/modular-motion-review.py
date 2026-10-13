"""Bound motion review for an authored part rig plus actual pixel observations.
Authoritative part identity comes from immutable authoring slots/binds, never
screen order or debug colors. Agent visual review is a separate signed receipt.
This approves one action/view only; it is not a generic anatomical detector.
"""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def apply(m,p):return [m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]
def bound(root,row):
 p=(root/row['path']).resolve()
 if not p.is_relative_to(root.resolve()) or sha(p)!=row['sha256']:raise ValueError('Stale/outside-root evidence: '+row['path'])
 return p
def review(case,root):
 checks=[]
 def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
 for row in case['evidence_inputs']:bound(root,row)
 P=(root/case['directory']).resolve();parts=json.loads((P/'parts.json').read_text())['parts'];byname={p['name']:p for p in parts}
 for p in parts:bound(root,{'path':p['file'],'sha256':p['sha256']})
 source=json.loads((root/case['source_json']).read_text());bound(root,{'path':source['source_file'],'sha256':source['source_sha256']})
 poses=json.loads((P/'poses.json').read_text());receipt=json.loads((P/'rig-bind-review.json').read_text());framecase=json.loads((P/'image-case.json').read_text());visual=json.loads((P/'visual-review.json').read_text());contract=json.loads((root/case['rig_contract']).read_text())
 scripts=Path(__file__).resolve().parent
 pixel=module('pixels',scripts/'rigged-surface-observer.py').observe(json.loads((P/'observer-case.json').read_text()),root)
 # Rerun observations instead of trusting earlier positive metrics/booleans.
 for i,f in enumerate(framecase['frames']):
  for name,track in pixel['tracks'].items():f['observations'][name]={k:v for k,v in track[i].items() if k in ('status','xy','uncertainty_px','anatomical_owner')}
 surface=module('surface',scripts/'planted-surface-review.py').audit(framecase,root)
 check('same declared 6px planted / .25 source-phase gates',framecase['planted_budget_px']==6 and framecase['reference_phase']['warning_fraction']==.25)
 check('actual RGBA surface measurements pass',surface['numerical_surface_check_pass'])
 check('8 actual source/pose/image times correspond',len(poses)==len(source['frames'])==len(framecase['frames'])==8 and all(abs(p['source_time_seconds']-source['frames'][i]['source_time_seconds'])<1e-8 and abs(framecase['frames'][i]['source_time_seconds']-source['frames'][i]['source_time_seconds'])<1e-8 for i,p in enumerate(poses)))
 check('complete ordered exported rig receipt matches authoring contract',len(receipt['frames'])==8 and [f['index'] for f in receipt['frames']]==list(range(8)) and receipt['chain']==contract['chains'])
 lengths=[];binds=[];owners=[];mirrors=[];footanchors=[]
 for i,f in enumerate(receipt['frames']):
  j=poses[i]['joints']
  check('exact16uniquepartslots frame'+str(i),len(f['rows'])==16 and len({r['name'] for r in f['rows']})==16)
  for r in f['rows']:
   part=byname[r['name']];m=r['matrix'];mirrors.append(m[0]*m[3]-m[1]*m[2]>0 and not part['mirrored']);owners.append(r['semantic_owner']==part['semantic_owner']==(r['name'].split('.')[0] if '.' in r['name'] else 'body') and r['texture_sha256']==part['sha256'])
   c=contract['chains'].get(r['name'])
   if c:
    binds.extend([math.dist(apply(m,part['pivot']),j[c[0]])<1e-6,math.dist(apply(m,part['end']),j[c[1]])<1e-6])
    if c[2]:lengths.append(abs(math.dist(j[c[0]],j[c[1]])-c[2])<1e-6)
   if r['name'].endswith('.foot'):
    n=r['name'].split('.')[0]+'.ankle';footanchors.extend([j[n]==contract['fixed_foot_anchors'][n],math.dist(apply(m,part['pivot']),j[n])<1e-6])
 check('constant valid fixed-length chains',all(lengths));check('all actual part endpoint binds match declared owner chain',all(binds));check('bound owned textures remain on original side',all(owners));check('no reflected part transforms',all(mirrors));check('two independently bound planted foot anchors',all(footanchors))
 check('pixel tracker did not consume future pose coordinates',not pixel['later_pose_coordinates_used'])
 check('agent visual review bound to exact current eight RGBA files',visual['reviewer']=='agent' and visual['decision']=='PASS_ONE_VIEW_MOTION' and visual['frames']==[{'path':f['path'],'sha256':f['sha256']} for f in framecase['frames']] and all(c['pass'] for c in visual['checks']))
 passed=all(c['pass'] for c in checks)
 phase=surface['markers'].get('surface.reaching_cuff',{}).get('source_relative_phase',[])
 return {'schema':'bounded-modular-motion-review-v1','motion_review_pass':passed,'approval':'AGENT_MOTION_REVIEW_PASS' if passed else 'BLOCKED','checks':checks,'observed_planted_range_px':{n:v['range_xy_px'] for n,v in surface['markers'].items() if 'boot' in n},'held_out_source_phase_max_difference':max((r['absolute_fraction_difference'] for r in phase if r['held_out']),default=None),'user_art_approved':False,'full_factory_production_pass':False,'hidden_image_anatomy_detected':False,'scope':case['scope']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=review(json.loads(a.case.read_text()),a.root);r['case_sha256']=sha(a.case);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'approval':r['approval'],'checks':len(r['checks'])}));raise SystemExit(0 if r['motion_review_pass'] else 1)
if __name__=='__main__':main()
