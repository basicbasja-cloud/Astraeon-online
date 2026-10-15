import copy,json,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('gate',P/'audit.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);i=json.loads((P/'arm-inspection.json').read_text());old=i['before'];new=i['after'];c={}
c['actual_new_saved_rig_passes']=all(mod.arm_gate(new).values());c['actual_rejected_v44_rig_fails']=not all(mod.arm_gate(old).values());renamed=copy.deepcopy(old);renamed['name']='fixed left arm';c['renaming_old_rig_report_not_a_fix']=not all(mod.arm_gate(renamed).values())
def reject(n,edit):
 x=copy.deepcopy(new);edit(x);c[n]=not all(mod.arm_gate(x).values())
reject('side_elbow_wing_rejected',lambda x:x['summary'].update(max_abduction_degrees=43));reject('wrong_bend_plane_rejected',lambda x:x['summary'].update(max_plane_deviation_degrees=80));reject('normal_flip_rejected',lambda x:x['summary'].update(max_normal_step_degrees=179));reject('nan_unknown_rejected',lambda x:x['summary'].update(max_plane_deviation_degrees=float('nan')));reject('missing_current_modifier_rejected',lambda x:x.update(missing_actual_modifiers=['left.continuous_arm']));reject('valid_area_but_ring_collapse_rejected',lambda x:x['summary'].update(min_ring_spacing_ratio=.1));reject('frozen_world_source_left_target_rejected',lambda x:x['source_key_errors'][3].update(max_error=.2));reject('between_key_foot_jump_rejected',lambda x:x['summary'].update(max_foot_vertex_drift=.01));reject('incomplete_sample_coverage_rejected',lambda x:x['frames'].pop());reject('missing_metric_not_assumed_zero',lambda x:x['summary'].pop('max_plane_deviation_degrees'))
reject('open_actual_arm_surface_rejected',lambda x:x.update(arm_nonmanifold_edges=2))
reject('negative_weights_rejected',lambda x:x.update(invalid_weights=1))
from PIL import Image
import numpy as np
bad=json.loads((P/'failed-isolation-prop-REJECTED/receipt.json').read_text())
counts=[]
for f in bad['retained_actual_negative_frames']:
 a=np.asarray(Image.open(P/f['path']).convert('RGBA'));orange=(a[:,:,0]>240)&(a[:,:,1]>60)&(a[:,:,1]<200)&(a[:,:,2]<80);counts.append(int(((a[:,:,3]>128)&~orange).sum()))
c['real_bad_isolation_with_animated_prop_rejected']=all(n>0 for n in counts)
(P/'regressions.json').write_text(json.dumps(dict(checks=c,pass_all=all(c.values()),scope='Specific free-arm source contract controls; not approval of art, image anatomy or all motions'),indent=2)+'\n');print(json.dumps(c,indent=2));assert all(c.values())
