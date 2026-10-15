#!/usr/bin/env python3
"""Read-only v48 integrity check. A hash match is never motion/art acceptance."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
manifest=json.loads((P/'evidence-manifest.json').read_text())
failures=[]
for f in manifest['files']:
    p=P/f['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:failures.append(f['path'])
print(json.dumps({'integrity_pass':not failures,'checked':len(manifest['files']),'failures':failures,'production_pass':False}))
raise SystemExit(1 if failures else 0)
