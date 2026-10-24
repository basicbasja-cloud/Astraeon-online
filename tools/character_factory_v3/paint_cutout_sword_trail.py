"""Paint a short post-cut ribbon using native tip history and painted blade fit.

FX only: never transform the character. Front/back placement is an explicit
artist decision, not a claim of mesh depth or collision accuracy.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label
from track_visible_cutouts import pin_inputs,verify_inputs,sha


def blade_axis(image,expected_grip):
    a=np.array(image.convert('RGBA'));rgb=a[:,:,:3].astype(float);maximum=rgb.max(2);minimum=rgb.min(2)
    mask=(a[:,:,3]>16)&(maximum>90)&((maximum-minimum)<.32*np.maximum(maximum,1))
    components,count=label(mask);choices=[]
    for i in range(1,count+1):
        y,x=np.where(components==i)
        if len(x)<10:continue
        points=np.column_stack([x,y]);values,vectors=np.linalg.eigh(np.cov(points.T));elongation=values[-1]/max(values[0],.01)
        if elongation<4:continue
        axis=vectors[:,-1];middle=points.mean(0);projected=(points-middle)@axis
        ends=[middle+axis*projected.min(),middle+axis*projected.max()];base,tip=sorted(ends,key=lambda p:np.linalg.norm(p-expected_grip))
        choices.append((elongation*np.sqrt(len(x)),base,tip))
    if not choices:raise ValueError('Painted blade requires explicit endpoint annotation')
    _,base,tip=max(choices,key=lambda item:item[0]);return base,tip


def bounded_history(history,base,tip,max_fraction=.55):
    if not 0<max_fraction<=.6:raise ValueError('Trail history must remain short')
    source=history[-1];v=source[1]-source[0];paint=tip-base
    if np.linalg.norm(v)<1 or np.linalg.norm(paint)<4:raise ValueError('Degenerate blade fit')
    angle=np.arctan2(paint[1],paint[0])-np.arctan2(v[1],v[0]);scale=np.linalg.norm(paint)/np.linalg.norm(v)
    matrix=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])*scale
    fitted=[(matrix@(g-source[0])+base,matrix@(t-source[0])+base)for g,t in history]
    maximum=np.linalg.norm(paint)*max_fraction;selected=[fitted[-1]];travel=0.
    for older in reversed(fitted[:-1]):
        newer=selected[0];distance=np.linalg.norm(newer[1]-older[1])
        if travel+distance>maximum:
            fraction=(maximum-travel)/max(distance,1e-9)
            selected.insert(0,(newer[0]+(older[0]-newer[0])*fraction,newer[1]+(older[1]-newer[1])*fraction));travel=maximum;break
        selected.insert(0,older);travel+=distance
    return selected,float(travel),float(maximum)


def ribbon(history,size):
    image=Image.new('RGBA',(size*2,size*2));draw=ImageDraw.Draw(image)
    lengths=[np.linalg.norm(b[1]-a[1])for a,b in zip(history,history[1:])];total=sum(lengths);elapsed=0.
    for (g0,t0),(g1,t1),length in zip(history,history[1:],lengths):
        for j in range(32):
            a=j/32;b=(j+1)/32;ga=g0+(g1-g0)*a;gb=g0+(g1-g0)*b;ta=t0+(t1-t0)*a;tb=t0+(t1-t0)*b
            age=(elapsed+length*b)/max(total,1e-9);color=np.array([91,78,132])*(1-age)+np.array([248,241,255])*age
            for band in range(10):
                inner=1-.75*age
                r0=inner+(1-inner)*band/10;r1=inner+(1-inner)*(band+1)/10
                polygon=[ga+(ta-ga)*r0,ga+(ta-ga)*r1,gb+(tb-gb)*r1,gb+(tb-gb)*r0]
                draw.polygon([tuple(p*2)for p in polygon],fill=(*map(int,color),int(225*age**.65)))
        elapsed+=length
    return image.resize((size,size),Image.Resampling.LANCZOS)


def build(guide,direction,weapons,history_manifest,output,depth):
    if output.exists():raise ValueError('Preserve previous effects; choose a fresh output')
    manifest=json.loads((guide/'manifest.json').read_text());view=manifest['views'][direction];records=view['frames']
    native=json.loads(history_manifest.read_text());clip=next(c for c in native['clips']if c['clip']==direction)
    if native.get('sha256')!=manifest['job']['source_sha256'] or native.get('source_rig')!='unretargeted' or manifest['job'].get('retarget_to'):raise ValueError('Native motion source/rig differs')
    old_pitch=native['camera']['rotation'][0];new_pitch=view['camera']['rotation'][0]
    old_yaw=np.deg2rad(clip['camera']['yaw_degrees']);new_yaw=view['camera']['rotation'][2]
    if abs(old_pitch-new_pitch)>1e-5 or abs(np.arctan2(np.sin(old_yaw-new_yaw),np.cos(old_yaw-new_yaw)))>1e-5:raise ValueError('Source camera orientations differ')
    reference=[r for r in clip['frames']if r['action']=='Sword_Attack'and r['source_frame']in [11,12,13]]
    if len(reference)!=3 or [r['source_frame']for r in reference]!=[11,12,13]:raise ValueError('Native cut history differs')
    emissions=[i for i,r in enumerate(records)if r['action']=='Sword_Attack'and abs(r['source_frame']-13)<1e-6]
    if len(emissions)!=1:raise ValueError('This trail requires the actual post-cut source pose 13')
    index=emissions[0];path=weapons/f'{index:03d}.png';pinned=pin_inputs([Path(__file__),guide/'manifest.json',path,history_manifest])
    painted=Image.open(path);size=painted.width
    if painted.mode!='RGBA' or painted.size!=(768,768):raise ValueError('Expected canonical actual painted weapon')
    expected=np.array(records[index]['weapon_guide']['grip'])/(manifest['job']['resolution']/size)
    base,tip=blade_axis(painted,expected);history=[(np.array(r['sword_grip'],float),np.array(r['sword_tip'],float))for r in reference]
    history,travel,maximum=bounded_history(history,base,tip);effect=ribbon(history,size);output.mkdir(parents=True)
    for i in range(manifest['frame_count']):
        layer=Image.new('RGBA',(size,size))
        if i==index:layer=effect.copy()
        elif i==index+1:
            layer=effect.copy();layer.putalpha(layer.getchannel('A').point(lambda a:round(a*.25)))
        for role in ['WeaponLightBack','WeaponLightFront']:
            folder=output/role;folder.mkdir(exist_ok=True);(layer if role==depth else Image.new('RGBA',(size,size))).save(folder/f'{i:03d}.png')
    verify_inputs(pinned)
    report={'status':'PAINT_REGISTERED_POST_CUT_FX_REVIEW','direction':direction,'guide_job':manifest['job']['id'],'input_hashes':pinned,
            'motion_source_sha256':native['sha256'],'native_and_target_camera_orientations_agree':True,
            'first_emission_index':index,'first_emission_source_frame':13,'fade_index':index+1,'native_history_source_frames':[11,12,13],
            'painted_blade_base':base.tolist(),'painted_blade_tip':tip.tolist(),'recent_tip_travel_author_px':travel,'maximum_recent_tip_travel_author_px':maximum,
            'depth':depth,'depth_is_artist_staging_not_mesh_occlusion':True,'body_or_weapon_pixels_transformed':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['guide','weapons','history-manifest','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--direction',required=True);p.add_argument('--depth',choices=['WeaponLightBack','WeaponLightFront'],required=True);a=p.parse_args()
    print(json.dumps(build(a.guide,a.direction,a.weapons,a.history_manifest,a.output,a.depth)))
