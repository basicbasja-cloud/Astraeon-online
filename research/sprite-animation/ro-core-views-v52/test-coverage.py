"""Failure-focused fixtures use synthetic art; never certify real clips."""
from pathlib import Path
import tempfile,importlib.util,hashlib,copy,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('coverage',P.parents[2]/'tools/sprite-coverage-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);Image.new('RGBA',(32,32),(255,100,30,255)).save(p/'fixture.png');sha=hashlib.sha256((p/'fixture.png').read_bytes()).hexdigest();catalog={'directions':m.DIRECTIONS,'canvas':[32,32],'clock_quantum_ms':10,'actions':{}}
 for name,count in m.CORE.items():
  aliases={v:m.DIRECTIONS[(i//2)*2] if count==4 else v for i,v in enumerate(m.DIRECTIONS)};clips={}
  for v in set(aliases.values()):
   n=16 if name=='pickup' else 1
   clips[v]={'frames':[{'path':'fixture.png','sha256':sha} for _ in range(n)],'durations_ms':[100]*n,'review':{'frame_sha256':[sha]*n,'status':'agent_visual_pass','observations':['Synthetic test fixture only']},'checks':dict.fromkeys(['registration','appearance','playback','pose_readability','whole_motion'],True)}
  catalog['actions'][name]={'aliases':aliases,'clips':clips}
 assert m.evaluate(catalog,p)['pass'];checks={'complete_synthetic_contract':True}
 for label,mutation in [
  ('missing_direction',lambda c:c['actions']['sit']['clips'].pop('NE')),
  ('unsafe_alias',lambda c:c['actions']['pickup']['aliases'].update({'NE':'S'})),
  ('changed_pixel',lambda c:c['actions']['idle']['clips']['N']['frames'][0].update({'sha256':'0'*64})),
  ('stale_review',lambda c:c['actions']['idle']['clips']['N']['review'].update({'frame_sha256':[]})),
  ('manual_rejection',lambda c:c['actions']['walk']['clips']['W']['review'].update({'status':'rejected'})),
  ('mirror_asymmetry',lambda c:c['actions']['attack1']['clips']['E'].update({'mirrored':True})),
  ('unverified_motion',lambda c:c['actions']['pickup']['clips']['S']['checks'].update({'whole_motion':False})),
  ('unencoded_clock',lambda c:c['actions']['hurt']['clips']['N'].update({'durations_ms':[95]}))]:
  c=copy.deepcopy(catalog);mutation(c);assert not m.evaluate(c,p)['pass'],label;checks[label]=True
 c=copy.deepcopy(catalog);c.pop('clock_quantum_ms');c['actions']['hurt']['clips']['N']['durations_ms']=[1000/60];assert m.evaluate(c,p)['pass'];checks['fractional_engine_clock_without_gif_quantum']=True
 for value in [0,-1,float('nan'),float('inf'),True]:
  c=copy.deepcopy(catalog);c['actions']['hurt']['clips']['N']['durations_ms']=[value];assert not m.evaluate(c,p)['pass']
 checks['nonfinite_nonpositive_boolean_clocks_rejected']=True
 c=copy.deepcopy(catalog);c['clock_quantum_ms']=0;assert not m.evaluate(c,p)['pass'];checks['invalid_encoding_profile']=True
 action=catalog['actions']['pickup'];assert m.resolve(action,1,1)=='W';assert m.resolve(action,7,2)=='S';assert m.resolve(catalog['actions']['sit'],7,2)=='SW';checks['camera_before_action_alias_and_wrap']=True
 (P/'coverage-tool-tests.json').write_text(json.dumps({'pass':True,'checks':checks,'scope':'Synthetic negative controls, not production art approval'},indent=2)+'\n');print(checks)
