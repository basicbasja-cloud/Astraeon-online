"""Build exact source streaming, bump current cache, capture ordinary gameplay."""
import subprocess,json,hashlib,os,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';seal=json.loads((O/'verified-source.json').read_text());assert seal['pass'] and hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==seal['sourceSHA256'];env=os.environ.copy();env['ASTRAEON_CAPITAL_REVIEW_DIR']='docs/review/wayfarer-capital-v80'
steps=[('transport-build',['node','--max-old-space-size=6000','tools/build-world-streaming.mjs']),('transport-check',['node','--max-old-space-size=4000','tools/check-world-streaming.mjs']),('streaming-tests',['node','--test-reporter=tap','tests/world_streaming.test.mjs']),('default-captures',['python3','tools/capture-wayfarer-views.py','--output',str(O/'views'),'--views','street-west,plaza-frontages,street-artisan,merchant-frontage,willow-court,artisan-court,hall-terrace,riverwatch','--width','910','--height','512','--scene-only','--verify-culling','--startup-timeout-ms','180000','--template-file','docs/review/wayfarer-capital-v78/frontage-placement/views/fixture-save.json']),('camera-controls',['python3','tools/check-capital-camera-v76.py','--output',str(O/'camera-controls')])]
ap=argparse.ArgumentParser();ap.add_argument('--from-stage',choices=[a for a,_ in steps]);args=ap.parse_args()
if args.from_stage:steps=steps[[a for a,_ in steps].index(args.from_stage):]
for name,cmd in steps:
 print('START',name,flush=True)
 with (O/(name+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);print('END',name,flush=True)
 if name=='transport-check':
  for fname in ('boot.js','index.html','sw.js'):
   f=R/fname;t=f.read_text()
   if fname=='boot.js':assert "const version='94';" in t;t=t.replace("const version='94';","const version='95';")
   elif fname=='index.html':assert '?v=94' in t;t=t.replace('?v=94','?v=95')
   else:assert 'astraeon-static-v94' in t;t=t.replace('-v94','-v95').replace('?v=94','?v=95')
   f.write_text(t)
print('PASS current transport, ordinary default views and camera controls; human visual review required',flush=True)
