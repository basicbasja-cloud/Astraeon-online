from pathlib import Path
import importlib.util,json,copy
p=Path('work/all-actions-v61/generation');f=p/'S-candidate7';spec=importlib.util.spec_from_file_location('player','tools/sprite-layer-player.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);clip=json.loads((f/'four-slots.json').read_text());full=f/'clip.json';rows=[]
for name in ['stale-source-hash','missing-complete-head','different-clock','non-GIF-clock']:
 d=copy.deepcopy(clip)
 if name=='stale-source-hash':d['frames'][3]['slots']['head']['sha256']='0'*64
 elif name=='missing-complete-head':d['frames'][3]['slots']['head']=None
 elif name=='different-clock':d['frames'][3]['duration_ms']=100
 else:d['frames'][3]['duration_ms']=91
 path=f/('player-negative-'+name+'.json');path.write_text(json.dumps(d));out=f/('player-negative-'+name)
 try:m.build(path,full,out)
 except AssertionError as e:rows.append({'control':name,'rejected':True,'message':str(e),'no_output_created':not out.exists()})
 else:raise AssertionError('Negative accepted '+name)
assert all(r['no_output_created']for r in rows);(p/'player-control-review.json').write_text(json.dumps({'pass':True,'controls':rows},indent=2));print('4 genuine incorrect-input controls rejected before creating artifacts')
