import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];audit=json.loads((P/'audit-report.json').read_text());assert audit.get('checks') and all(r['pass_'] for r in audit['checks'])
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']+[ROOT/'skills/modular-eight-direction-sprites/references/body-outfit-production-slots.md']
rows=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(paths)]
(P/'evidence-manifest.json').write_text(json.dumps(dict(schema='v35-body-outfit-slot-evidence-v1',files=rows,bytes=sum(r['bytes'] for r in rows),decision='TWO_LOGICAL_SLOTS_VERIFIED_PROPORTION_CANDIDATE',user_proportion_approved=False,animation_pass=False,production_pass=False),indent=2)+'\n');print(json.dumps(dict(files=len(rows))))
