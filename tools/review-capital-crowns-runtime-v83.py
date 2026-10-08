"""Exact v83 stream/cache98 and serial ordinary browser/mobile verification."""
import json,hashlib,subprocess,os,time,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v83';V=O/'layered-crowns'
ap=argparse.ArgumentParser();ap.add_argument('--from-stage');ap.add_argument('--wait-for-native',action='store_true');args=ap.parse_args()
if args.wait_for_native:
    while not (V/'verified-source.json').exists():
        progress=V/'progress.json'
        if progress.exists():
            records=json.loads(progress.read_text())
            if records and records[-1]['exitCode']:
                raise SystemExit('Native review failed; runtime verification remains blocked')
        time.sleep(5)
seal=json.loads((V/'verified-source.json').read_text());assert seal['pass']
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==seal['sourceSHA256']
env=os.environ.copy();env['ASTRAEON_CAPITAL_REVIEW_DIR']='docs/review/wayfarer-capital-v83'
env['LD_LIBRARY_PATH']='/workspace/.cache/astraeon-webkit-libs/usr/lib/x86_64-linux-gnu'
steps=[('transport-build',['node','--max-old-space-size=6000','tools/build-world-streaming.mjs']),
       ('transport-check',['node','--max-old-space-size=4000','tools/check-world-streaming.mjs']),
       ('streaming-tests',['node','--test-reporter=tap','tests/world_streaming.test.mjs']),
       ('normal-captures',['python3','tools/capture-wayfarer-views.py','--output',str(V/'views'),'--views','street-west,plaza-frontages,street-artisan,merchant-frontage,willow-court,artisan-court,hall-terrace,riverwatch','--width','910','--height','512','--scene-only','--verify-culling','--startup-timeout-ms','180000','--template-file','docs/review/wayfarer-capital-v78/frontage-placement/views/fixture-save.json']),
       ('camera-controls',['python3','tools/check-capital-camera-v76.py','--output',str(V/'camera-controls')]),
       ('mobile-touch',['python3','tests/mobile_streaming.py','--engine','webkit','--legs','128,150;80,200;13.4,144;128,150','--output',str(O/'mobile-streaming/ordinary-touch-v83')]),
       ('cache-offline',['python3','tests/cache_resume.py','--output',str(O/'cache-resume'),'--startup-timeout-ms','180000']),
       ('field-return',['python3','tests/mobile_field_return.py','--output',str(O/'mobile-field-return')])]
assert args.from_stage is None or args.from_stage in [n for n,_ in steps]
records=[]
if args.from_stage:
    i=[n for n,_ in steps].index(args.from_stage);records=json.loads((V/'runtime-progress.json').read_text())[:i]
    assert len(records)==i and all(a['exitCode']==0 for a in records);steps=steps[i:]
for name,cmd in steps:
    print('START',name,time.strftime('%H:%M:%S'),flush=True);start=time.monotonic()
    with (V/(name+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
    records.append({'name':name,'exitCode':r.returncode,'seconds':round(time.monotonic()-start,1)})
    (V/'runtime-progress.json').write_text(json.dumps(records,indent=2)+'\n')
    print('END',name,r.returncode,flush=True)
    if r.returncode:raise SystemExit(r.returncode)
    if name=='transport-check':
        for name in ('boot.js','index.html','sw.js'):
            f=R/name;t=f.read_text()
            if name=='boot.js':assert "const version='97';" in t;t=t.replace("const version='97';","const version='98';")
            elif name=='index.html':assert '?v=97' in t;t=t.replace('?v=97','?v=98')
            else:assert 'astraeon-static-v97' in t;t=t.replace('-v97','-v98').replace('?v=97','?v=98')
            f.write_text(t)
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==seal['sourceSHA256']
(V/'runtime-verified.json').write_text(json.dumps({'sourceSHA256':seal['sourceSHA256'],
    'runtimeSHA256':hashlib.sha256((R/'world-view.js').read_bytes()).hexdigest(),
    'steps':records,'pass':True,'physicalIPhoneSafari':'PENDING','visualAcceptance':'Human review required'},indent=2)+'\n')
