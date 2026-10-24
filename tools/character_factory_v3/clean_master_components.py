"""Remove detached neighboring-cell fragments without fitting or repainting.

Keep the main connected figure and nearby detached details. A source-registered
prop corridor also protects detached thin weapons. All retained RGBA is exact.
This is technical cleanup, not anatomical/semantic approval.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from source_capture_identity import verify_source_reference
from track_visible_cutouts import pin_inputs,verify_inputs


def clean(image, prop=None, near=8):
    pixels=np.array(image.convert('RGBA'));visible=pixels[:,:,3]>0
    if type(near) is not int or not 0<=near<=24:raise ValueError('Invalid nearby-detail radius')
    labels,count=ndimage.label(visible)
    if not count:raise ValueError('Empty master')
    sizes=np.bincount(labels.ravel());sizes[0]=0;main=labels==int(np.argmax(sizes))
    distance=ndimage.distance_transform_edt(~main)
    allowed=set(int(v)for v in np.unique(labels[distance<=near])if v)
    if prop:
        start,end=[np.asarray(prop[key],float)for key in ['grip','tip']]
        if not np.isfinite(start).all() or not np.isfinite(end).all():raise ValueError('Nonfinite prop coordinates')
        axis=end-start;length=float(np.linalg.norm(axis))
        if length<1:raise ValueError('Degenerate prop corridor')
        yy,xx=np.indices(visible.shape);delta=np.stack([xx-start[0],yy-start[1]],axis=2)
        along=delta@(axis/length);across=np.abs(delta[:,:,0]*axis[1]-delta[:,:,1]*axis[0])/length
        corridor=(along>=-24)&(along<=length+24)&(across<=24)
        for label in np.unique(labels[corridor]):
            if label and sizes[label]>=12 and (corridor&(labels==label)).sum()/sizes[label]>=.8:allowed.add(int(label))
    keep=np.isin(labels,list(allowed));removed=visible&~keep
    result=pixels.copy();result[~keep]=0
    if not np.array_equal(result[keep],pixels[keep]):raise ValueError('Retained pixels changed')
    return Image.fromarray(result),{'removed_detached_pixels':int(removed.sum()),'removed_component_sizes':[int(sizes[i])for i in range(1,count+1)if i not in allowed],'retained_pixel_changes':0,'source_prop_corridor_protection':bool(prop),'frame_translation':[0,0],'scale':1}


def build(guide,recipe_path,frames,output):
    if output.exists():raise ValueError('Choose a new cleanup destination')
    recipe=json.loads(recipe_path.read_text());source=json.loads((guide/'manifest.json').read_text())
    verification=verify_source_reference(recipe_path,guide)
    indices=recipe['source_pose_indices'];direction=recipe['direction'];size=recipe['source_size'];factor=source['job']['resolution']/size[0]
    paths=[frames/f'{i:03d}.png'for i in indices];pins=pin_inputs([Path(__file__),guide/'manifest.json',recipe_path,*paths]);output.mkdir(parents=True);rows=[]
    for index,path in zip(indices,paths):
        image=Image.open(path)
        if image.mode!='RGBA' or list(image.size)!=size:raise ValueError('Master canvas differs')
        prop=source['views'][direction]['frames'][index].get('weapon_guide',{})
        prop={key:(np.array(prop[key])/factor).tolist()for key in ['grip','tip']}if {'grip','tip'}<=set(prop)else None
        result,row=clean(image,prop);result.save(output/f'{index:03d}.png');rows.append({'index':index,**row})
    verify_inputs(pins)
    proof={'status':'DETACHED_FRAGMENT_CLEANUP_REQUIRES_SEMANTIC_REVIEW','source_verification':verification,'frames':rows,'input_pins':pins,'painted_anatomy_modified':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['guide','recipe','frames','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.guide,a.recipe,a.frames,a.output)))
