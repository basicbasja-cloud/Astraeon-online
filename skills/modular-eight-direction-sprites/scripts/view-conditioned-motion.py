"""Camera-specific visible receiver phase + reused real neck/support pixel gates.

Two source/paint samples calibrate each projected axis. This tests temporal phase
and signed motion, not absolute 3D-to-painted anatomy or camera equivalence.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image
spec=importlib.util.spec_from_file_location('neck',Path(__file__).with_name('coherent-neck-motion.py'))
neck=importlib.util.module_from_spec(spec);spec.loader.exec_module(neck)
spec2=importlib.util.spec_from_file_location('boots',Path(__file__).with_name('visible-boot-components.py'))
boots=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(boots)

def phase(source,observed,limit=.25):
    source=np.array(source,dtype=float);observed=np.array(observed,dtype=float)
    # This reach action's peak is declared by the actual lowest world head height,
    # passed as sample3. Do not infer the peak from a noisy painted observation.
    peak=3;delta_source=source[peak]-source[0];delta_image=observed[peak]-observed[0]
    valid=bool(np.all(np.abs(delta_source)>1e-6) and np.all(np.abs(delta_image)>3))
    if not valid:return dict(pass_=False,reason='Insufficient observable projected excursion; unknown, never certify')
    expected=(source-source[0])/delta_source;actual=(observed-observed[0])/delta_image
    held=[1,2,4,5,6,7];errors=np.max(np.abs(actual[held]-expected[held]),axis=0)
    signed=bool(np.all(delta_source*delta_image>0))
    recovery=np.diff(observed[peak:,0]);towards_rest=np.sign(observed[0,0]-observed[peak,0]);backtrack=float(max(0,-np.min(recovery*towards_rest)))
    return dict(calibration_indices=[0,3],held_out_indices=held,source_normalized=expected.tolist(),observed_normalized=actual.tolist(),source_delta_xy=delta_source.tolist(),painted_delta_xy=delta_image.tolist(),axis_amplitude_ratio=(delta_image/delta_source).tolist(),held_out_max_error_xy=errors.tolist(),signed_direction_matches=signed,recovery_x_backtrack_px=backtrack,pass_=bool(signed and max(errors)<=limit and backtrack<=2),scope='Visible surface phase under two declared calibrations per axis; not absolute retarget accuracy, hidden anatomy, head orientation or contact forces')

def fidelity(source,observed,scale,budget):
    source=np.array(source,dtype=float);observed=np.array(observed,dtype=float)
    # One rest-origin calibration only; DO NOT fit independent X/Y amplitudes.
    expected=(source-source[0])*scale;actual=observed-observed[0]
    errors=np.linalg.norm(actual-expected,axis=1)
    return dict(calibration_indices=[0],held_out_indices=list(range(1,len(source))),expected_displacement_xy=expected.tolist(),observed_displacement_xy=actual.tolist(),errors_px=errors.tolist(),maximum_error_px=float(errors.max()),budget_px=budget,source_to_guide_scale=scale,pass_=bool(errors.max()<=budget),scope='Fidelity to the declared authoring guide displacement adapter, not automatic physical retarget accuracy or hidden joint recovery. No fitted peak, per-axis gain, per-key registration or art warp.')

def run(contract,root,renders):
    root=Path(root);renders=Path(renders);source=json.loads((root/contract['source']['path']).read_text());output={}
    common={}
    bindings=[contract['source'],contract['original_source'],contract['head'],contract['packing'],contract['normalization']]+[v for rows in contract['variants'].values() for r in rows for v in [r['body'],r['raw_sheet']]]
    common['input_hashes']=all(neck.digest(root/b['path'])==b['sha256'] for b in bindings)
    common['actual_external_asset_hash']=neck.digest(root/source['source_file'])==source['source_sha256']
    common['peak_world_height_is_sample3']=int(np.argmin([f['points']['head']['world_xyz'][2] for f in source['frames']]))==3
    common['logical_body_plus_head']=contract['logical_slots']==['body_outfit','complete_head_style']
    common['no_factory_approval']=not contract['full_factory_production_pass']
    for variant,rows in contract['variants'].items():
        passes=[{mode:np.array(Image.open(renders/variant/mode/f'{i:02}.png').convert('RGBA')) for mode in ['full','body','head','collar']} for i in range(8)]
        geometry=dict(common_body_matrix=all(r['body_matrix']==contract['body_uniform_rest_matrix'] for r in rows),positive_fixed_head_scale=all(neck.uniform_positive(r['head_matrix'],contract['head_scale']) for r in rows),exact_source_clock=[r['source_time_seconds'] for r in rows]==[f['source_time_seconds'] for f in source['frames']],seven_drawings=len({r['body']['sha256'] for r in rows})>=7,exact_rest_rgba=np.array_equal(passes[0]['full'],passes[7]['full']))
        geometry['positive_uniform_body']=bool(contract['body_uniform_rest_matrix'][0]>0 and all(neck.uniform_positive(r['body_matrix'],contract['body_uniform_rest_matrix'][0]) for r in rows))
        geometry['verification_atlas_crops']=all(np.array_equal(np.array(Image.open(root/r['body']['path']).convert('RGBA')),np.array(Image.open(root/r['raw_sheet']['path']).crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512)))) for i,r in enumerate(rows))
        n=[neck.neck_metrics(r,contract,p) for r,p in zip(rows,passes)]
        component_review=boots.sequence([np.array(Image.open(root/r['body']['path']).convert('RGBA')) for r in rows],[p['body'] for p in passes],contract['body_uniform_rest_matrix'][0],contract['planted_surface_budget_px'])
        supports=component_review['support']
        timing=phase([f['points']['head']['xy'] for f in source['frames']],[r['observed_receiver_surface_xy'] for r in rows],contract['phase_warning_fraction'])
        guide=fidelity([f['points']['head']['xy'] for f in source['frames']],[r['observed_receiver_surface_xy'] for r in rows],contract['guide_fidelity']['source_to_display_displacement_scale'],contract['guide_fidelity']['provisional_budget_px'])
        partial=bool(all(common.values()) and all(geometry.values()) and all(x['pass_'] for x in n) and component_review['pass_'] and timing['pass_'])
        output[variant]=dict(geometry=geometry,neck=n,support=supports,boot_component_review=component_review,projected_phase=timing,guide_fidelity=guide,phase_neck_support_pass=partial,metrics_pass=bool(partial and guide['pass_']),production_pass=False)
    return dict(scope='Bound rear-view candidate; source/painting phase and actual visible pixel checks only. Raw-alpha/acting/manual review remain separate.',integrity_checks=common,variants=output,production_pass=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--renders',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-motion',action='store_true');a=p.parse_args()
    r=run(json.loads(a.contract.read_text()),a.root,a.renders);a.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:dict(metrics_pass=v['metrics_pass'],phase=v['projected_phase']) for k,v in r['variants'].items()}));return 1 if a.require_motion and not r['variants']['review']['metrics_pass'] else 0
if __name__=='__main__':raise SystemExit(main())
