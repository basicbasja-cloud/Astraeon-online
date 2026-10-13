"""Freeze published evidence; exclude models/raw game archives/full article caches."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];STUDY=Path(__file__).resolve().parent
paths=[p for p in STUDY.rglob('*') if p.is_file() and 'local-cache' not in p.parts and '__pycache__' not in p.parts and p.name!='evidence-manifest.json']
paths += [ROOT/'skills/modular-eight-direction-sprites/scripts'/name for name in ('joint-image-track.py','build-joint-grid-review.py','joint-track-reference-review.py','pose-image-proposals.py','requirements-joint-review.txt','tests/test_joint_image_track.py')]
paths += [ROOT/'skills/modular-eight-direction-sprites/references/image-joint-tracking-and-ro-coverage.md']
rows=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(set(paths))]
(STUDY/'evidence-manifest.json').write_text(json.dumps({'schema':'v30-published-evidence-manifest-v1','files':rows,'excluded':['local-cache: model weights, full raw RO raster banks/tables, archive, full article/code snapshots','__pycache__'],'total_bytes':sum(r['bytes'] for r in rows),'production_pass':False},indent=2)+'\n');print(json.dumps({'frozen_files':len(rows),'bytes':sum(r['bytes'] for r in rows)}))
