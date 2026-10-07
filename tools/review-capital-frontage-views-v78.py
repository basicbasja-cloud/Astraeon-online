"""Exact current-source transport, ordinary default captures and angle studies.
Run only after all native pipeline stages pass. One browser at a time.
"""
import subprocess,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v78/frontage-placement'
seal=json.loads((O/'verified-source.json').read_text());assert seal['pass']
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==seal['sourceSHA256']
env=os.environ.copy();env['ASTRAEON_CAPITAL_REVIEW_DIR']='docs/review/wayfarer-capital-v78'
def run(name,cmd):
 print('START',name,flush=True)
 with (O/(name+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);print('END',name,flush=True)
run('transport-build',['node','--max-old-space-size=6000','tools/build-world-streaming.mjs'])
run('transport-check',['node','--max-old-space-size=4000','tools/check-world-streaming.mjs'])
for name in ('boot.js','index.html','sw.js'):
 f=R/name;text=f.read_text()
 if name=='boot.js':assert "const version='93';" in text;text=text.replace("const version='93';","const version='94';")
 elif name=='index.html':assert '?v=93' in text;text=text.replace('?v=93','?v=94')
 else:assert "astraeon-static-v93" in text;text=text.replace('-v93','-v94').replace('?v=93','?v=94')
 f.write_text(text)
run('streaming-tests',['node','--test-reporter=tap','tests/world_streaming.test.mjs'])
run('default-captures',['python3','tools/capture-wayfarer-views.py','--output',str(O/'views'),
 '--views','street-west,plaza-frontages,street-artisan,merchant-frontage,willow-court,artisan-court,hall-terrace,riverwatch',
 '--width','910','--height','512','--scene-only','--verify-culling','--startup-timeout-ms','180000',
 '--template-file','docs/review/wayfarer-capital-v77/street-depth/views/fixture-save.json'])
run('camera-study',['python3','tools/study-capital-ro3-camera-v76.py','--output',str(O/'camera-study'),
 '--profiles','45-30-125,45-35-135,50-30-125'])
print('PASS source-matched captures and ordinary camera studies; visual review pending',flush=True)
