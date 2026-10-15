#!/usr/bin/env python3
"""Read-only evidence integrity; never art/anatomy approval."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
m=json.loads((P/'evidence-manifest.json').read_text());bad=[]
for f in m['files']:
 p=P/f['path']
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:bad.append(f['path'])
print(json.dumps({'integrity_pass':not bad,'checked':len(m['files']),'failures':bad,'production_pass':False}))
raise SystemExit(1 if bad else 0)
