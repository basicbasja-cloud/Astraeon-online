"""Dependency-negative checks around an actual saved foot proof contract."""
from pathlib import Path
import json,copy,importlib.util
P=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('foot',P.parents[2]/'tools/sprite-foot-binding.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);d=json.loads((P/'world-proof-contracts/W-original-contract.json').read_text());r=json.loads((P/'world-foot-qa.json').read_text());base=m.foot_binding(d);assert base==r['foot_spatial_binding_sha256'];checks={'actual_saved_proof_key_matches':True}
for label,mut in [('head_art_not_read_by_foot_renderer',lambda x:x['definitions']['head'].update(texture_sha256='new-head')),('body_pose_not_read_by_foot_renderer',lambda x:x['poses'][0].update(head=[999,999]))]:
 c=copy.deepcopy(d);mut(c);assert m.foot_binding(c)==base;checks[label]=True
for label,mut in [('leg_art',lambda x:x['definitions']['left_leg'].update(texture_sha256='changed')),('leg_rest',lambda x:x['definitions']['left_leg']['rest']['left.ankle'].__setitem__(0,999)),('leg_pose',lambda x:x['poses'][0]['left.ankle'].__setitem__(0,999)),('world_travel',lambda x:x['world_offsets'][0].__setitem__(0,999)),('source_reference',lambda x:x.update(source_sha256='changed'))]:
 c=copy.deepcopy(d);mut(c);assert m.foot_binding(c)!=base;checks['invalidate_'+label]=True
assert m.normalize_numbers({'a':[-0.0,2.0]})=={'a':[0,2]};checks['browser_integral_number_serialization']=True
(P/'foot-binding-tests.json').write_text(json.dumps({'pass':True,'checks':checks,'scope':'Dependency identity only; actual raster verdicts remain in world-foot reports'},indent=2)+'\n');print(checks)
