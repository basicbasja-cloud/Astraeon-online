"""Negative controls based on reproduced renderer/rig failures, not approval tests."""
import copy,json,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('gate',P/'audit.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);base=json.loads((P/'saved-rig-inspection.json').read_text());checks={};checks['current_saved_rig_passes_bounded_geometry']=all(mod.inspect_gate(base).values())
def reject(name,edit):
 r=copy.deepcopy(base);edit(r);checks[name]=not all(mod.inspect_gate(r).values())
neg=json.loads((P/'known-negative-inspection.json').read_text());reject('actual_old_unbound_details_rejected',lambda r:r.update(missing_armature_modifiers=neg['attempt4-unbound-details-REJECTED']['missing_actual_deform_modifiers']));reject('actual_old_bind_axes_rejected',lambda r:r.update(actual_bind_vertex_errors={'actual_bad_basis':neg['attempt1-bind-axis-REJECTED']['maximum_actual_bind_matrix_error']}));reject('missing_evidence_rejected',lambda r:r.pop('actual_bind_vertex_errors'));reject('foot_drift_rejected',lambda r:r.update(max_dense_foot_vertex_drift=.01));reject('wrong_grasp_rejected',lambda r:r.update(max_dense_right_grasp_socket_error=.02));reject('nonfinite_rejected',lambda r:r.update(max_dense_bone_length_error=float('nan')));reject('hidden_bad_weights_rejected',lambda r:r.update(invalid_weights=1));reject('incomplete_source_keys_rejected',lambda r:r['source_key_errors'].pop());reject('open_arm_surface_rejected',lambda r:r['closed_limb_topology']['left.continuous_arm'].update(nonmanifold_edges=1));reject('ring_collapse_rejected',lambda r:r.update(dense_limb_ring_area_ratio_range=[.2,1]));reject('per_limb_runtime_slots_rejected',lambda r:r.update(runtime_slots=['left_arm','head']))
# Real two render frames from the wrong-clock attempt must be recognized as static.
from PIL import Image
import numpy as np
f=P/'attempt3-frame-evaluation-REJECTED';a=f/'S-00.png';b=f/'S-03.png';checks['real_wrong_clock_static_pixels_detected']=a.exists() and b.exists() and np.array_equal(np.asarray(Image.open(a)),np.asarray(Image.open(b)))
checks['real_original_glb_rejects_surface_mismatch']=not json.loads((P/'glb-roundtrip.json').read_text())['roundtrip_surface_pass']
checks['real_split_clip_corrective_glb_rejected']=not json.loads((P/'corrective-split-actions-REJECTED/corrective-glb-roundtrip.json').read_text())['roundtrip_surface_pass']
checks['actual_merged_corrective_glb_all40_samples_pass']=json.loads((P/'corrective-glb-roundtrip.json').read_text())['roundtrip_surface_pass'] and len(json.loads((P/'corrective-glb-roundtrip.json').read_text())['frames'])==40
(P/'regressions.json').write_text(json.dumps(dict(checks=checks,pass_all=all(checks.values()),scope='Controls for bounded rig/capture evidence; never user/final-art approval'),indent=2)+'\n');print(json.dumps(checks,indent=2));assert all(checks.values())
