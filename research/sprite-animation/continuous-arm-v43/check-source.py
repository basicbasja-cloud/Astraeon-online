"""Independent projections/contact/chain checks on the actual eight-view source."""
from pathlib import Path
import importlib.util,json,hashlib,math
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sp=importlib.util.spec_from_file_location('arms',ROOT/'skills/modular-eight-direction-sprites/scripts/arm-chain-audit.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
s=json.loads((P/'source/source.json').read_text());q=m.audit(s);checks=q['checks'].copy();errors=[];images=[];neutral={};worlds=[]
checks['eight_named_physical_cameras']=set(s['cameras'])=={'S','SE','E','NE','N','NW','W','SW'}
checks['equal_ortho_scale']=len({c['ortho_scale'] for c in s['cameras'].values()})==1
for v,c in s['cameras'].items():
    inv=np.linalg.inv(c['world_matrix']);pp=512/c['ortho_scale']
    for f in s['frames']:
        for name,p in f['points'].items():
            local=inv@np.array([*p['world_xyz'],1]);expected=np.array([192+local[0]*pp,256-local[1]*pp]);errors.append(float(np.linalg.norm(expected-p['xy'][v])))
        path=P/f['views'][v]['path'];images.append(hashlib.sha256(path.read_bytes()).hexdigest()==f['views'][v]['sha256'])
        guide=json.loads((P/'guide-bind.json').read_text())['whole_bank_matrix'];ss,tx,ty=guide[0],guide[4],guide[5]
        char=P/f['views'][v]['character']['path'];images.append(hashlib.sha256(char.read_bytes()).hexdigest()==f['views'][v]['character']['sha256'])
        original=Image.open(char).convert('RGBA');im=np.array(original.transform((384,512),Image.Transform.AFFINE,(1/ss,0,-tx/ss,0,1/ss,-ty/ss),Image.Resampling.BICUBIC));a=im[:,:,3]>=128
        images.append(not(a[0].any() or a[-1].any() or a[:,0].any() or a[:,-1].any()))
        if f['index']==0:
            yy,xx=np.where(a);neutral[v]=dict(height=int(yy.max()-yy.min()+1),bbox=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())])
checks['independent_projection']=max(errors)<.001
checks['render_hashes_and_unclipped_guides']=all(images)
checks['exact_world_neutral_return']=all(np.array_equal(np.array(p['world_xyz']),np.array(s['frames'][7]['points'][k]['world_xyz'])) for k,p in s['frames'][0]['points'].items())
checks['source_feet_world_stationary']=all(np.array_equal(f['points'][side+'.'+k]['world_xyz'],s['frames'][0]['points'][side+'.'+k]['world_xyz']) for side in ['left','right'] for k in ['ankle','toe'] for f in s['frames'])
checks['ground_object_bottom_zero']=abs(s['frames'][0]['object_center'][2]-.075)<1e-6
checks['actual_peak_grip_matches_ground_object_top']=np.linalg.norm(np.array(s['frames'][3]['points']['right.grip']['world_xyz'])-(np.array(s['frames'][3]['object_center'])+[0,0,.075]))<1e-6
checks['lifted_object_follows_right_grip']=all(np.linalg.norm(np.array(s['frames'][i]['object_center'])+[0,0,.075]-s['frames'][i]['points']['right.grip']['world_xyz'])<1e-6 for i in [4,5,6])
checks['object_stored_at_return']=not s['frames'][7]['object_visible']
checks['one_shared_neutral_calibrated_display']=neutral['S']['height']==399 and neutral['S']['bbox'][3]==480
owner=json.loads((P/'source-owner-eight/source.json').read_text())
checks['ownership_renders_use_identical_world_poses']=all(np.array_equal(p['world_xyz'],owner['frames'][i]['points'][k]['world_xyz']) for i,f in enumerate(s['frames']) for k,p in f['points'].items())
checks['ownership_render_hashes_and_cameras']=s['cameras']==owner['cameras'] and all(hashlib.sha256((P/f['views'][v]['path']).read_bytes()).hexdigest()==f['views'][v]['sha256'] for f in owner['frames'] for v in s['cameras'])
checks={k:bool(v) for k,v in checks.items()}
out=dict(checks=checks,source_metrics_pass=all(checks.values()),projection_count=len(errors),max_projection_error_px=max(errors),neutral_physical_view_bounds=neutral,arm_detail=q,scope='Source render/declared-world proof only; not native painted registration, image anatomy, continuous-time collision, final skin deformation or production acceptance',production_pass=False)
(P/'source-qa.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['checks','projection_count','max_projection_error_px','source_metrics_pass']}));assert out['source_metrics_pass']
