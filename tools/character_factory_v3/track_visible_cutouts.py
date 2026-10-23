"""Propagate reviewed visible-part masks through a fixed-canvas painted sequence.

Requires the separately installed official SAM2 package and a licensed checkpoint.
No model downloads, image generation, body warping, or runtime admission occur.
BodyCostume receives the unclaimed master pixels; hidden surfaces are not authored.
"""
import argparse,hashlib,json,tempfile
from pathlib import Path
import numpy as np
from PIL import Image

ROLES={'HeadHair','Weapon','WeaponHandOccluder','BackAccessory','Headgear'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def partition_visible(master,logits,roles,seed_masks=None):
    """Assign original RGBA pixels once; never feather the master alpha twice."""
    if master.mode!='RGBA':raise ValueError('Master must be RGBA')
    a=np.asarray(master);scores=np.asarray(logits)
    if not roles or len(set(roles))!=len(roles)or set(roles)-ROLES:raise ValueError('Invalid tracked roles')
    if scores.shape!=(len(roles),master.height,master.width)or not np.isfinite(scores).all():raise ValueError('Invalid mask scores')
    # Highest positive confidence wins when temporal proposals overlap.
    owner=np.argmax(scores,axis=0);claimed=scores.max(axis=0)>0
    result={}
    if seed_masks:
        reserved=np.zeros(claimed.shape,bool)
        for role,mask in seed_masks.items():
            mask=np.asarray(mask,dtype=bool)
            if role not in roles or mask.shape!=claimed.shape or np.any(reserved&mask):raise ValueError('Invalid or overlapping correction masks')
            reserved|=mask
            # A corrected role is authoritative for its complete visible mask.
            claimed&=owner!=roles.index(role)
        for role,mask in seed_masks.items():owner[mask]=roles.index(role);claimed|=mask
    claimed&=a[:,:,3]>0
    for i,role in enumerate(roles):
        pixels=a.copy();pixels[~(claimed&(owner==i))]=0;result[role]=Image.fromarray(pixels)
    body=a.copy();body[claimed]=0;result['BodyCostume']=Image.fromarray(body)
    composed=Image.new('RGBA',master.size)
    for part in result.values():composed.alpha_composite(part)
    actual=np.asarray(composed);visible=a[:,:,3]>0
    if not np.array_equal(actual[:,:,3],a[:,:,3])or not np.array_equal(actual[visible],a[visible]):raise ValueError('Visible pixel partition changed the master')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--masters',type=Path,required=True);p.add_argument('--seeds',type=Path,required=True,help='JSON: roles plus corrections [{index, masks:{role:relativePNG}}]');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--config',default='configs/sam2.1/sam2.1_hiera_t.yaml');p.add_argument('--model-revision',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve existing results; choose a new output folder')
    files=sorted(a.masters.glob('*.png'))
    if not files or [f.stem for f in files]!=[f'{i:03d}'for i in range(len(files))]:raise ValueError('Expected contiguous canonical000.png sequence')
    seed=json.loads(a.seeds.read_text());roles=seed['roles'];masters=[Image.open(f)for f in files]
    if any(im.mode!='RGBA'for im in masters):raise ValueError('Canonical masters must be RGBA')
    if any(im.size!=masters[0].size for im in masters):raise ValueError('Canvas changed across frames')
    if not roles or len(set(roles))!=len(roles)or set(roles)-ROLES:raise ValueError('Invalid tracked roles')
    corrections={};used_roles=set();evidence=[]
    for correction in seed['corrections']:
        i=correction['index']
        if isinstance(i,bool)or not isinstance(i,int)or not 0<=i<len(files)or i in corrections:raise ValueError('Invalid or duplicate seed index')
        masks={}
        for role,relative in correction['masks'].items():
            if role not in roles:raise ValueError('Unknown correction role')
            path=(a.seeds.parent/relative).resolve();im=Image.open(path)
            if im.size!=masters[i].size:raise ValueError('Seed mask canvas mismatch')
            mask=np.asarray(im.getchannel('A')if im.mode=='RGBA'else im.convert('L'))>0
            if not mask.any():raise ValueError('Empty correction mask')
            masks[role]=mask;used_roles.add(role);evidence.append({'index':i,'role':role,'sha256':sha(path)})
        # Run overlap and shape validation before initializing an expensive model.
        partition_visible(masters[i],np.full((len(roles),masters[i].height,masters[i].width),-1.),roles,masks)
        corrections[i]=masks
    if used_roles!=set(roles)or set(corrections.get(0,{}))!=set(roles):raise ValueError('Every tracked role needs a visible seed at frame0')
    import torch
    from sam2.build_sam import build_sam2_video_predictor
    torch.set_num_threads(4)
    predictor=build_sam2_video_predictor(a.config,str(a.checkpoint),device='cpu',apply_postprocessing=False)
    a.output.mkdir(parents=True)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='visible-cutouts-')as tmp,torch.inference_mode():
        video=Path(tmp)
        for i,im in enumerate(masters):
            bg=Image.new('RGBA',im.size,'#e8e8e8');bg.alpha_composite(im);bg.convert('RGB').save(video/f'{i:05d}.jpg',quality=98)
        state=predictor.init_state(video_path=str(video),offload_video_to_cpu=True,offload_state_to_cpu=True)
        for i,masks in sorted(corrections.items()):
            for role,mask in masks.items():predictor.add_new_mask(state,frame_idx=i,obj_id=roles.index(role)+1,mask=mask)
        for i,ids,logits in predictor.propagate_in_video(state,start_frame_idx=0):
            scores=logits[:,0].cpu().numpy();order=[ids.index(j+1)for j in range(len(roles))]
            parts=partition_visible(masters[i],scores[order],roles,corrections.get(i))
            for role,im in parts.items():
                folder=a.output/role;folder.mkdir(exist_ok=True);im.save(folder/f'{i:03d}.png')
            rows.append({'index':i,'master_sha256':sha(files[i]),'visible_pixels':{r:int(np.count_nonzero(np.asarray(im)[:,:,3]))for r,im in parts.items()}})
            print(json.dumps({'frame':i,'frames':len(files)}),flush=True)
    if {r['index']for r in rows}!=set(range(len(files))):raise ValueError('Incomplete temporal proposal')
    receipt={'status':'TEMPORAL_VISIBLE_CUTOUT_PROPOSAL_REQUIRES_SEMANTIC_REVIEW','model_repository':'https://github.com/facebookresearch/sam2','model_revision':a.model_revision,'checkpoint_sha256':sha(a.checkpoint),'config':a.config,'device':'cpu','seed_manifest_sha256':sha(a.seeds),'correction_masks':evidence,'frames':rows,'master_pixel_changes':0,'pixel_translation':False,'hidden_surfaces_authored':False,'weapon_separated':'Weapon'in roles,'anatomy_registration_approved':False,'owner_approved':False,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
