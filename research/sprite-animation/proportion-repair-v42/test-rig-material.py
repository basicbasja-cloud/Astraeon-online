"""Negative controls use temporary synthetic mutations, never final artwork."""
from pathlib import Path
import copy,hashlib,importlib.util,json,tempfile,subprocess,sys
import numpy as np
from PIL import Image,ImageFilter,ImageChops
P=Path(__file__).resolve().parent;ROOT=P.parents[2];script=ROOT/'skills/modular-eight-direction-sprites/scripts/rig-material-continuity.py';s=importlib.util.spec_from_file_location('rigqa',script);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=json.loads((P/'rig-continuity-contract.json').read_text());q=m.run(c,ROOT);checks=[]
def check(name,ok):
 assert ok,name
 checks.append(dict(name=name,pass_=True))
def bind(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
check('current actual22 bounded rig checks pass',len(q['checks'])==22 and q['bounded_rig_metrics_pass'])
check('all8arm/shin material sections vary<=2px',all(x['range_px'][1]-x['range_px'][0]<=2 for x in q['widths'].values()))
check('both neutral399px/floor480 and exact full-character pixels',q['checks']['approved_neutral_height_and_ground'] and q['checks']['identical_neutral_character_pixels'])
check('actual painted supports stationary and item touches picking hand',q['checks']['stationary_painted_feet'] and q['contact_pixel_distance']==0)
check('three runtime passes actually reproduce body/head composition',q['checks']['two_logical_slots_three_pass_exact_recomposition'])
check('new view does not inherit family/art/production acceptance',not q['agent_art_approval'] and not q['production_pass'] and q['full_family_proportion_status'].startswith('UNKNOWN'))
d=copy.deepcopy(c);d['sections'].pop('left.forearm');check('cannot omit one arm measurement',not m.run(d,ROOT)['checks']['required_material_sections'])
d=copy.deepcopy(c);d['support_windows'].pop('right.foot');check('cannot omit hidden/far foot requirement',not m.run(d,ROOT)['checks']['two_required_feet_observed'])
d=copy.deepcopy(c);d['frames'][4]['full']['sha256']='0'*64;check('stale image binding cannot pass',not m.run(d,ROOT)['checks']['input_hashes'])
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 d=copy.deepcopy(c);f=d['frames'][3];im=m.image(ROOT,f['isolated']['left.forearm']);im.putalpha(im.getchannel('A').filter(ImageFilter.MaxFilter(11)));p=td/'SYNTHETIC-expanded-bracer.png';im.save(p);f['isolated']['left.forearm']=bind(p);test=m.run(d,ROOT);check('newly hashed swollen bracer is caught by actual pixels',not test['checks']['all_reviewed_material_sections'])
 d=copy.deepcopy(c);f=d['frames'][3];im=m.image(ROOT,f['full']);out=Image.new('RGBA',im.size);out.paste(im,(4,0));p=td/'SYNTHETIC-shifted-character.png';out.save(p);f['full']=bind(p);test=m.run(d,ROOT);check('newly hashed4px frame bounce breaks support and composition',not test['checks']['stationary_painted_feet'] and not test['checks']['two_logical_slots_three_pass_exact_recomposition'])
 d=copy.deepcopy(c);f=d['frames'][3];im=m.image(ROOT,f['prop']);out=Image.new('RGBA',im.size);out.paste(im,(35,0));p=td/'SYNTHETIC-floating-item.png';out.save(p);f['prop']=bind(p);test=m.run(d,ROOT);check('floating item fails real contact/source/scene checks',not test['checks']['actual_hand_item_rasters_touch'] and not test['checks']['actual_item_pixels_follow_source'] and not test['checks']['actual_scene_recomposition'])
 d=copy.deepcopy(c);b=json.loads((ROOT/d['rig_binding']['path']).read_text());b['frames'][3]['source_points']['left.elbow'][0]+=10;p=td/'SYNTHETIC-false-bone-point.json';p.write_text(json.dumps(b));d['rig_binding']=bind(p);test=m.run(d,ROOT);check('newly hashed false joint cannot masquerade as source projection',not test['checks']['independent_source_camera_projection'] and not test['checks']['authored_chain_attachment_error'])
 d=copy.deepcopy(c);b=json.loads((ROOT/d['rig_binding']['path']).read_text());b['assets']['left.forearm']['chain']=['right.elbow','right.wrist'];p=td/'SYNTHETIC-swapped-owner.json';p.write_text(json.dumps(b));d['rig_binding']=bind(p);test=m.run(d,ROOT);check('changing owner labels cannot repair an arm',not test['checks']['declared_owner_chains'] and not test['checks']['authored_chain_attachment_error'])
 results=[]
 for flag in ['--require-metrics','--require-production']:
  r=subprocess.run([sys.executable,str(script),'--contract',str(P/'rig-continuity-contract.json'),'--root',str(ROOT),'--out',str(td/(flag[2:]+'.json')),flag],capture_output=True,text=True);results.append(dict(flag=flag,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 check('actual metric CLI exits0, production CLI exits1',results[0]['returncode']==0 and results[1]['returncode']==1)
 (P/'strict-gate-receipt.json').write_text(json.dumps(dict(commands=results,scope='Bounded rig metrics are executable; unknown full family/art acceptance still blocks production.'),indent=2)+'\n')
(P/'test-receipt.json').write_text(json.dumps(dict(checks=checks,synthetic_mutations_are_not_artwork=True,production_pass=False),indent=2)+'\n');print(len(checks),'meaningful rig-material regression controls passed')
