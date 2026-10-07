"""Serial angle studies through ordinary gameplay mouse controls.

Use after native lighting, export, transport verification and cache versioning.
No model, character-art or resolution setter is used to hide scale differences.
"""
import argparse,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=R/'docs/review/wayfarer-capital-v76/property-frontages/ro3-polish-camera')
parser.add_argument('--profiles',default='45-20-125,50-10-125,45-10-110')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
fixture=R/'docs/review/wayfarer-capital-v76/mobile-streaming/streamed-views/fixture-save.json'
profiles=[]
for name in args.profiles.split(','):
    pitch,yaw,zoom=map(float,name.split('-'));target=args.output/name;target.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(R/'tools/capture-wayfarer-views.py'),'--output',str(target),
         '--views','street-west,plaza-frontages','--width','910','--height','512','--scene-only',
         '--pitch',str(pitch),'--yaw',str(yaw),'--zoom',str(zoom),'--startup-timeout-ms','180000',
         '--template-file',str(fixture)]
    print('START',name,flush=True)
    with (target/'capture.log').open('w') as log:result=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
    assert result.returncode==0,(name,result.returncode)
    records=json.loads((target/'views.json').read_text())
    for record in records:
        assert not record['errors'] and record['streaming']['sourceSHA256']==record['sourceSHA256']
        for key,value in [('pitch',pitch),('yaw',yaw),('zoom',zoom)]:assert abs(record['camera'][key]-value)<.06
    profiles.append({'profile':name,'manifest':str(target/'views.json'),'captures':len(records)})
    print('END',name,flush=True)
(args.output/'study.json').write_text(json.dumps({'profiles':profiles,'ordinaryCameraControls':True,
    'visualAcceptance':'Compare roof/facade balance, street depth and person-relative framing with supplied RO3; no measured game camera telemetry.'},indent=2)+'\n')
