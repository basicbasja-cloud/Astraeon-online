"""Validate staff-role capture evidence; this never approves painted artwork."""
import math


def valid_staff_grip_capture(job,manifest):
    if not job.get('staff_grip_alignment_revision'):return True
    if type(job['staff_grip_alignment_revision']) is not int or job['staff_grip_alignment_revision']!=1:return False
    proof=manifest.get('staff_grip_adaptation',{})
    if not isinstance(proof,dict):return False
    for a,b in [('adapter_sha256','staff_grip_alignment_sha256'),('alignment_math_sha256','staff_grip_alignment_math_sha256'),('canonical_renderer_sha256','renderer_sha256')]:
        expected=job.get(b)
        if not isinstance(expected,str) or len(expected)!=64 or proof.get(a)!=expected:return False
    if proof.get('source_glb_modified') is not False:return False
    def bounded(value,maximum):return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value) and 0<=value<=maximum
    def signed_bounded(value,maximum):return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value) and abs(value)<=maximum
    reference=proof.get('reference_adaptations',[])
    if not isinstance(reference,list) or len(reference)!=1 or not isinstance(reference[0],dict):return False
    ref=reference[0]
    if ref.get('reference_action')!=job.get('staff_arm_reference') or not signed_bounded(ref.get('forearm_roll_degrees'),100) or not bounded(ref.get('wrist_flex_degrees'),35) or not bounded(ref.get('aligned_reference_axis_error_degrees'),.001):return False
    errors=ref.get('reference_anchor_errors_m',{})
    if not isinstance(errors,dict):return False
    if not all(bounded(errors.get(n),1e-5) for n in ['head','pelvis','foot_r','foot_l','hand_r','hand_l','lowerarm_r']):return False
    rows=proof.get('rendered_grip_checks',[]);expected={f'{d}/{i:03d}.png' for d in job['directions'] for i in range(job['frames'])}
    if not isinstance(rows,list) or any(not isinstance(r,dict) for r in rows):return False
    if len(rows)!=len(expected) or {r.get('image') for r in rows}!=expected:return False
    return all(bounded(r.get('axis_error_degrees'),.05) and bounded(r.get('grip_axis_distance_m'),1e-5) for r in rows)
