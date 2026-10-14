"""New rear view; common row packing and two isolated native repairs are explicit."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def receiver(image):
    a=np.asarray(image.convert('RGBA'));r,g,b=a[:,:,:3].astype(float).transpose(2,0,1)
    y,x=np.mgrid[:a.shape[0],:a.shape[1]];ys,xs=np.where(a[:,:,3]>=128);top=int(ys.min())
    gr=np.divide(g,r,out=np.zeros_like(g),where=r>0);br=np.divide(b,r,out=np.zeros_like(b),where=r>0)
    mask=(a[:,:,3]>=128)&(y>=top)&(y<top+21)&(x>120)&(x<240)&(r>140)&(gr>.65)&(gr<.9)&(br>.55)&(br<.82)
    sy,sx=np.where(mask)
    if len(sx)<30:raise ValueError('Skin observation unknown: do not substitute a bone')
    center=[float(sx.mean()),float(sy.mean())+3]
    return dict(center=center,points=[[center[0]-16,center[1]],[center[0]+16,center[1]]],pixels=int(len(sx)),top=top,mask=mask)

def main():
    im=Image.open(P/'body-attempt3-raw.png').convert('RGBA');assert im.size==(1536,1024)
    folder=P/'body-canonical';folder.mkdir(exist_ok=True)
    for i in range(8):
        c=im.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512))
        if i>=4:assert np.array(c)[489:,:,3].max()<128,'Row repair would cut actual foreground'
        out=Image.new('RGBA',(384,512));out.paste(c,(0,23 if i>=4 else 0));out.save(folder/f'{i:02}.png')
    clipped=np.asarray(im)[1001:,:,3]
    packing=dict(native=bind(P/'body-attempt3-raw.png'),row_offsets=[[0,0],[0,23]],method='One shared integer row-origin correction, not individual-frame foot fitting. All four raw lower-row near soles are463 versus486 in all four upper cells; same correction also moves collar/cape/arms. No resampling. Original native atlas is retained including off-canvas noise.',near_sole_raw_y=[486]*4+[463]*4,visible_foreground_cut_alpha128=False,clipped_nonzero_alpha_pixels=int(np.count_nonzero(clipped)),clipped_max_alpha=int(clipped.max()),raw_alpha_failure_not_rescued=True)
    (P/'packing-receipt.json').write_text(json.dumps(packing,indent=2)+'\n')
    normalizations=[]
    for key in [1,4]:
        raw=P/f'repair-key{key}-raw.png';src=Image.open(raw).convert('RGBA');w,h=src.size;assert w==h
        inverse=[w/512,0,w/8,0,h/512,0];src.transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC).save(P/f'repaired-key{key}.png')
        normalizations.append(dict(key=key,raw=bind(raw),inverse_matrix=inverse,source_plate=[1024,1024],input_paste=[128,0],input_scale=2,method='Known square canvas inverse only, no feature/bbox/foot fit'))
    (P/'normalization.json').write_text(json.dumps(normalizations,indent=2)+'\n')
    s=300/317;m=[s,0,0,s,192-192*s,480-486*s];head_pair=[[563,1000],[808,1000]];head_center=np.mean(head_pair,axis=0);hs=.13
    source=json.loads((P/'source/source.json').read_text());variants={};observations=[]
    # Two nearly upright native drawings are assigned explicitly: art6 is rest,
    # art7 is the tiny remaining recovery. No owner relabel or pixel repaint.
    indices=[6,1,2,3,4,5,7,6]
    for variant in ['raw8','review']:
        atlas=Image.new('RGBA',(1536,1024));paths=[]
        for i,j in enumerate(indices):
            path=P/f'repaired-key{i}.png' if variant=='review' and i in [1,4] else folder/f'{j:02}.png'
            atlas.paste(Image.open(path).convert('RGBA'),(i%4*384,i//4*512));paths.append(path)
        atlas_path=P/f'{variant}-verification-atlas.png';atlas.save(atlas_path);rows=[]
        for i,path in enumerate(paths):
            image=Image.open(path).convert('RGBA');o=receiver(image);center=np.array(o['center'])*s+np.array(m[4:]);points=o['points'];poly=[[points[0][0]-4,points[0][1]],[points[1][0]+4,points[1][1]],[points[1][0]+4,points[1][1]+24],[points[0][0]-4,points[0][1]+24]]
            row=dict(index=i,source_time_seconds=source['frames'][i]['source_time_seconds'],body=bind(path),raw_sheet=bind(atlas_path),raw_art_index=i,raw_sheet_kind='Locally packed verification atlas, NOT native full-strip output',body_matrix=m,head_matrix=[hs,0,0,hs,*list(center-head_center*hs)],body_collar_lip_points_native=points,observed_receiver_surface_xy=center.tolist(),collar_foreground_polygon_native=poly,visible_surface_proxy='Reviewed bounded skin-cap color centroid +3px; inner32px horizontal receiver, not a recovered anatomical neck joint',native_origin=dict(kind='isolated_key' if variant=='review' and i in [1,4] else 'whole_strip',art_index=indices[i]))
            rows.append(row)
            mask=Image.fromarray(np.uint8(o.pop('mask'))*255);mask.save(P/f'{variant}-skin-mask-{i:02}.png');observations.append(dict(variant=variant,index=i,body=bind(path),**o))
        variants[variant]=rows
    contract=dict(schema='rear-camera-coherent-motion-v1',canvas=[384,512],source=bind(P/'source/source.json'),original_source=bind(P.parent/'pickup-pilot-v31/source/source.json'),head=bind(P/'head-attempt1-raw.png'),head_insertion_points_native=head_pair,head_scale=hs,body_uniform_rest_matrix=m,body_rest_calibration=dict(raw_art_index=6,cap_y=169,sole_y=486,target_sole_y=480,cap_to_sole_height=300,scope='Single bank-rest calibration before motion review; not per-key fit'),variants=variants,clocks=dict(source=[190,180,190,180,190,180,190,600],game=[100]*7+[600]),terminal_hold_ms=600,minimum_distinct_body_drawings=7,receiver_endpoint_budget_px=3,planted_surface_budget_px=6,phase_warning_fraction=.25,recovery_overshoot_budget_px=2,forefoot_observation_rois_native=dict(near=[110,455,215,500],far=[215,435,305,479]),full_factory_production_pass=False,logical_slots=['body_outfit','complete_head_style'],render_passes=['body_outfit','head','body_owned_collar'],pose_map=indices,selection_policy='Native art6 reused for exact rest0/7; art7 is penultimate recovery. Early and initial-recovery keys use isolated native repairs. No final guide warp, shoe patch, per-key scale/translation or raster reflection.',packing=bind(P/'packing-receipt.json'),normalization=bind(P/'normalization.json'))
    contract['draw_order']=contract['render_passes']
    contract['guide_fidelity']=dict(source_to_display_displacement_scale=1.65*s,provisional_budget_px=8,added_after_phase_only_false_positive=True,scope='New diagnostic gate against the previously declared guide adapter;8px is provisional and does not replace established6px support/3px neck/.25phase budgets. Both retained candidate variants fail it; never calibrate independent axis amplitudes to approve a pose.')
    (P/'motion-contract.json').write_text(json.dumps(contract,indent=2)+'\n');(P/'visible-receiver-observations.json').write_text(json.dumps(dict(scope='Color-assisted visible skin cap proxy in manually inspected ROI. Thresholds are specific to this skin/material/camera, not an arbitrary character detector. Hidden joints/arm visibility remain unknown.',selection=dict(alpha_min=128,top_band_height=21,x_range=[120,240],red_min=140,green_red=[.65,.9],blue_red=[.55,.82],receiver_offset_y=3,inner_pair_width=32),observations=observations),indent=2)+'\n')
if __name__=='__main__':main()
