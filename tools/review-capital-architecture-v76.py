"""Serial native and ordinary-input verification of architecture revision76.

Set ASTRAEON_ARCH_REVIEW_FROM to resume a named stage. Requires a local server,
Blender, Playwright and the Shapely/cutout-alpha caches described in the handoff.
"""
import os,subprocess,time,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76'
env=os.environ.copy();env.update(PYTHONPATH='/tmp/astraeon-curb-geometry',ASTRAEON_CAPITAL_REVIEW_DIR='docs/review/wayfarer-capital-v76',ASTRAEON_SHADOW_ALPHA_CACHE='/tmp/astraeon-ro3-72/composition-alpha.json')
def step(name,args,allow_failure=False):
 print('START',name,time.strftime('%H:%M:%S'),flush=True)
 with (O/(name+'.log')).open('w') as f:res=subprocess.run(args,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 print('END',name,res.returncode,time.strftime('%H:%M:%S'),flush=True)
 if res.returncode and not allow_failure:raise SystemExit(res.returncode)
def blender(name,script):step(name,['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python','tools/'+script+'.py'])
start=os.environ.get('ASTRAEON_ARCH_REVIEW_FROM','lodge-entries');stop_after=os.environ.get('ASTRAEON_ARCH_REVIEW_TO');active=False
def run(name,callback):
 global active
 if name==start:active=True
 if active:
  callback()
  if name==stop_after:
   print('REVIEW COMPLETE THROUGH REQUESTED STAGE',name,flush=True)
   raise SystemExit(0)
run('lodge-entries',lambda:blender('lodge-entries','refine-capital-lodge-doors-v76'))
run('geometry',lambda:step('geometry',['python3','tools/check-capital-architecture-v76.py']))
run('assembly',lambda:step('assembly',['python3','tools/check-wayfarer-capital-v75.py']))
run('density',lambda:step('density',['python3','tools/check-capital-density-v75.py']))
run('traversal',lambda:step('traversal',['node','tools/check-ro3-traversal-v68.cjs',str(O/'traversal.json')]))
run('architecture-bake',lambda:blender('architecture-bake','bake-town-depth-v48'))
run('foliage-bake',lambda:blender('foliage-bake','bake-ro3-foliage-v70'))
run('ground-bake',lambda:blender('ground-bake','bake-ground-shadows-v54'))
run('native-parity',lambda:blender('native-parity','check-blender-export-v3'))
run('geometry-final',lambda:step('geometry-final',['python3','tools/check-capital-architecture-v76.py']))
run('beta-edges-final',lambda:step('beta-edges-final',['python3','tools/check-capital-beta-edges-v76.py']))
run('assembly-final',lambda:step('assembly-final',['python3','tools/check-wayfarer-capital-v75.py']))
run('density-final',lambda:step('density-final',['python3','tools/check-capital-density-v75.py']))
run('traversal-final',lambda:step('traversal-final',['node','tools/check-ro3-traversal-v68.cjs',str(O/'traversal.json')]))
run('blueprint',lambda:step('blueprint',['python3','tools/draw-capital-architecture-v76.py']))
run('tests',lambda:step('tests',['python3','tools/check-current-capital-tests.py']))
run('schemas',lambda:step('schemas',['python3','tools/validate-world-v3.py']))
template=R/'docs/review/wayfarer-capital-v75/before-density/views/fixture-save.json'
def capture(name,views,zoom=160,yaw=25,pitch=46,width=1280):
 step(name,['python3','tools/capture-wayfarer-views.py','--views',views,'--output',str(O/name),'--template-file',str(template),'--zoom',str(zoom),'--yaw',str(yaw),'--pitch',str(pitch),'--width',str(width),'--startup-timeout-ms','300000','--verify-culling','--scene-only'])
run('beta-default',lambda:step('beta-default',['python3','tools/capture-wayfarer-views.py','--views','street-west,plaza-frontages','--output',str(O/'beta-default'),'--template-file',str(template),'--width','910','--height','512','--startup-timeout-ms','300000','--verify-culling','--scene-only']))
run('beta-camera-study',lambda:step('beta-camera-study',['python3','tools/capture-wayfarer-views.py','--views','street-west,plaza-frontages','--output',str(O/'beta-camera-study'),'--template-file',str(template),'--width','910','--height','512','--zoom','65','--pitch','46','--startup-timeout-ms','300000','--verify-culling','--scene-only']))
run('streets',lambda:capture('streets','street-west,street-east,street-artisan,street-borough'))
run('plaza-courts',lambda:capture('plaza-courts','plaza-frontages,artisan-court,willow-court',220,25,60,1920))
run('civic',lambda:capture('civic','council-roof,archive-roof,exchange-roof',325,0,65,1920))
run('shore',lambda:capture('shore','bank-east',325,90,46,1920))
run('services',lambda:step('services',['python3','tests/golden_wayfarer.py','--phase','services','--neighborhoods','--travel-mode','sprint','--startup-timeout-ms','300000','--output',str(O/'services')]))
run('cache',lambda:step('cache',['python3','tests/cache_resume.py','--startup-timeout-ms','300000','--output',str(O/'cache')]))
run('performance',lambda:step('performance',['python3','tests/movement_performance.py','--startup-timeout-ms','300000','--output',str(O/'performance.json')],True))
if not active:raise SystemExit('Unknown review start stage: '+start)
if stop_after:raise SystemExit('Unknown or unreached review stop stage: '+stop_after)
print('ARCHITECTURE REVIEW STAGES COMPLETE',flush=True)
