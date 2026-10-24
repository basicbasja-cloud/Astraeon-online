"""Use source sockets to propose same-frame head and weapon cutouts with SAM2.

Original RGBA pixels are partitioned exactly once. Scores, source socket proximity
and exact recomposition never constitute semantic or animation acceptance.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw

from track_visible_cutouts import partition_visible,pin_inputs,verify_inputs,sha
from source_capture_identity import verify_source_reference,reference_sidecar


def nearest_visible(pixels,target,scope=None):
    selected=pixels[:,:,3]>16
    if scope is not None:selected&=scope
    yy,xx=np.where(selected)
    if not len(xx):raise ValueError('No visible prompt candidate')
    index=np.argmin((xx-target[0])**2+(yy-target[1])**2)
    return [int(xx[index]),int(yy[index])]


def source_prompts(pixels,record,factor):
    height,width=pixels.shape[:2];yy,xx=np.indices((height,width))
    head=np.array(record['landmarks']['head'])/factor
    hx,hy=head;head_box=[max(0,hx-68),max(0,hy-84),min(width-1,hx+76),min(height-1,hy+18)]
    x0,y0,x1,y1=head_box;scope=(xx>=x0)&(xx<=x1)&(yy>=y0)&(yy<=y1)
    hair=nearest_visible(pixels,head+[0,-28],scope)
    head_negative=[[float(min(width-1,hx+12)),float(min(height-1,hy+30))]]
    # Projected hand joints may be hidden behind the head, shoulder or hilt.
    # They are geometry references, not observed visible glove pixels. Only
    # actual same-frame manual annotations may add hand exclusion prompts.
    prompts={'HeadHair':{'box':head_box,'positive':[hair],'negative':head_negative}}
    prop=record.get('weapon_guide',{})
    if not {'grip','tip'}<=set(prop):raise ValueError('This proposal requires a single sword/staff source guide')
    grip=np.array(prop['grip'])/factor;tip=np.array(prop['tip'])/factor;axis=tip-grip
    if np.linalg.norm(axis)<10:raise ValueError('Weapon is too foreshortened for automatic prompting; annotate manually')
    length=np.linalg.norm(axis);unit=axis/length
    delta=np.stack([xx-grip[0],yy-grip[1]],axis=2)
    along=delta@unit;across=np.abs(delta[:,:,0]*unit[1]-delta[:,:,1]*unit[0])
    rgb=pixels[:,:,:3].astype(float);maximum=rgb.max(axis=2);minimum=rgb.min(axis=2)
    metal=(maximum-minimum<.30*np.maximum(maximum,1))&(maximum>75)
    # Head/hair is a common false positive for pale sword blades.
    metal&=~(((xx-hx)/48)**2+((yy-(hy-22))/42)**2<1)
    band=metal&(along>length*.12)&(along<length*.95)&(across<24)
    positives=[]
    for t in [.35,.65]:
        point=nearest_visible(pixels,grip+axis*t,band)
        if np.linalg.norm(np.array(point)-(grip+axis*t))>35:raise ValueError('Painted blade is too far from source; annotate/repaint before cutouts')
        positives.append(point)
    lo=np.minimum(grip,tip)-28;hi=np.maximum(grip,tip)+28
    prompts['Weapon']={'box':[float(max(0,lo[0])),float(max(0,lo[1])),float(min(width-1,hi[0])),float(min(height-1,hi[1]))],
                       'positive':positives,'negative':[hair]}
    return prompts


def retain_soft_edges(pixels,mask):
    """Reassign nearby pale edge pixels, never change their color or alpha."""
    rgb=pixels[:,:,:3].astype(float);maximum=rgb.max(axis=2);minimum=rgb.min(axis=2)
    pale=(maximum-minimum<.3*np.maximum(maximum,1))&(maximum>100)
    padded=np.pad(mask,3);near=np.zeros_like(mask)
    for dy in range(-3,4):
        for dx in range(-3,4):
            if dx*dx+dy*dy<=9:near|=padded[3+dy:3+dy+mask.shape[0],3+dx:3+dx+mask.shape[1]]
    return mask|(near&pale&(pixels[:,:,3]>0))


def propose(guide,recipe_path,frames_folder,checkpoint,model_revision,output,annotations=None):
    if output.exists():raise ValueError('Preserve earlier proposals; choose a fresh output')
    recipe=json.loads(recipe_path.read_text());manifest_path=guide/'manifest.json';manifest=json.loads(manifest_path.read_text())
    if recipe.get('frame_space')!='canonical-authoring':raise ValueError('Canonical recipe required')
    source_verification=verify_source_reference(recipe_path,guide)
    direction=recipe['direction'];indices=recipe['source_pose_indices'];files=[frames_folder/f'{i:03d}.png'for i in indices]
    sidecar=reference_sidecar(recipe_path)
    pinned=pin_inputs([Path(__file__),manifest_path,recipe_path,checkpoint,*files]+([annotations]if annotations else [])+([sidecar]if sidecar.exists()else []))
    if sha(checkpoint)!='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69' or model_revision!='2b90b9f5ceec907a1c18123530e92e794ad901a4':raise ValueError('Use the retained licensed SAM2.1 tiny implementation and checkpoint')
    manual=json.loads(annotations.read_text())if annotations else {}
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4)
    model=build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False)
    predictor=SAM2ImagePredictor(model);output.mkdir(parents=True);records=[];failures=[]
    size=tuple(recipe['source_size']);factor=manifest['job']['resolution']/size[0]
    sheets={r:Image.new('RGBA',(size[0]*4,size[1]*((len(indices)+3)//4)))for r in ['HeadHair','BodyCostume','Weapon']}
    for slot,(index,path)in enumerate(zip(indices,files)):
        im=Image.open(path)
        if im.mode!='RGBA' or im.size!=size:raise ValueError('Canonical painted canvas differs')
        pixels=np.array(im);source=manifest['views'][direction]['frames'][index]
        try:prompts=manual.get(str(index)) or source_prompts(pixels,source,factor)
        except ValueError as error:
            failures.append({'index':index,'reason':str(error)});continue
        bg=Image.new('RGBA',size,'#e8e8e8');bg.alpha_composite(im);predictor.set_image(np.array(bg.convert('RGB')))
        logits=[];scores={};failed=None
        with torch.inference_mode():
            for role in ['HeadHair','Weapon']:
                p=prompts[role];points=np.array(p['positive']+p['negative'],dtype=np.float32);labels=np.array([1]*len(p['positive'])+[0]*len(p['negative']))
                masks,confidence,raw=predictor.predict(point_coords=points,point_labels=labels,box=np.array(p['box'],dtype=np.float32),multimask_output=True,return_logits=True)
                valid=[]
                for candidate in range(len(confidence)):
                    matches=True
                    for point,label in zip(points,labels):
                        x,y=np.rint(point).astype(int)
                        if not 0<=x<size[0]or not 0<=y<size[1]or (masks[candidate,y,x]>0)!=bool(label):matches=False;break
                    if matches:valid.append(candidate)
                if not valid:failed='No '+role+' proposal respects all manual/source prompts';break
                chosen=max(valid,key=lambda index:confidence[index]);mask=masks[chosen]>0
                x0,y0,x1,y1=p['box'];yy,xx=np.indices(mask.shape);scope=(xx>=x0)&(xx<=x1)&(yy>=y0)&(yy<=y1)
                mask&=scope;expanded=retain_soft_edges(pixels,mask)&scope
                logits.append(np.where(expanded,np.maximum(masks[chosen],.001),-100.));scores[role]=float(confidence[chosen])
        if failed:
            failures.append({'index':index,'reason':failed});continue
        parts=partition_visible(im,np.stack(logits),['HeadHair','Weapon'])
        visible={r:int(np.count_nonzero(np.array(part)[:,:,3]))for r,part in parts.items()}
        if not visible['HeadHair'] or not visible['Weapon']:
            failures.append({'index':index,'reason':'Empty role proposal; manual annotation required'});continue
        for role,part in parts.items():
            target=output/role;target.mkdir(exist_ok=True);part.save(target/f'{index:03d}.png');sheets[role].paste(part,((slot%4)*size[0],(slot//4)*size[1]))
        ids=np.zeros(pixels.shape[:2],dtype=np.uint8)
        for label,role in enumerate(['BodyCostume','HeadHair','Weapon'],1):ids[np.array(parts[role])[:,:,3]>0]=label
        target=output/'labels';target.mkdir(exist_ok=True);Image.fromarray(ids).save(target/f'{index:03d}.png')
        records.append({'index':index,'source_master_sha256':sha(path),'prompts':prompts,'proposal_scores':scores,'visible_pixels':visible,'recomposition_mismatch_pixels':0})
        print(json.dumps({'index':index,'status':'PARTITIONED_REQUIRES_SEMANTIC_REVIEW'}),flush=True)
    for role,sheet in sheets.items():sheet.save(output/(role+'-sheet.png'))
    verify_inputs(pinned)
    result={'status':'SOURCE_ASSISTED_VISIBLE_CUTOUT_PROPOSALS_NOT_APPROVED','guide_job':recipe['guide_job'],'direction':direction,'source_capture_verification':source_verification,
            'canonical_canvas':list(size),'model_repository':'https://github.com/facebookresearch/sam2','model_revision':model_revision,
            'checkpoint_sha256':sha(checkpoint),'implementation_sha256':sha(Path(__file__)),
            'complete_visible_partition':not failures and len(records)==len(indices),'frames':records,'failures':failures,
            'input_hashes':pinned,'hidden_surfaces_authored':False,'source_pixels_changed':False,'runtime_admitted':False,
            'semantic_boundary_review_required':True,'hand_occlusion_separated':False}
    (output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['guide','recipe','frames','checkpoint','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--model-revision',required=True);p.add_argument('--annotations',type=Path);a=p.parse_args()
    r=propose(a.guide,a.recipe,a.frames,a.checkpoint,a.model_revision,a.output,a.annotations)
    print(json.dumps({'frames':len(r['frames']),'failures':r['failures'],'complete_visible_partition':r['complete_visible_partition']}))
