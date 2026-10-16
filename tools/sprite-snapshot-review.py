"""Read-only content review for published v51+ original sprite research snapshots."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def evaluate():
 failures=[];count=0;cases=[]
 for p in sorted((ROOT/'research/sprite-animation').glob('*/evidence-manifest.json')):
  version=p.parent.name.rsplit('-v',1)[-1]
  if not version.isdigit()or int(version)<51:continue
  d=json.loads(p.read_text());assert d['path_base']=='repository_root';cases.append(p.parent.name)
  for r in d['files']:
   f=ROOT/r['path'];count+=1
   if not f.is_file()or hashlib.sha256(f.read_bytes()).hexdigest()!=r['sha256']:failures.append(r['path'])
 return {'pass':bool(cases)and not failures,'cases':cases,'leaf_checks':count,'failures':failures,'scope':'Payload integrity only, including preserved rejected experiments; never transfers approval.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();r=evaluate()
 if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r));raise SystemExit(0 if r['pass']else 1)
