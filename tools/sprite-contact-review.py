#!/usr/bin/env python3
"""Reusable, unknown-first visible surface contact review.

Input is a SHA-bound frame list, manually authored visible surface windows,
contact intervals and declared budgets. No colors, source joints, future pose
transforms or screen-X anatomical labels enter pixel observation.
This detects surface drift, not anatomical identity or invisible sole contacts.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
from scipy import ndimage

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def observe(image,box,band=8,alpha=128,min_area=40):
    a=np.asarray(image.convert('RGBA'))[:,:,3]>=alpha
    x0,y0,x1,y1=box
    if not (0<=x0<x1<=a.shape[1] and 0<=y0<y1<=a.shape[0]):return {'status':'UNKNOWN_INVALID_WINDOW'}
    labels,n=ndimage.label(a[y0:y1,x0:x1]);counts=np.bincount(labels.ravel());counts[0]=0
    candidates=[i for i,c in enumerate(counts) if c>=min_area]
    if len(candidates)!=1:return {'status':'UNKNOWN_MISSING_OR_AMBIGUOUS_COMPONENT','components':len(candidates)}
    ys,xs=np.where(labels==candidates[0]);bottom=int(ys.max()+y0)
    if xs.min()==0 or xs.max()==x1-x0-1 or ys.max()==y1-y0-1:return {'status':'UNKNOWN_WINDOW_CUT'}
    yy,xx=np.where((labels==candidates[0]) & (np.indices(labels.shape)[0]>=ys.max()-band+1))
    return {'status':'VISIBLE_SURFACE_ONLY','left_x':int(xx.min()+x0),'right_x':int(xx.max()+x0),'bottom_y':bottom,'area':int(counts[candidates[0]]),'band_px':band}

def evaluate(contract,base):
    rows=[];failures=[]
    # Reject vacuous pass and malformed schedules before observing any pixels.
    frames=contract.get('frames',[]);surfaces=contract.get('surfaces',{})
    valid=bool(frames and surfaces) and type(contract.get('alpha_threshold',128)) is int and 1<=contract.get('alpha_threshold',128)<=255
    valid=valid and all(isinstance(f,dict) and isinstance(f.get('path'),str) and isinstance(f.get('sha256'),str) and len(f['sha256'])==64 for f in frames)
    for s in surfaces.values():
        schedule=s.get('planted_frames',[]);budget=s.get('budget_px',{});window=s.get('window',[])
        valid=valid and len(window)==4 and all(type(x) is int for x in window)
        valid=valid and type(s.get('min_component_area',40)) is int and s.get('min_component_area',40)>0
        valid=valid and bool(schedule) and len(set(schedule))==len(schedule) and all(type(i) is int and 0<=i<len(frames) for i in schedule)
        valid=valid and all(isinstance(budget.get(k),(int,float)) and np.isfinite(budget[k]) and budget[k]>=0 for k in ['x','y'])
        valid=valid and type(s.get('distal_band_px',8)) is int and s.get('distal_band_px',8)>0
    if not valid:return {'visible_surface_contact_pass':False,'failures':[{'kind':'invalid_or_empty_contract'}],'summary':{},'production_pass':False}

    for i,f in enumerate(contract['frames']):
        path=base/f['path']
        if not path.is_file():failures.append({'kind':'missing_frame','index':i});continue
        digest=sha(path)
        if digest!=f['sha256']:failures.append({'kind':'stale_frame','index':i});continue
        image=Image.open(path);surfaces={}
        for name,s in contract['surfaces'].items():
            if i not in s['planted_frames']:surfaces[name]={'status':'NOT_IN_CONTACT_SCHEDULE'};continue
            surfaces[name]=observe(image,s['window'],s.get('distal_band_px',8),contract.get('alpha_threshold',128),s.get('min_component_area',40))
        rows.append({'index':i,'frame_sha256':digest,'surfaces':surfaces})
    summary={}
    for name,s in contract['surfaces'].items():
        active=[r['surfaces'][name] for r in rows if r['index'] in s['planted_frames']]
        covered=len(active)==len(s['planted_frames']) and all(v['status']=='VISIBLE_SURFACE_ONLY' for v in active)
        ranges={k:max(v[k] for v in active)-min(v[k] for v in active) for k in ['left_x','right_x','bottom_y']} if covered else None
        budget=s['budget_px'];passed=bool(covered and max(ranges['left_x'],ranges['right_x'])<=budget['x'] and ranges['bottom_y']<=budget['y'])
        heldout=[r['index'] for r in rows if r['index'] in s['planted_frames'] and r['index'] not in contract.get('calibration_output_frames',[])]
        summary[name]={'fully_visible':covered,'ranges_px':ranges,'budget_px':budget,'heldout_frame_count':len(heldout),'surface_stability_pass':passed}
    passed=not failures and all(v['surface_stability_pass'] for v in summary.values())
    return {'visible_surface_contact_pass':passed,'frames':rows,'summary':summary,'failures':failures,'anatomical_identity_pass':None,'hidden_joint_accuracy':None,'production_pass':False,'scope':'Visible authored surface windows under contact schedule; no anatomical recovery or all-factory acceptance'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('contract');ap.add_argument('--output');ap.add_argument('--require-contact',action='store_true');args=ap.parse_args();path=Path(args.contract);r=evaluate(json.loads(path.read_text()),path.parent)
    if args.output:Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'visible_surface_contact_pass':r['visible_surface_contact_pass'],'summary':r['summary'],'failures':r['failures']}));raise SystemExit(1 if args.require_contact and not r['visible_surface_contact_pass'] else 0)
