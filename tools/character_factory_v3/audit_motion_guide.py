#!/usr/bin/env python3
"""Audit captured motion geometry without treating silhouette IoU as an art grade."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image
from audit_sprite_candidate import _iou, RESEARCH_IOU_WARNING


def audit(root):
    manifest=json.loads((root/'manifest.json').read_text());frames=manifest['frames']
    images=[Image.open(root/record.get('image',f'frames/{i:03d}.png')).convert('RGBA') for i,record in enumerate(frames)]
    steps={}
    for name in frames[0]['landmarks']:
        pairs=[(math.dist(a['landmarks'][name],b['landmarks'][name]),i) for i,(a,b) in enumerate(zip(frames,frames[1:]))]
        delta,index=max(pairs);steps[name]={'max_step_source_px':round(delta,4),'frames':[index,index+1]}
    joins=[]
    for i,(a,b) in enumerate(zip(frames,frames[1:])):
        if a['segment']!=b['segment']:
            joins.append({'frames':[i,i+1],'segments':[a['segment'],b['segment']], 'steps_px':{n:round(math.dist(a['landmarks'][n],b['landmarks'][n]),4) for n in ['head','pelvis','hand_r','foot_l','foot_r']}})
    edges=[];bounds=[];outside_sword=[]
    for i,im in enumerate(images):
        mask=np.asarray(im.getchannel('A'))>8;ys,xs=np.nonzero(mask)
        if len(xs)==0:raise ValueError(f'Empty guide frame {i}')
        bounds.append([int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)])
        if mask[0,:].any() or mask[-1,:].any() or mask[:,0].any() or mask[:,-1].any():edges.append(i)
        if any(not (0<=frames[i][k][0]<im.width and 0<=frames[i][k][1]<im.height) for k in ['sword_grip','sword_tip']):outside_sword.append(i)
    ious=[_iou(a,b) for a,b in zip(images,images[1:])]
    contacts={}
    for foot in ['ball_l','ball_r']:
        points=[r['feet_world'][foot] for r in frames];floor=min(v[2] for v in points)
        near=[i for i,v in enumerate(points) if v[2]<=floor+.025]
        moves=[(math.dist(points[i][:2],points[i+1][:2]),i) for i in near if i+1 in near]
        contacts[foot]={'lowest_height_m':round(floor,5),'near_floor_threshold_m':.025,'near_floor_frames':near,'max_horizontal_step_while_near_floor_m':round(max((x[0] for x in moves),default=0),5),'interpretation':'Height proxy only; inspect sole contact and sliding visually.'}
    first=np.asarray(images[0]);last=np.asarray(images[-1])
    result={'status':'DIAGNOSTIC_ONLY_NOT_ART_APPROVAL','frame_count':len(frames),'output_fps':manifest['output_fps'],'camera':manifest['camera'],'source_pose_steps':steps,'segment_joins':joins,'frames_touching_canvas_edge':edges,'sword_points_outside_canvas':outside_sword,'shared_alpha_bounds':[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)],'first_last_pixel_difference_count':int(np.any(first!=last,axis=2).sum()),'first_last_max_landmark_delta_px':max(math.dist(frames[0]['landmarks'][n],frames[-1]['landmarks'][n]) for n in frames[0]['landmarks']),'adjacent_alpha_iou_min':min(ious),'adjacent_alpha_iou_mean':sum(ious)/len(ious),'research_iou_warning':RESEARCH_IOU_WARNING,'foot_contact_proxies':contacts,'interpretation':'Research silhouette IoU is a warning signal. Fast strikes legitimately change silhouettes. An identical endpoint or fixed camera cannot establish human motion, blade grip or art quality.'}
    (root/'motion-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path);args=parser.parse_args()
    r=audit(args.folder);print(json.dumps({k:r[k] for k in ['frame_count','frames_touching_canvas_edge','sword_points_outside_canvas','shared_alpha_bounds','first_last_pixel_difference_count','first_last_max_landmark_delta_px','adjacent_alpha_iou_mean','segment_joins']},indent=2))
