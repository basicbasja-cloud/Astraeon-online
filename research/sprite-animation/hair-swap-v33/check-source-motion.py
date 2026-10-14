"""Reuse frozen v32 observer calibration; independently locate new frame pixels."""
import copy,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;OLD=P.parent/'pickup-modular-v32';S=ROOT/'skills/modular-eight-direction-sprites/scripts'
def load(n,f):
 s=importlib.util.spec_from_file_location(n,f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
observer=load('observer',S/'rigged-surface-observer.py');auditor=load('surface',S/'planted-surface-review.py')
case=json.loads((P/'swap-case.json').read_text());reports={}
for style in ['silver','auburn','bald']:
 tracking=json.loads((OLD/'observer-case.json').read_text());tracking['frames']=case['styles'][style];observations=observer.observe(tracking,ROOT)
 surfaces=json.loads((OLD/'image-case.json').read_text());surfaces['frames']=copy.deepcopy(case['styles'][style])
 for i,f in enumerate(surfaces['frames']):f['observations']={n:{k:v for k,v in rows[i].items() if k in ('status','xy','uncertainty_px','anatomical_owner')} for n,rows in observations['tracks'].items()}
 report=auditor.audit(surfaces,ROOT);reports[style]={'surface_review':report,'actual_pixel_observations':observations,'source_phase_max_difference':max(r['absolute_fraction_difference'] for r in report['markers']['surface.reaching_cuff']['source_relative_phase'] if r['held_out'])}
 if not report['numerical_surface_check_pass']:raise ValueError('New hair variant failed actual motion surface checks: '+style)
(P/'source-motion-review.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps({n:{'pass':r['surface_review']['numerical_surface_check_pass'],'phase':r['source_phase_max_difference']} for n,r in reports.items()}))
