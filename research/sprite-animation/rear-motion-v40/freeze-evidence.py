import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
q=json.loads((P/'audit-report.json').read_text());assert all(c['pass_'] for c in q['checks']) and not q['agent_motion_pass'] and not q['production_pass']
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths += [ROOT/'skills/modular-eight-direction-sprites/references/physical-view-phase-and-guide-fidelity.md']+[ROOT/'skills/modular-eight-direction-sprites/scripts'/n for n in ['physical-view-source-audit.py','visible-boot-components.py','view-conditioned-motion.py']]
files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(paths)]
(P/'evidence-manifest.json').write_text(json.dumps(dict(schema='v40-rejected-rear-view-evidence-v1',files=files,bytes=sum(r['bytes'] for r in files),decision=q['decision'],agent_motion_pass=False,production_pass=False),indent=2)+'\n');print(json.dumps(dict(files=len(files),bytes=sum(r['bytes'] for r in files))))
