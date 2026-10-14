"""Bounded raster checks for a source-driven cutout rig baked to sprite passes.

Known internal part identity allows surface correspondence. It does not turn a
whole generated frame into a known skeleton. New independent redraws must use
manual/image tracking and abstain when hidden or ambiguous.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(root,b):return Image.open(root/b['path']).convert('RGBA')
def section(im,center,axis):
 a=np.array(im.getchannel('A'));n=np.array([-axis[1],axis[0]],float);n/=np.linalg.norm(n);t=np.arange(-70,70.01,.25);xy=np.array(center)+t[:,None]*n;xs=np.rint(xy[:,0]).astype(int);ys=np.rint(xy[:,1]).astype(int);valid=(xs>=0)&(ys>=0)&(xs<im.width)&(ys<im.height);hit=np.zeros(len(t),bool);hit[valid]=a[ys[valid],xs[valid]]>=128;ids=np.flatnonzero(hit)
 if not len(ids) or ids[0]==0 or ids[-1]==len(t)-1:return dict(known=False,reason='Empty or sampling-line clipped')
 return dict(known=True,width_px=float(t[ids[-1]]-t[ids[0]]+.25),endpoints=[xy[ids[0]].tolist(),xy[ids[-1]].tolist()],center=list(center),normal=n.tolist())
def foreground(im):
 a=np.array(im.getchannel('A'));y,x=np.where(a>=128)
 return dict(bbox=[int(x.min()),int(y.min()),int(x.max()),int(y.max())],height=int(y.max()-y.min()+1),boundary_pixels=int((a[0]>=128).sum()+(a[-1]>=128).sum()+(a[:,0]>=128).sum()+(a[:,-1]>=128).sum()))
def run(c,root):
 root=Path(root);b=json.loads((root/c['rig_binding']['path']).read_text());source=json.loads((root/c['source']['path']).read_text());frames=c['frames'];receipt=json.loads((root/c['approval_receipt']['path']).read_text())
 allbindings=[c['rig_binding'],c['source'],c['approval_receipt'],c['prop_binding']]+c['approved_references']+[v for f in frames for k,v in f.items() if k not in ['index','isolated']]+[v for f in frames for v in f['isolated'].values()]
 checks=dict(input_hashes=all(sha(root/x['path'])==x['sha256'] for x in allbindings),eight_ordered_frames=len(frames)==8 and [f['index'] for f in frames]==list(range(8)),source_binding=b['source_sha256']==c['source']['sha256'],approved_references_covered=all(any(x['path']==r['path'] and x['sha256']==r['sha256'] for r in receipt['files']) for x in c['approved_references']))
 checks['actual_asset_hashes']=all(sha(root/c['asset_root']/d['file'])==d['sha256'] for d in b['assets'].values())
 required={s+'.'+p for s in ['left','right'] for p in ['upperarm','forearm','shin','hand']}
 checks['required_material_sections']=set(c['sections'])==required
 checks['two_required_feet_observed']=set(c['support_windows'])=={'left.foot','right.foot'}
 checks['declared_owner_chains']=all(all(k.startswith(name.split('.')[0]+'.') for k in d['chain']) for name,d in b['assets'].items() if name.startswith(('left.','right.')) and 'chain' in d)
 camera=source['cameras']['rear'];inverse=np.linalg.inv(np.array(camera['world_matrix']));pixels=512/camera['ortho_scale'];G=np.array(b['whole_bank_rest_matrix']);display=b['display_matrix'];projection_errors=[]
 for i,f in enumerate(source['frames']):
  for name,point in f['points'].items():
   p=inverse@np.array([*point['world_xyz'],1]);raw=np.array([192+pixels*p[0],256-pixels*p[1]]);shown=display[0]*raw+np.array(display[4:6]);expected=(G@np.array([*shown,1]))[:2];projection_errors.append(float(np.linalg.norm(expected-b['frames'][i]['source_points'][name])))
 checks['independent_source_camera_projection']=max(projection_errors)<.001
 checks['positive_unmirrored_matrices']=all(np.linalg.det(np.array(p['matrix'])[:,:2])>0 for f in b['frames'] for p in f['parts'])
 full=[image(root,f['full']) for f in frames];checks['identical_neutral_character_pixels']=np.array_equal(np.array(full[0]),np.array(full[7]));extents=[foreground(im) for im in full];checks['all_contours_unclipped']=all(x['boundary_pixels']==0 for x in extents)
 checks['approved_neutral_height_and_ground']=all(extents[i]['height']==c['reference_height_px'] and extents[i]['bbox'][3]==c['reference_ground_y'] for i in [0,7])
 widths={};points=[];recomposition=[];overlap=[]
 for name,policy in c['sections'].items():
  d=b['assets'][name];pivot=np.array(d['pivot']);end=np.array(d['end']);point=pivot+(end-pivot)*policy['fraction'];observations=[]
  for i,f in enumerate(frames):
   rec=next(p for p in b['frames'][i]['parts'] if p['name']==name);M=np.array(rec['matrix']);center=M@np.array([*point,1]);axis=np.array(b['frames'][i]['source_points'][d['chain'][1]])-b['frames'][i]['source_points'][d['chain'][0]];observations.append(section(image(root,f['isolated'][name]),center,axis))
   points.extend([float(np.linalg.norm(M@np.array([*pivot,1])-b['frames'][i]['source_points'][d['chain'][0]])),float(np.linalg.norm(M@np.array([*end,1])-b['frames'][i]['source_points'][d['chain'][1]]))])
  values=[o['width_px'] for o in observations if o['known']];interval=[min(values),max(values)] if values else None
  passed=len(values)==8 and interval[1]-interval[0]<=policy['max_variation_px'] and policy['width_interval_px'][0]<=interval[0] and interval[1]<=policy['width_interval_px'][1]
  widths[name]=dict(observations=observations,range_px=interval,pass_=passed,policy=policy)
 checks['all_reviewed_material_sections']=bool(widths) and all(v['pass_'] for v in widths.values());checks['authored_chain_attachment_error']=max(points,default=math.inf)<1e-5
 for i,f in enumerate(frames):
  a=image(root,f['back']);a.alpha_composite(image(root,f['head']));a.alpha_composite(image(root,f['front']));recomposition.append(np.array_equal(np.array(a),np.array(full[i])))
  xy=b['frames'][i]['source_points']['neck'];x,y=[int(round(v)) for v in xy];box=(max(0,x-18),max(0,y-18),min(384,x+19),min(512,y+19));h=np.array(image(root,f['head']).crop(box).getchannel('A'))>=128;body=np.array(image(root,f['back']).crop(box).getchannel('A'))>=128;overlap.append(int((h&body).sum()))
 checks['two_logical_slots_three_pass_exact_recomposition']=all(recomposition);checks['visible_neck_cloth_overlap']=min(overlap)>=c['minimum_neck_overlap_pixels']
 feet={}
 for name,roi in c['support_windows'].items():
  arrays=[np.array(image(root,f['isolated'][name])) for f in frames];patches=[np.array(im.crop(tuple(roi))) for im in full];masks=[a[:,:,3]>=128 for a in patches];rgba_diffs=[int(np.abs(a.astype(int)-patches[0].astype(int)).max()) for a in patches]
  feet[name]=dict(isolated_pixels_identical=all(np.array_equal(a,arrays[0]) for a in arrays),full_support_masks_identical=all(np.array_equal(a,masks[0]) for a in masks),full_support_max_rgba_delta=max(rgba_diffs),window=roi)
 checks['stationary_painted_feet']=all(v['isolated_pixels_identical'] and v['full_support_masks_identical'] and v['full_support_max_rgba_delta']<=c['support_rgba_budget'] for v in feet.values())
 peak=source['grasp_frame'];hand=np.array(image(root,frames[peak]['isolated']['right.hand']).getchannel('A'))>=128;prop=np.array(image(root,frames[peak]['prop']).getchannel('A'))>=128;contact=float(distance_transform_edt(~prop)[hand].min()) if prop.any() and hand.any() else None
 checks['actual_hand_item_rasters_touch']=contact is not None and contact<=c['contact_budget_px']
 propdata=json.loads((root/c['prop_binding']['path']).read_text());gem=Image.open(root/c['asset_root']/'gem-texture.png').convert('RGBA');prop_ok=sha(root/c['asset_root']/'gem-texture.png')==propdata['texture_sha256'];scene_ok=True
 for i,f in enumerate(frames):
  pf=propdata['frames'][i];v=inverse@np.array([*source['frames'][i]['object_center'],1]);raw=np.array([192+pixels*v[0],256-pixels*v[1]]);shown=display[0]*raw+np.array(display[4:6]);expected=(G@np.array([*shown,1]))[:2];prop_ok &= float(np.linalg.norm(expected-pf['center']))<.001 and pf['visible']==source['frames'][i]['object_visible']
  M=np.vstack([pf['matrix'],[0,0,1]]);I=np.linalg.inv(M);layer=gem.convert('RGBa').transform((384,512),Image.Transform.AFFINE,tuple(I[:2].flatten()),Image.Resampling.BICUBIC).convert('RGBA') if pf['visible'] else Image.new('RGBA',(384,512));prop_ok &= np.array_equal(np.array(layer),np.array(image(root,f['prop'])))
  composed=Image.new('RGBA',(384,512));composed.alpha_composite(image(root,f['prop']));composed.alpha_composite(full[i]);scene_ok &= np.array_equal(np.array(composed),np.array(image(root,f['scene'])))
 checks['actual_item_pixels_follow_source']=bool(prop_ok);checks['actual_scene_recomposition']=bool(scene_ok)
 checks['no_opaque_extra_foreground_collar']='collar' not in b['draw_order']
 return dict(checks=checks,widths=widths,feet=feet,neutral_extents=[extents[0],extents[7]],neck_overlap_pixels=overlap,max_authored_attachment_error_px=max(points,default=math.inf),contact_pixel_distance=contact,bounded_rig_metrics_pass=all(checks.values()),full_family_proportion_status='UNKNOWN: different front/rear views, garment occlusion and no approved matched-view shape adapter',agent_art_approval=False,production_pass=False,scope='Authored rig material width, source attachment, actual support raster and pass composition checks only. No automatic new-drawing anatomy/ownership detection, hidden joints, volume, complete acting/cloth/finger or factory acceptance.')

def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);p.add_argument('--require-metrics',action='store_true');p.add_argument('--require-production',action='store_true');a=p.parse_args();q=run(json.loads(a.contract.read_text()),a.root);a.out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q['checks']));return int((a.require_metrics and not q['bounded_rig_metrics_pass']) or (a.require_production and not q['production_pass']))
if __name__=='__main__':raise SystemExit(main())
