"""Read-only old-case verification with explicit manifest path conventions."""
from pathlib import Path
import json,hashlib,subprocess,argparse
ROOT=Path(__file__).resolve().parents[1]
# The four later publishers deliberately wrote paths relative to their case.
# Their own frozen verify.py scripts use P/leaf['path']; older schemas use ROOT.
CASE_RELATIVE={'painted-pickup-v47','pickup-sixteen-v48','pickup-contact-v49','grounded-actions-v50'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evaluate():
 failures=[];rows=[];count=0;sparse_verified=0;sparse={line[2:]for line in subprocess.check_output(['git','ls-files','-v'],cwd=ROOT,text=True).splitlines()if line.startswith('S ')};git=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for f in sorted((ROOT/'research/sprite-animation').glob('*/evidence-manifest.json')):
  if f.parent.name.rsplit('-v',1)[-1].isdigit() and int(f.parent.name.rsplit('-v',1)[-1])>50:continue
  base=f.parent if f.parent.name in CASE_RELATIVE else ROOT;d=json.loads(f.read_text());n=0
  for leaf in d.get('files',[]):
   p=(base/leaf['path']).resolve();n+=1;count+=1
   actual=None
   if p.is_relative_to(ROOT):
    rel=str(p.relative_to(ROOT))
    if p.is_file():actual=sha(p)
    elif rel in sparse:
     git.stdin.write(('HEAD:'+rel+'\n').encode());git.stdin.flush();header=git.stdout.readline().decode().strip().split()
     if len(header)==3 and header[1]=='blob':
      data=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n';actual=hashlib.sha256(data).hexdigest();sparse_verified+=1
   if actual!=leaf['sha256']:failures.append({'case':f.parent.name,'path':leaf['path'],'kind':'frozen'})
  rows.append({'manifest':str(f.relative_to(ROOT)),'manifest_sha256':sha(f),'path_base':str(base.relative_to(ROOT))or'.','leaves':n})
 git.stdin.close();git.stdout.close();git.wait()
 w=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/protected-W.json').read_text())
 for f in w['files']:
  p=ROOT/f['path']
  if not p.is_file()or sha(p)!=f['expected_sha256']:failures.append({'kind':'accepted_W','path':f['path']})
 changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines();unexpected=[p for p in changed if p!='CURRENT_HANDOFF.md']
 if unexpected:failures.append({'kind':'unexpected_tracked_change','paths':unexpected})
 return {'pass':not failures,'frozen_manifest_leaf_checks':count,'protected_W_files':len(w['files']),'sparse_excluded_leaves_verified_from_actual_HEAD_blobs':sparse_verified,'manifests':rows,'tracked_changes_at_test':changed,'failures':failures,'scope':'Actual payload byte integrity of published manifests throughv50, acceptedW13, and tracked-change guard. Existing files are hashed in workspace; only Git-declared sparse exclusions are read as actual HEAD blobs without materializing or rewriting old cases. Explicit case-relative conventions forv47..50 correct the older verifier assumption; no old file is rewritten.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();r=evaluate();s=json.dumps(r,indent=2)+'\n'
 if a.output:a.output.write_text(s)
 print({'pass':r['pass'],'leaves':r['frozen_manifest_leaf_checks'],'sparse_HEAD_blobs':r['sparse_excluded_leaves_verified_from_actual_HEAD_blobs'],'W_files':r['protected_W_files'],'failures':len(r['failures'])});raise SystemExit(0 if r['pass']else 1)
