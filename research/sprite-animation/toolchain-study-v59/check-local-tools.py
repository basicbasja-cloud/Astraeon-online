"""Actual-frame pack regression proof and invalid-input controls, no art approval."""
from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,copy,sys,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2];base=P.parent/'whole-body-v58';clip=json.loads((base/'pickup-S-four-slot.json').read_text());pack=P/'lossless-pack';meta=json.loads((pack/'atlas/frames.json').read_text());sheet=Image.open(pack/'atlas/frames.png').convert('RGBA');rows=[]
for i,r in enumerate(meta['frames']):
 src=base/'frames/full'/r['filename'];actual=sheet.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h']));assert actual.tobytes()==Image.open(src).convert('RGBA').tobytes();assert r['duration_ms']==clip['frames'][i]['duration_ms'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256'];rows.append(i)
assert sum(r['duration_ms']for r in meta['frames'])==1900
negative=json.loads((P/'img-upstream-atlas-negative.json').read_text());assert not negative['passed_exact_rgba']and all(r['alpha_different_pixels']>0 for r in negative['frames'])
for f in clip['frames']:
 for s in f['slots'].values():
  if s:s['asset']=str(base/s['asset'])
controls=[]
with tempfile.TemporaryDirectory(dir=ROOT/'work')as temp:
 temp=Path(temp)
 positive=subprocess.run([sys.executable,str(ROOT/'tools/whole-body-toolchain.py'),'pack','--clip',str(base/'pickup-S-four-slot.json'),'--frames',str(base/'frames/full'),'--out',str(temp/'positive')],capture_output=True,text=True);assert positive.returncode==0,positive.stderr;assert json.loads(positive.stdout)['exact_rgba_cells']==16
 mutations=[('zero_duration',lambda d:d['frames'][0].update(duration_ms=0)),('fragment_slot',lambda d:d['frames'][0]['slots'].update(knee=d['frames'][0]['slots']['body'])),('stale_pixels',lambda d:d['frames'][0]['slots']['body'].update(sha256='0'*64)),('canvas_changed',lambda d:d.update(canvas=[281,350])),('segmented_body',lambda d:d.update(bodyPolicy='segmented-limbs'))]
 for name,mutate in mutations:
  d=copy.deepcopy(clip);mutate(d);src=temp/(name+'.json');src.write_text(json.dumps(d));r=subprocess.run([sys.executable,str(ROOT/'tools/whole-body-toolchain.py'),'pack','--clip',str(src),'--frames',str(base/'frames/full'),'--out',str(temp/name)],capture_output=True,text=True);assert r.returncode!=0 and'AssertionError'in r.stderr,name;controls.append({'control':name,'rejected':True})
report={'local_pack_integration_pass':True,'actual_rgba_cells':rows,'upstream_double_alpha_negative_preserved':True,'exact_authored_clock_pass':True,'invalid_input_controls':controls,'art_approval_granted':False,'source_motion_still_rejected':True,'dependencies':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [ROOT/'tools/whole-body-toolchain.py',ROOT/'.agents/skills/img2game2d/forge/stage5_atlas/generate_spritesheet.py',pack/'atlas/frames.json',pack/'atlas/frames.png']}}
(P/'local-integration-review.json').write_text(json.dumps(report,indent=2)+'\n');print({'pack_integration_pass':True,'actual_cells':16,'negative_controls':len(controls)})
