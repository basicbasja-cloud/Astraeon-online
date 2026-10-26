"""Partition visible sprite roles from explicit same-frame semantic annotations.

All source RGBA is retained exactly once. Hidden surfaces and swap readiness
are separate gates. No pose inference from a misleading cuff-color heuristic.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def composite(images):
    result=Image.new('RGBA',images[0].size)
    for image in images:result=Image.alpha_composite(result,image)
    return result

def faint_edges(mask,alpha):
    padded=np.pad(mask,2);near=mask.copy();h,w=mask.shape
    for y in range(-2,3):
        for x in range(-2,3):
            if x*x+y*y<=4:near|=padded[2+y:2+y+h,2+x:2+x+w]
    return mask|(near&(alpha>0)&(alpha<=200))


def partition(image,masks,priority):
    values=np.array(image.convert('RGBA'));labels=np.zeros(values.shape[:2],np.uint8)
    if set(priority)!=set(masks)or len(priority)!=len(set(priority)):raise ValueError('Semantic priority differs from annotated roles')
    for i,name in enumerate(priority,1):
        if masks[name].shape!=labels.shape:raise ValueError('Semantic mask canvas differs')
        labels[masks[name]&(values[:,:,3]>0)]=i
    parts={}
    for i,name in enumerate(['BodyCostume',*priority]):
        out=np.zeros_like(values);out[labels==i]=values[labels==i];parts[name]=Image.fromarray(out)
    if composite(list(parts.values())).tobytes()!=image.convert('RGBA').tobytes():raise ValueError('Annotated partition changed source pixels')
    return parts,labels


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['masters','annotations','checkpoint','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh annotation proposal')
    if sha(a.checkpoint)!='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':raise ValueError('Unexpected SAM2 checkpoint')
    annotation=json.loads(a.annotations.read_text());frozen={str(f):sha(f)for f in [a.annotations,a.checkpoint]};implementation=sha(__file__)
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4)
    predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(a.checkpoint),device='cpu',apply_postprocessing=False))
    a.output.mkdir(parents=True);records=[]
    for row in annotation['frames']:
        i=row['index'];path=a.masters/f'{i:03}.png';digest=sha(path)
        if digest!=row['source_sha256']:raise ValueError('Annotated same-frame source changed')
        frozen[str(path)]=digest;image=Image.open(path).convert('RGBA');pixels=np.array(image);bg=Image.new('RGBA',image.size,'#aaa');bg.alpha_composite(image);predictor.set_image(np.array(bg.convert('RGB')));masks={};report={}
        for role,entry in row['roles'].items():
            positive=entry['positive'];negative=entry['negative'];points=np.array(positive+negative,np.float32);labels=np.array([1]*len(positive)+[0]*len(negative));box=np.array(entry['box'],np.float32)
            with torch.inference_mode():proposals,scores,_=predictor.predict(point_coords=points,point_labels=labels,box=box,multimask_output=True,return_logits=True)
            options=[]
            yy,xx=np.indices(pixels.shape[:2]);scope=(xx>=box[0])&(yy>=box[1])&(xx<box[2])&(yy<box[3])
            for k,proposal in enumerate(proposals):
                mask=(proposal>0)&scope&(pixels[:,:,3]>0)
                if not entry['pixel_range'][0]<=mask.sum()<=entry['pixel_range'][1]:continue
                if all(bool(proposal[int(y),int(x)]>0)==bool(label)for(x,y),label in zip(points,labels)):options.append(k)
            if not options:
                (a.output/'failure.json').write_text(json.dumps({'index':i,'role':role,'reason':'No candidate respects all same-frame annotations'},indent=2)+'\n');raise ValueError('Semantic annotation failed: '+role+' '+str(i))
            k=max(options,key=lambda n:scores[n]);masks[role]=faint_edges((proposals[k]>0)&scope,pixels[:,:,3])
            report[role]={'candidate':k,'score':float(scores[k]),'visible_pixels':int((masks[role]&(pixels[:,:,3]>0)).sum())}
        parts,labels=partition(image,masks,annotation['priority']);hashes={}
        for name,part in parts.items():
            folder=a.output/name;folder.mkdir(exist_ok=True);target=folder/f'{i:03}.png';part.save(target);hashes[name]=sha(target)
        folder=a.output/'labels';folder.mkdir(exist_ok=True);Image.fromarray(labels).save(folder/f'{i:03}.png')
        records.append({'index':i,'sha256':hashes,'semantic_proposals':report,'source_sha256':digest,'recomposition_changed_pixels':0})
        print('ANNOTATED_ROLE_PROPOSAL',i,flush=True)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Annotated source or implementation changed')
    (a.output/'receipt.json').write_text(json.dumps({'status':'ANNOTATED_VISIBLE_ROLES_NOT_SWAP_READY','frames':records,'priority':annotation['priority'],'input_sha256':frozen,'implementation_sha256':implementation,'hidden_surfaces_authored':False,'runtime_admitted':False},indent=2)+'\n')
    replay=a.output/'replay';replay.mkdir()
    shutil.copyfile(__file__,replay/'propose_annotated_roles.py')


if __name__=='__main__':main()
