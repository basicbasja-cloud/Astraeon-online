"""Independent clock/parity/source projection controls and strict painted gate."""
from pathlib import Path
import json,hashlib,argparse,copy
import numpy as np
from PIL import Image,ImageSequence
P=Path(__file__).resolve().parent;OLD=P.parent/'painted-pickup-v47'
c=json.loads((P/'contract.json').read_text());r=json.loads((P/'review.json').read_text());s=json.loads((P/'source/receipt.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def starts(a):return np.cumsum([0]+a[:-1]).tolist()
def clock_gate(a,b):return sum(a)==sum(b)==1900 and all(starts(a)[i]==starts(b)[k] for i,k in enumerate(c['original_key_output_indices']))
def parity(seq):return all(np.array_equal(np.asarray(Image.open(OLD/'frames'/f'{i:02}.png')),np.asarray(seq[k])) for i,k in enumerate(c['original_key_output_indices']))
seq=[Image.open(P/'frames16'/f'{k:02}.png') for k in range(16)]
checks={'same1900ms_and_key_start_times':clock_gate(c['original_clock_ms'],c['sixteen_clock_ms']),'all8_parent_rgba_exact':parity(seq)}
mut=copy.deepcopy(c['sixteen_clock_ms']);mut[1]+=10;mut[3]-=10
checks['equal_total_but_misaligned_key_negative']=not clock_gate(c['original_clock_ms'],mut)
bad=list(seq);bad[2]=seq[15];checks['replaced_parent_key_negative']=not parity(bad)
checks['16_exposures_16_unique_png_hashes']=len({sha(P/'frames16'/f'{k:02}.png') for k in range(16)})==16
checks['parent_rig_copy_exact']=sha(P/'source/parent-v45.blend')==sha(P.parent/'left-arm-repair-v45/original-character.blend')==s['blend_sha256']
checks['new8_source_frames_evaluated']=len(s['frames'])==8 and all(abs(f['phase']-k/7)<1e-10 for f,k in zip(s['frames'],c['new_source_key_fractions']))
inv=np.linalg.inv(np.asarray(s['camera_matrix']));scale=512/s['ortho_scale'];error=0
for f in s['frames']:
 for point in f['source_bones'].values():
  q=inv@np.asarray(point['world']+[1]);pred=np.asarray([192+q[0]*scale,256-q[1]*scale]);error=max(error,float(np.linalg.norm(pred-point['projected_raw'])))
checks['independent_source_projection_under001px']=error<.001
drift=max(f['actual_foot_vertex_max_world_drift'] for f in s['frames'])*scale*c['inherited_source_matrix'][0]
checks['new_source_foot_drift_under02px']=drift<.02
for name,n,clock in [('painted-8.gif',8,c['original_clock_ms']),('painted-16-REJECTED.gif',16,c['sixteen_clock_ms']),('source-16.gif',16,c['sixteen_clock_ms']),('source-8-16-comparison.gif',16,c['sixteen_clock_ms'])]:
 im=Image.open(P/'previews'/name);observed=[f.info['duration'] for f in ImageSequence.Iterator(im)];checks['decoded_'+name]=len(observed)==n and observed==clock
checks['known_painted_floor_failure_stays_blocked']=not all(v['bounded_6px_pass'] for v in r['painted16']['summary'].values())
checks['original_v47_evidence_unchanged']=all(sha(OLD/f['path'])==f['sha256'] for f in json.loads((OLD/'evidence-manifest.json').read_text())['files'])
release=all(v['bounded_6px_pass'] for v in r['painted16']['summary'].values()) and r.get('family_dimensions_pass') is True and r.get('visible_ownership_and_grip_pass') is True
report={'checks':checks,'pass':all(checks.values()),'production_pass':bool(release),'independent_projection_max_px':error,'new_actual_source_foot_drift_projected_upper_bound_px':drift,'strict_release_blocked':not release,'scope':'Exact clocks/old pixels and bounded source checks, separate from rejected new paint'}
(P/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));ap=argparse.ArgumentParser();ap.add_argument('--require-production',action='store_true');args=ap.parse_args();raise SystemExit(1 if not report['pass'] or args.require_production and not release else 0)
