"""Recompute all image correspondences and held-out metrics, not semantic truth."""
import importlib.util,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];STUDY=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('tracker',ROOT/'skills/modular-eight-direction-sprites/scripts/joint-image-track.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for assisted in (False,True):
 runs=[]
 for directory in sorted((STUDY/'benchmark').iterdir()):
  if not directory.is_dir():continue
  name='assisted-case.json' if assisted else 'case.json';case,images=m.load_case(directory/name,ROOT);report=m.bidirectional(case,images) if assisted else m.track(case,images);out='assisted-tracks.json' if assisted else 'tracks.json';(directory/out).write_text(json.dumps(report,indent=2)+'\n');m.grid_board(case,report,ROOT,directory/('grid-assisted.png' if assisted else 'grid-tracks.png'))
  truth=json.loads((directory/'truth.json').read_text());seeds={(s['frame'],s['joint']) for s in case['seeds']};errors=[];targets=0
  for f,t in zip(report['frames'],truth['frames']):
   for name,point in t['points'].items():
    if (f['index'],name) in seeds:continue
    targets+=1;p=f['points'][name]
    if p['status']=='proposal':errors.append(math.dist(p['xy'],point['xy']))
  runs.append({'clip':directory.name,'labelled_seed_frames':sorted({s['frame'] for s in case['seeds']}),'held_out_target_count':targets,'proposal_count':len(errors),'coverage':len(errors)/targets,'median_error_px':float(np.median(errors)),'p95_error_px':float(np.percentile(errors,95)),'over_3px':sum(e>3 for e in errors),'within_3px_fraction':sum(e<=3 for e in errors)/len(errors),'production_pass':False})
 result={'mode':'sparse source-projected benchmark keyframes; held-out remaining points; NOT human annotations/fullyautomatic inference' if assisted else 'frame0 source-projected seeds; held-out later points','config':m.DEFAULTS,'percentile_method':'numpy.percentile linear','runs':runs,'art_anatomy_accuracy':None,'thresholds_tuned_to_truth':False,'seed_frames_excluded_from_scoring':True,'future_unseeded_truth_used':False}
 (STUDY/('assisted-tracking-benchmark.json' if assisted else 'tracking-benchmark.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'clips':len(runs),'assisted':[{'clip':r['clip'],'p95':r['p95_error_px'],'coverage':r['coverage']} for r in runs]}))
