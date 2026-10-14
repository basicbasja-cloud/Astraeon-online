from pathlib import Path
import json,copy,hashlib,importlib.util,tempfile,subprocess,sys
from PIL import Image,PngImagePlugin
P=Path(__file__).resolve().parent;ROOT=P.parents[2];script=ROOT/'skills/modular-eight-direction-sprites/scripts/painted-owner-continuity.py';spec=importlib.util.spec_from_file_location('owner',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);c=json.loads((P/'painted-owner-contract.json').read_text());n=json.loads((P/'painted-owner-negative-pixels.json').read_text());checks=[]
def check(name,ok):
 assert ok,name
 checks.append(dict(name=name,pass_=True))
q=m.audit(c,ROOT,n);check('actual paint swaps collecting owner between keys3and4',not q['temporal_owner_review_pass'] and q['observed_owner_changes']==[[3,4]])
check('missing image-side held-frame reviews remain UNKNOWN',q['frames'][5]['status']=='UNKNOWN' and q['frames'][6]['status']=='UNKNOWN')
d=copy.deepcopy(c);d['frames'][4]['review']['holding_owner']='right';check('relabeling known wrong current pixels cannot repair painting',not m.audit(d,ROOT,n)['checks']['no_known_rejected_pixels'])
d=copy.deepcopy(c);d['frames'].pop(4);check('cannot drop failing exposure',not m.audit(d,ROOT,n)['checks']['eight_required_exposures'])
d=copy.deepcopy(c);d['atlas']['sha256']='0'*64;check('stale source image binding fails',not m.audit(d,ROOT,n)['checks']['current_atlas_hash'])
d=copy.deepcopy(c);d['frames'][3]['review']['visible_chain']=[dict(xy=[0,0],uncertainty_px=1)];check('point outside current foreground cannot remain reviewed',m.audit(d,ROOT,n)['frames'][3]['status']=='UNKNOWN')
with tempfile.TemporaryDirectory() as td:
 td=Path(td);im=Image.open(ROOT/c['atlas']['path']).convert('RGBA');info=PngImagePlugin.PngInfo();info.add_text('not_a_repair','different PNG metadata, identical actual pixels');path=td/'metadata-only.png';im.save(path,pnginfo=info);d=copy.deepcopy(c);d['atlas']=dict(path=str(path),sha256=m.sha(path));check('new PNG filename/metadata cannot clear exact RGBA rejection',not m.audit(d,ROOT,n)['checks']['no_known_rejected_pixels'])
 im.putpixel((116,512+350),(255,0,0,255));path=td/'SYNTHETIC-changed-image.png';im.save(path);d=copy.deepcopy(c);d['atlas']=dict(path=str(path),sha256=m.sha(path));check('changed actual pixels invalidate old manual review instead of auto approving',m.audit(d,ROOT,n)['frames'][4]['status']=='UNKNOWN')
 r=subprocess.run([sys.executable,str(script),'--contract',str(P/'painted-owner-contract.json'),'--negatives',str(P/'painted-owner-negative-pixels.json'),'--root',str(ROOT),'--out',str(td/'q.json'),'--require-owner-review'],capture_output=True,text=True);check('actual strict current-image CLI returns1',r.returncode==1)
(P/'painted-owner-tests.json').write_text(json.dumps(dict(checks=checks,synthetic_mutations_are_not_artwork=True,production_pass=False),indent=2)+'\n');print(len(checks),'image-owner controls passed')
