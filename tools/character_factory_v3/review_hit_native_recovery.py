"""Build bounded Hit source/painting diagnostics without altering masters or plans."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qualify_cropped_paint_resolution import qualify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build(audit,candidate,output):
    if output.exists()or output.is_symlink():raise ValueError('Choose fresh output')
    data=json.loads(audit.read_text());rows=data['frames'];source=json.loads((candidate/'source-manifest.json').read_text())
    if data['manifest_sha256']!=sha(candidate/'source-manifest.json'):raise ValueError('Source mismatch')
    if data['fcurves_or_mute_flags_changed']is not False or data['max_recorded_landmark_world_error_m']>1e-5:raise ValueError('Unexpected dense source')
    output.mkdir(parents=True)
    times=[r['source_frame']for r in rows]
    def points(name,direction='SW'):return [r['runtime_projected_points'][direction][name]for r in rows]
    metrics={}
    for name in ('head','hand_r','foot_l','foot_r','sword_tip'):
        values={}
        for direction in source['job']['directions']:
            p=points(name,direction);bytime={t:point for t,point in zip(times,p)}
            prior=math.dist(bytime[8.],bytime[9.]);tail=math.dist(bytime[9.],bytime[10.])
            u=np.subtract(bytime[9.],bytime[8.]);v=np.subtract(bytime[10.],bytime[9.]);denom=np.linalg.norm(u)*np.linalg.norm(v)
            values[direction]={'source_8_to_9_runtime_px':prior,'source_9_to_10_runtime_px':tail,
                'tail_over_prior_distance':tail/prior if prior>1e-12 else None,
                'prior_tail_direction_cosine':float(np.dot(u,v)/denom)if denom>1e-12 else None}
        metrics[name]=values
    plt.rcParams['svg.hashsalt']='native-hit-recovery-20261102'
    fig,axes=plt.subplots(3,1,figsize=(9,8),layout='constrained')
    for name,color in [('head','#6d3c98'),('sword_tip','#267c92')]:
        p=points(name);displacement=[math.dist(v,p[0])for v in p]
        axes[0].plot(times,displacement,label=name,color=color)
        speeds=[math.dist(p[i],p[i-1])/(times[i]-times[i-1])for i in range(1,len(times))]
        axes[1].plot([(times[i]+times[i-1])/2 for i in range(1,len(times))],speeds,label=name,color=color)
        axes[2].plot([v[0] for v in p],[v[1]for v in p],label=name,color=color)
    axes[0].set(ylabel='distance from first pose (runtime px)',title='SW native Hit: source motion, no new transition or retiming')
    axes[1].set(ylabel='travel / source frame (runtime px)',xlabel='native source frame (not gameplay seconds)')
    for axis in axes[:2]:axis.axvspan(9,10,color='#f6cc8a',alpha=.4);axis.grid(alpha=.2);axis.legend()
    axes[2].set(xlabel='projected runtime X',ylabel='projected runtime Y');axes[2].invert_yaxis();axes[2].legend();axes[2].grid(alpha=.2)
    fig.savefig(output/'native-recovery.png',dpi=140);fig.savefig(output/'native-recovery.svg',metadata={'Date':None});plt.close(fig)
    svg=output/'native-recovery.svg';svg.write_text('\n'.join(line.rstrip()for line in svg.read_text().splitlines())+'\n')
    with Image.open(candidate/'raw.png')as image:paint=image.convert('RGBA')
    with Image.open(candidate/'guide.png')as image:guide=image.convert('RGB')
    if paint.size!=(1448,1086)or guide.size!=(1536,1152):raise ValueError('Unexpected exact sheet grid')
    manifest=source['views']['SW']['frames'];frames=[];native=362
    manual={0:[235.,131.],7:[240.,161.],11:[236.,131.]}
    annotation=candidate/'manual-tip-annotations.json'
    if annotation.exists():
        recorded=json.loads(annotation.read_text())
        if recorded['raw_sha256']!=sha(candidate/'raw.png')or recorded['native_slot']!=[362,362]or recorded['radial_uncertainty_native_px']!=3:raise ValueError('Invalid native tip annotations')
        manual={int(k):v for k,v in recorded['tips'].items()}
    elif candidate.name!='swordsman-hit-snapshot-wholesheet-20261102':raise ValueError('New candidates require manual tip annotations')
    tip_results={}
    for i in range(12):
        x=i%4;y=i//4
        rgba=paint.crop((x*native,y*native,(x+1)*native,(y+1)*native))
        cell=Image.new('RGBA',(native,native),'white');cell.alpha_composite(rgba)
        draw=ImageDraw.Draw(cell)
        projected={}
        for name,p in manifest[i]['weapon_guide'].items():
            v=[(p[0]-448)*native/640,(p[1]-520)*native/640];projected[name]=v
            draw.ellipse((v[0]-3,v[1]-3,v[0]+3,v[1]+3),outline='#ff00d8',width=2)
            draw.text((v[0]+5,v[1]+2),name,fill='#b00088')
        if i in manual:
            p=manual[i];draw.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),outline='#008b9a',width=2)
            draw.line([tuple(projected['tip']),tuple(p)],fill='#008b9a',width=1)
            tip_results[str(i)]={'manually_marked_painted_tip_native_slot_px':p,
                'source_tip_native_slot_px':projected['tip'],'manual_point_uncertainty_native_px':3,
                'endpoint_distance_runtime_px':math.dist(projected['tip'],p)*640/native*240/1536,
                'uncertainty_runtime_px':3*640/native*240/1536,
                'sole_contact_measurement':False}
        board=Image.new('RGB',(724,394),'white');board.paste(guide.crop((x*384,y*384,(x+1)*384,(y+1)*384)).resize((362,362),Image.Resampling.LANCZOS),(0,32));board.paste(cell.convert('RGB'),(362,32))
        d=ImageDraw.Draw(board);d.text((6,8),f'SW {i:03d} source',fill='black');d.text((368,8),'paint draft + source controls',fill='black');frames.append(board)
        if i in manual:board.save(output/f'SW{i:03d}-controls.png')
    for name,duration in [('normal',100),('slow',300)]:frames[0].save(output/f'paint-{name}-one-shot.gif',save_all=True,append_images=frames[1:],duration=duration,disposal=2)
    first=np.asarray(paint.crop((0,0,362,362)))
    last=np.asarray(paint.crop((1086,724,1448,1086)))
    baseline=json.loads((ROOT/'docs/character-factory/review/restore-tall-swordsman-baseline-20261026/baseline-proof.json').read_text())['baseline_files']
    assert all(sha(ROOT/p)==digest for p,digest in baseline.items())
    summary={'status':'SOURCE_AND_REJECTED_PAINT_DIAGNOSTIC_NOT_ACCEPTANCE','source_samples':len(rows),'bones':data['bones'],
        'source_frame_range':data['action_range'],'source_first_last_all_bone_world_matrix_error':data['first_last_all_bone_world_matrix_component_error'],
        'matches_twelve_recorded_pose_world_landmarks_max_m':data['max_recorded_landmark_world_error_m'],
        'native_interval_diagnostics':metrics,'manual_painted_tip_diagnostics':tip_results,
        'native_sheet_canvas':list(paint.size),'native_slot':[362,362],'target_slot':[768,768],
        'resolution_qualification':qualify(list(paint.size),[4,3],[1536,1536],[448,520,1088,1160],[768,768]),
        'transparent_pixel_count':int((np.asarray(paint)[:,:,3]==0).sum()),'per_frame_fit_or_repair_performed':False,
        'first_last_painted_slot_rgba_different_pixels':int(np.any(first!=last,axis=2).sum()),
        'first_last_difference_is_not_anatomical_or_semantic_score':True,
        'baseline_hashes_matched':len(baseline),'production_plan_or_art_modified':False,
        'completed_characters':0,'new_gameplay_tests':0,'gif_loop_extension':False,
        'input_sha256':{str(p.relative_to(ROOT)):sha(p)for p in (audit,candidate/'raw.png',candidate/'guide.png',candidate/'source-manifest.json')},
        'implementation_sha256':sha(Path(__file__)),
        'resolution_qualification_implementation_sha256':sha(Path(__file__).with_name('qualify_cropped_paint_resolution.py')),
        'limitations':['Projected bone origins are not sole contacts; no sole-contact pass is claimed.',
                       'Manual painted tip annotations have a 3-native-pixel radial uncertainty.',
                       'Native time units and diagnostic preview timing are not approved gameplay timing.',
                       'Dense sampling preserves the native return segment and does not repair its velocity change.',
                       'The cropped native detail can downsample into authoring768, but geometry, other directions, semantic layers and runtime remain unapproved.']}
    (output/'proof.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit',type=Path,required=True);parser.add_argument('--candidate',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=build(args.audit.resolve(),args.candidate.resolve(),args.output.resolve())
    print(json.dumps({k:result[k]for k in ('source_samples','native_slot','baseline_hashes_matched','manual_painted_tip_diagnostics')}))
