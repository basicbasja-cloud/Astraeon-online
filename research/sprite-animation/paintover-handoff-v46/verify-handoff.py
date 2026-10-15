#!/usr/bin/env python3
"""Read-only verification of historical manifests, accepted W and delivered file inventory."""
from pathlib import Path
import hashlib, json, re, sys
from urllib.parse import unquote
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    failures=[]; count=0; manifests=[]
    for m in sorted((ROOT/'research/sprite-animation').glob('*/evidence-manifest.json')):
        manifests.append(str(m.relative_to(ROOT)))
        for leaf in json.loads(m.read_text()).get('files',[]):
            p=ROOT/leaf['path']; count+=1
            if not p.is_file() or sha(p)!=leaf['sha256']: failures.append({'kind':'frozen','path':leaf['path']})
    w=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/protected-W.json').read_text())
    for f in w['files']:
        p=ROOT/f['path']
        if not p.is_file() or sha(p)!=f['expected_sha256']: failures.append({'kind':'accepted_W','path':f['path']})
    ledger=json.loads((P/'generation-ledger.json').read_text())
    for j in ledger['jobs']:
        p=P/j['raw_path']
        if not p.is_file() or sha(p)!=j['raw_sha256']: failures.append({'kind':'raw_image','path':str(p)})
    inventory=P/'handoff/FILES.json'
    if inventory.exists():
        for f in json.loads(inventory.read_text())['files']:
            p=ROOT/f['path']
            if not p.is_file() or sha(p)!=f['sha256']: failures.append({'kind':'delivery_inventory','path':f['path']})
    else: failures.append({'kind':'missing_inventory'})
    for doc in [ROOT/'HANDOFF.md', P/'README.md', *sorted((P/'handoff').glob('*.md'))]:
        if not doc.exists(): failures.append({'kind':'missing_doc','path':str(doc)});continue
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            target=target.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'):continue
            q=doc.parent/unquote(target)
            if not q.exists(): failures.append({'kind':'broken_link','doc':str(doc.relative_to(ROOT)),'target':target})
    report={'handoff_integrity_pass':not failures,'historical_manifests':len(manifests),'historical_leaf_checks':count,'protected_W_files':len(w['files']),'raw_jobs':len(ledger['jobs']),'failures':failures,'production_pass':False,'scope':'Byte integrity and local handoff links only; NOT anatomy, motion quality, semantic segmentation, billing or license clearance.'}
    print(json.dumps(report,indent=2)); return 0 if not failures else 1
if __name__=='__main__':sys.exit(main())
