"""Validate native render snapshot consistency; never certify painted contacts."""
import hashlib
import math
import re


def bounded(value,maximum):
    return type(value)in(int,float)and math.isfinite(value)and 0<=value<=maximum


def finite_vector(value,size):
    return isinstance(value,list)and len(value)==size and all(type(v)in(int,float)and math.isfinite(v)for v in value)


def valid_render_snapshot_capture(job,manifest,folder):
    if 'render_snapshot_revision'not in job:return True
    try:
        if type(job['render_snapshot_revision'])is not int or job['render_snapshot_revision']!=1:return False
        if type(job['resolution'])is not int or job['resolution']<1 or type(job['frames'])is not int or job['frames']<1:return False
        if not isinstance(job['directions'],list)or not job['directions']or len(set(job['directions']))!=len(job['directions']):return False
        if any(d not in {'S','SW','W','NW','N','NE','E','SE'}for d in job['directions']):return False
        proof=manifest['render_snapshot']
        if type(proof['revision'])is not int or proof['revision']!=1 or proof['applied']is not True:return False
        implementation=job['render_snapshot_sha256'];png=job['render_snapshot_png_sha256']
        if not all(isinstance(v,str)and re.fullmatch('[0-9a-f]{64}',v)for v in(implementation,png)):return False
        if proof['implementation_sha256']!=implementation:return False
        digests=manifest['implementation_digests_at_process_start']
        if digests.get('render_hit_snapshot_guides.py')!=implementation or digests.get('seal_source_guide_replay.py')!=png:return False
        if proof['source_fcurves_or_mute_flags_changed']is not False or proof['source_samples_or_camera_changed']is not False:return False
        if not re.fullmatch('[0-9a-f]{64}',proof['source_fcurves_sha256_before_and_after']):return False
        expected={f'{d}/{i:03}.png':(d,i)for d in job['directions']for i in range(job['frames'])}
        rows=proof['frames']
        if not isinstance(rows,list)or len(rows)!=len(expected)or{r['image']for r in rows}!=set(expected):return False
        counts=set()
        for row in rows:
            direction,index=expected[row['image']];reference=manifest['views'][direction]['frames'][index]
            if type(row['index'])is not int or row['index']!=index:return False
            if type(row['source_frame'])not in(int,float)or not math.isfinite(row['source_frame']):return False
            if row['source_action']!=reference['action']or row['source_frame']!=reference['source_frame']:return False
            if type(row['bones'])is not int or row['bones']<1:return False
            counts.add(row['bones'])
            for name in('max_before_render_matrix_component_error','max_after_render_matrix_component_error'):
                if not bounded(row[name],1e-5):return False
            matrices=[row['declared_object_world_matrix'],row['evaluated_object_world_matrix_after_render']]
            if any(not isinstance(m,list)or len(m)!=4 or not all(finite_vector(v,4)for v in m)for m in matrices):return False
            if max(abs(matrices[0][r][c]-matrices[1][r][c])for r in range(4)for c in range(4))>1e-5:return False
            if set(row['joints'])!={'head','pelvis','hand_r','hand_l','foot_r','foot_l'}:return False
            for data in row['joints'].values():
                a,b=data['declared_source_px'],data['evaluated_after_render_px']
                if not finite_vector(a,2)or not finite_vector(b,2):return False
                actual=math.dist(a,b)*240/job['resolution']
                reported=data['distance_runtime_px']
                if not bounded(actual,1e-3)or not bounded(reported,1e-3)or abs(actual-reported)>1e-8:return False
            if row['canvas']!=[job['resolution'],job['resolution']]:return False
            if not re.fullmatch('[0-9a-f]{64}',row['rgba_sha256']):return False
            path=folder/row['image']
            if not path.is_file()or hashlib.sha256(path.read_bytes()).hexdigest()!=row['png_sha256']:return False
        return len(counts)==1
    except (KeyError,TypeError,ValueError,OSError,AttributeError):
        return False
