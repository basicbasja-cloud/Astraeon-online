"""Real captured-layer counterfactuals, not self-certifying synthetic poses."""
from pathlib import Path
from PIL import Image
import importlib.util,json,copy,hashlib,tempfile
P=Path(__file__).resolve().parent;tool=P.parents[2]/'tools/sprite-layer-contact-review.py';sp=importlib.util.spec_from_file_location('review',tool);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);source=P/'S-front4-layer-contact-case.json';d=json.loads(source.read_text());checks={};assert m.evaluate(d,P)['layer_contact_pass'];checks['real_captured_positive']=True
for label,mutation in [
 ('empty_schedule',lambda c:c.update(frames=[])),
 ('missing_layer',lambda c:c['frames'][8]['layers'].pop('right_arm')),
 ('stale_composite',lambda c:c['frames'][8]['composite'].update(sha256='0'*64)),
 ('wrong_visible_foot_owner',lambda c:c['foot_windows'].update(right_leg=[270,480,345,515])),
 ('unobservable_roi',lambda c:c['foot_windows'].update(right_leg=[0,0,20,20])),
 ('oversized_rounding_budget',lambda c:c.update(rgba_rounding_budget=200)),
 ('vacuous_visibility_budget',lambda c:c.update(min_visible_baseline_fraction=0)),
 ('invalid_window_type',lambda c:c['foot_windows'].update(right_leg=[1,2,False,4])),
 ('invalid_distal_band',lambda c:c.update(distal_band_px=0))]:
 c=copy.deepcopy(d);mutation(c);assert not m.evaluate(c,P)['layer_contact_pass'],label;checks[label]=True
scratch=P.parents[2]/'work';scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as tmp:
 t=Path(tmp)
 for label,owner in [('translated_isolated_boot','right_leg'),('empty_occluder','right_arm'),('all_hidden_occluder','right_arm')]:
  c=copy.deepcopy(d);ref=c['frames'][8]['layers'][owner];im=Image.open(P/ref['path']).convert('RGBA')
  if label=='translated_isolated_boot':new=Image.new('RGBA',im.size);new.alpha_composite(im,(4,0))
  else:new=Image.new('RGBA',im.size,(0,0,0,255 if label=='all_hidden_occluder' else 0))
  f=t/(label+'.png');new.save(f);ref.update(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest());r=m.evaluate(c,P);assert not r['layer_contact_pass'],label;checks[label]=True
r={'pass':True,'checks':checks,'positive_case_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tool_sha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'scope':'Actual positive source/body rasters plus independent missing/stale/owner/occlusion/translated boot counterfactuals. Diagnostic mutation only; final art unchanged.'};(P/'layer-contact-tool-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(checks)
