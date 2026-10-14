import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
audit=json.loads((P/'audit-report.json').read_text())
if audit.get('approval')!='AGENT_SECOND_VIEW_PART_MOTION_REVIEW' or not audit.get('checks') or not all(c['pass_'] for c in audit['checks']):
 raise ValueError('Refuse evidence freeze before a completed passing audit')
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths += [ROOT/'skills/modular-eight-direction-sprites/scripts'/n for n in ['directional-part-review.py','rigid-surface-observer-v2.py','tests/test_directional_part_review.py','tests/test_rigid_surface_observer_v2.py']]
paths += [ROOT/'skills/modular-eight-direction-sprites/references/physical-view-and-texture-support.md']
rows=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(set(paths))]
(P/'evidence-manifest.json').write_text(json.dumps(dict(schema='v34-published-physical-view-evidence-v1',files=rows,bytes=sum(r['bytes'] for r in rows),approval='AGENT_SECOND_VIEW_PART_MOTION_REVIEW',user_new_art_approved=False,full_factory_production_pass=False),indent=2)+'\n');print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows))))
