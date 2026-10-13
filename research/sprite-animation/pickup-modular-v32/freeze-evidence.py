import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths+=[ROOT/'skills/modular-eight-direction-sprites/scripts'/n for n in ('rigged-surface-observer.py','modular-motion-review.py','tests/test_modular_motion_review.py')]
paths+=[ROOT/'skills/modular-eight-direction-sprites/references/source-driven-part-motion.md']
rows=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(set(paths))]
inputs=[ROOT/'research/sprite-animation/pickup-pilot-v31/source/source.json',ROOT/'research/sprite-animation/joint-tracking-ro-v30/preset-source/Rig_Medium_General.glb',ROOT/'research/sprite-animation/joint-tracking-ro-v30/preset-source/KayKit-License.txt']
r={'schema':'v32-published-evidence-v1','files':rows,'external_source_inputs':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs],'bytes':sum(r['bytes'] for r in rows),'motion_review_pass':True,'full_factory_production_pass':False,'excluded':['__pycache__'],'scope':'One action/view agent motion review; protected publishedv30/v31 evidence retained unchanged.'};(P/'evidence-manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'files':len(rows),'bytes':r['bytes']}))
