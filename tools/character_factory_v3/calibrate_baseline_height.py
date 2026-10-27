"""Calibrate one candidate-fit scale using a preserved baseline and source pose.

Source head/ground deltas distinguish intended crouching from image-size drift.
This produces a proposed fit, not anatomical or animation acceptance.
"""
import math


def baseline_height_fit(reference_crown_y,reference_ground_y,reference_head_y,
                        reference_foot_y,target_head_y,target_foot_y,
                        candidate_crown_y,candidate_ground_y):
    values=[reference_crown_y,reference_ground_y,reference_head_y,reference_foot_y,
            target_head_y,target_foot_y,candidate_crown_y,candidate_ground_y]
    if not all(math.isfinite(x) for x in values):raise ValueError('Finite measured points required')
    if candidate_ground_y<=candidate_crown_y:raise ValueError('Invalid candidate body extent')
    target_crown=reference_crown_y+target_head_y-reference_head_y
    target_ground=reference_ground_y+target_foot_y-reference_foot_y
    if target_ground<=target_crown:raise ValueError('Invalid transferred baseline extent')
    scale=(target_ground-target_crown)/(candidate_ground_y-candidate_crown_y)
    return {'shared_scale':scale,'first_frame_y_translation':target_ground-scale*candidate_ground_y,
            'target_crown_y':target_crown,'target_ground_y':target_ground,
            'expected_body_height_px':target_ground-target_crown,
            'basis':'Baseline crown/head and ground/foot offsets transferred once to target source pose',
            'approved':False,'note':'Hairstyle and footwear offsets are provisional base-fit references; never recalibrate scale for a cosmetic swap or each frame.'}
