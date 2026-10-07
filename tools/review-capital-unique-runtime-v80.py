"""Wait for sealed native checks, then run transport/views and mobile serially.
No publishing or commit; human gameplay-image inspection remains required.
"""
import time,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';seal=O/'verified-source.json'
print('WAIT full current native validation seal',flush=True)
while not seal.exists():time.sleep(5)
s=json.loads(seal.read_text());assert s['pass'] and all(a['exitCode']==0 for a in s['steps']);assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==s['sourceSHA256']
for name,script in [('views','tools/review-capital-unique-views-v80.py'),('mobile','tools/review-capital-mobile-v80.py')]:
 print('START',name,flush=True)
 with (O/(name+'-pipeline.log')).open('w') as f:r=subprocess.run(['python3',script],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 print('END',name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
print('PASS runtime gates; human visual comparison and branch checkpoint pending',flush=True)
