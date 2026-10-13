import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
paths=[p for p in P.rglob('*') if p.is_file() and 'local-cache' not in p.parts and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths += [ROOT/'skills/modular-eight-direction-sprites/scripts'/p for p in ('image-surface-track.py','planted-surface-review.py','tests/test_planted_surface_review.py')]
paths += [ROOT/'skills/modular-eight-direction-sprites/references/pickup-pilot-and-surface-tracking.md']
rows=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(set(paths))]
external=[ROOT/'research/sprite-animation/joint-tracking-ro-v30/preset-source'/p for p in ('Rig_Medium_General.glb','KayKit-License.txt')]
receipt={'schema':'v31-published-evidence-v1','files':rows,'external_source_inputs':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in external],'bytes':sum(r['bytes'] for r in rows),'excluded':['local-cache: full external article snapshots','__pycache__'],'production_pass':False}
(P/'evidence-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'files':len(rows),'bytes':receipt['bytes']}))
