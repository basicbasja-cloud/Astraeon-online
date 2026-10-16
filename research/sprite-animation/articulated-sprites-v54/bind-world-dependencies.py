"""Add dependency metadata to existing runs only after verifying their original full contract.
No measured outputs, images, verdicts or budgets are changed. Original full contracts and runner are retained.
"""
from pathlib import Path
import json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('foot',P.parents[2]/'tools/sprite-foot-binding.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();out=P/'world-proof-contracts';out.mkdir(exist_ok=True)
for v in ['S','SW','W','NW','N','NE','E','SE']:
 prefix='' if v=='W' else v+'-';f=P/(prefix+'world-foot-qa.json');r=json.loads(f.read_text());c=P/(prefix+'walk-rig-contract.json');d=json.loads(c.read_text());full=hashlib.sha256(json.dumps(m.normalize_numbers({k:d[k] for k in ['definitions','poses','world_offsets','source_sha256']}),sort_keys=True,separators=(',',':')).encode()).hexdigest();assert full==r['spatial_binding_sha256'],v
 snap=out/(v+'-original-contract.json');shutil.copyfile(c,snap);r.update({'foot_spatial_binding_sha256':m.foot_binding(d),'proof_contract_snapshot':str(snap.relative_to(P)),'proof_contract_sha256':sha(snap),'render_dependencies':{n:sha(P/'inputs'/n) for n in ['sprite-mesh-player.js','sprite-articulated-player.js']},'dependency_scope':'footFrame reads only leg textures/bindings/pose nodes, source reference and world offset. Full original contract retained. Body/head artwork is not consumed by this isolated diagnostic. Added metadata does not change any measured output or verdict.'});f.write_text(json.dumps(r,indent=2)+'\n');print(v,'original full binding verified; foot dependency key recorded')
shutil.copyfile(P/'check-world-feet.py',out/'original-check-world-feet.py');shutil.copyfile(P.parents[2]/'tools/sprite-foot-binding.py',P/'inputs/sprite-foot-binding.py')
