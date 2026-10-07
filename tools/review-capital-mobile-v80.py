"""Serial ordinary browser mobile/cache/field gates on the sealed current art."""
import json,hashlib,subprocess,os,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80';V=O/'unique-neighborhoods';seal=json.loads((V/'verified-source.json').read_text());assert seal['pass'];raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==seal['sourceSHA256'];del raw
manifest=json.loads((R/'world/v3/world-manifest.json').read_text());zone=json.loads((R/manifest['zones'][manifest['defaultZone']]['url']).read_text());assert zone['sourceSHA256']==seal['sourceSHA256']
env=os.environ.copy();env['LD_LIBRARY_PATH']='/workspace/.cache/astraeon-webkit-libs/usr/lib/x86_64-linux-gnu';records=[]
steps=[('mobile-touch',['python3','tests/mobile_streaming.py','--engine','webkit','--legs','128,150;80,200;13.4,144;128,150','--output',str(O/'mobile-streaming/ordinary-touch-v80')]),('cache-offline',['python3','tests/cache_resume.py','--output',str(O/'cache-resume'),'--startup-timeout-ms','180000']),('field-return',['python3','tests/mobile_field_return.py','--output',str(O/'mobile-field-return')])]
for name,cmd in steps:
 print('START',name,flush=True);start=time.monotonic()
 with (V/(name+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 records.append({'name':name,'exitCode':r.returncode,'seconds':round(time.monotonic()-start,1)});(V/'mobile-progress.json').write_text(json.dumps(records,indent=2)+'\n');print('END',name,r.returncode,flush=True)
 assert r.returncode==0,(name,r.returncode)
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==seal['sourceSHA256']
(V/'mobile-verified.json').write_text(json.dumps({'sourceSHA256':seal['sourceSHA256'],'runtimeSHA256':hashlib.sha256((R/'world-view.js').read_bytes()).hexdigest(),'steps':records,'pass':True,'physicalIPhoneSafari':'PENDING'},indent=2)+'\n')
