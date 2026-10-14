import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
audit=json.loads((P/'audit-report.json').read_text());assert all(r['pass_'] for r in audit['checks']) and not audit['motion_pass']
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths+=[ROOT/'skills/modular-eight-direction-sprites/references/coherent-motion-repair-and-two-axis-review.md']
paths+=[ROOT/'skills/modular-eight-direction-sprites/scripts'/n for n in ['coherent-motion-spacing.py','coherent-strip-alpha.py','native-strip-edit-audit.py']]
rows=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(paths)]
(P/'evidence-manifest.json').write_text(json.dumps(dict(schema='v38-coherent-motion-two-axis-evidence-v1',files=rows,bytes=sum(r['bytes'] for r in rows),decision=audit['decision'],motion_pass=False,production_pass=False),indent=2)+'\n');print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows))))
