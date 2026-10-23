"""Check explicitly inspected local ownership landmarks, not global art quality."""
from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parent;probes=json.loads((p/'semantic-boundary-probes.json').read_text())['probes'];rows=[]
for probe in probes:
 name=f"{probe['frame']:03d}.png";xy=tuple(probe['xy']);master=p/'sequence/detail'/name;source=Image.open(master);owners=[r for r in ['HeadHair','BodyCostume','Weapon']if Image.open(p/'action-layer-proposals'/r/name).getpixel(xy)[3]>0];passed=source.getpixel(xy)[3]>16 and owners==[probe['role']];rows.append({**probe,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'actual_owners':owners,'passed':passed})
report={'status':'KNOWN_BOUNDARY_PROBES_PASS_NOT_FULL_SEMANTIC_ACCEPTANCE'if all(r['passed']for r in rows)else'KNOWN_BOUNDARY_PROBE_FAILURE','probes':rows,'owner_approved':False,'runtime_admitted':False};(p/'semantic-boundary-probe-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if all(r['passed']for r in rows)else 1)
