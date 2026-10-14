import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
paths=[p for p in P.rglob('*') if p.is_file() and 'local-cache' not in p.parts and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths+=[ROOT/'skills/modular-eight-direction-sprites/scripts'/n for n in ('hair-swap-review.py','tests/test_hair_swap_review.py')]
paths+=[ROOT/'skills/modular-eight-direction-sprites/references/hair-replacement-and-appearance-stability.md']
rows=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(set(paths))]
r={'schema':'v33-published-hair-evidence-v1','files':rows,'bytes':sum(r['bytes'] for r in rows),'approval':'AGENT_ONE_VIEW_HAIR_SWAP_REVIEW_PASS','full_factory_production_pass':False,'excluded':['local-cache: complete external HTML snapshots','__pycache__'],'scope':'Actual rendered replacement and unchanged-motion evidence for one camera/action. New artwork not user-approved.'};(P/'evidence-manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'files':len(rows),'bytes':r['bytes']}))
