"""Transfer visible-part ownership to canonical master pixels and review sheets.

Masks share one explicit viewport; pixels come from the canonical master once.
No independent part resampling, anatomy fitting, hidden-surface authoring or
runtime admission occurs. A complete semantic review remains mandatory.
"""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from track_visible_cutouts import partition_visible,pin_inputs,verify_inputs
from build_fixed_grid_sequence_review import gif

def transfer_ownership(master,masks,viewport):
    x,y,w,h=viewport
    if any(isinstance(v,bool)or not isinstance(v,int)for v in viewport)or x<0 or y<0 or w<1 or h<1 or x+w>master.width or y+h>master.height:raise ValueError('Invalid shared viewport')
    roles=list(masks)
    if not roles or len({im.size for im in masks.values()})!=1:raise ValueError('Mask canvases differ')
    scores=[];reserved=np.zeros((master.height,master.width),bool)
    for role,im in masks.items():
        alpha=im.getchannel('A')if im.mode=='RGBA'else im.convert('L');mask=Image.new('L',master.size);mask.paste(alpha.resize((w,h),Image.Resampling.NEAREST),(x,y));selected=np.asarray(mask)>0
        if np.any(selected&reserved):raise ValueError('Overlapping visible ownership masks')
        reserved|=selected;scores.append(np.where(selected,1.,-1.))
    return partition_visible(master,np.stack(scores),roles)

def retain_weapon_underlay(parts,donor):
    if donor.size!=parts['BodyCostume'].size:raise ValueError('Underlay canvas mismatch')
    body=np.array(parts['BodyCostume']);pixels=np.array(donor);opaque=np.array(parts['Weapon'])[:,:,3]==255;selected=opaque&(pixels[:,:,3]>0)
    body[selected]=pixels[selected];result=dict(parts);result['BodyCostume']=Image.fromarray(body)
    return result,int(selected.sum())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--masters',type=Path,required=True);p.add_argument('--detail-masters',type=Path,required=True);p.add_argument('--masks',type=Path,required=True);p.add_argument('--viewport',nargs=4,type=int,required=True,metavar=('X','Y','W','H'));p.add_argument('--timing',type=Path,required=True);p.add_argument('--hidden-body-manifest',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous review; use a new output')
    files=sorted(a.masters.glob('*.png'));detail=sorted(a.detail_masters.glob('*.png'));receipt_path=a.masks/'receipt.json';receipt=json.loads(receipt_path.read_text());records={r['index']:r for r in receipt['frames']}
    if not files or len(files)!=len(detail)or [f.stem for f in files]!=[f'{i:03d}'for i in range(len(files))]or [f.stem for f in detail]!=[f.stem for f in files]:raise ValueError('Master timeline mismatch')
    if set(records)!=set(range(len(files))):raise ValueError('Tracking timeline mismatch')
    role_paths={r:sorted((a.masks/r).glob('*.png'))for r in ['HeadHair','Weapon']}
    if any([f.stem for f in paths]!=[f.stem for f in files]for paths in role_paths.values()):raise ValueError('Missing tracked role frames')
    donors={}
    if a.hidden_body_manifest:
        data=json.loads(a.hidden_body_manifest.read_text())
        for key,value in data['frames'].items():
            if not key.isdigit()or not 0<=int(key)<len(files):raise ValueError('Invalid underlay frame')
            donors[int(key)]=(a.hidden_body_manifest.parent/value).resolve()
    pinned=pin_inputs(files+detail+[receipt_path,a.timing]+[f for paths in role_paths.values()for f in paths]+list(donors.values())+([a.hidden_body_manifest]if a.hidden_body_manifest else []));timing=json.loads(a.timing.read_text());durations=timing['durations_ms']
    if len(durations)!=len(files)or any(isinstance(d,bool)or not isinstance(d,int)or d<=0 for d in durations):raise ValueError('Invalid review timing')
    for i,f in enumerate(detail):
        if hashlib.sha256(f.read_bytes()).hexdigest()!=records[i]['master_sha256']:raise ValueError('Tracked mask belongs to stale painted source')
    a.output.mkdir(parents=True);rows=[];reviews=[];masters=[];roles=['HeadHair','BodyCostume','Weapon'];sheets={};size=None;cols=4;sheet_rows=math.ceil(len(files)/cols)
    for i,f in enumerate(files):
        master=Image.open(f).convert('RGBA')
        if size is None:size=master.size;sheets={r:Image.new('RGBA',(size[0]*cols,size[1]*sheet_rows))for r in roles}
        if master.size!=size:raise ValueError('Canonical canvas changed')
        masks={r:Image.open(paths[i])for r,paths in role_paths.items()};parts=transfer_ownership(master,masks,a.viewport);hidden_count=0;combined=Image.new('RGBA',size)
        if i in donors:
            donor=Image.open(donors[i]).convert('RGBA')
            if donor.size!=next(iter(masks.values())).size:raise ValueError('Detail underlay canvas mismatch')
            x,y,w,h=a.viewport;canonical=Image.new('RGBA',size);canonical.paste(donor.convert('RGBa').resize((w,h),Image.Resampling.BICUBIC).convert('RGBA'),(x,y));parts,hidden_count=retain_weapon_underlay(parts,canonical)
        for r in roles:
            part=parts[r];folder=a.output/r;folder.mkdir(exist_ok=True);part.save(folder/f'{i:03d}.png');sheets[r].paste(part,((i%cols)*size[0],(i//cols)*size[1]));combined.alpha_composite(part)
        x,y,w,h=a.viewport;review=Image.new('RGBA',(1536,416),'#e8e8e8');draw=ImageDraw.Draw(review)
        for j,r in enumerate(roles+['Assembly']):
            im=combined if r=='Assembly'else parts[r];review.alpha_composite(im.crop((x,y,x+w,y+h)).resize((384,384),Image.Resampling.LANCZOS),(j*384,32));draw.text((j*384+10,8),r,fill='black')
        original=np.array(master);actual=np.array(combined);visible=(original[:,:,3]>0)|(actual[:,:,3]>0)
        if not np.array_equal(actual[:,:,3],original[:,:,3])or not np.array_equal(actual[visible],original[visible]):raise ValueError('Canonical assembly changed master pixels')
        reviews.append(review);masters.append(combined.convert('RGBa').resize((240,240),Image.Resampling.LANCZOS).convert('RGBA'));rows.append({'index':i,'canonical_master_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sheet_rect':[(i%cols)*size[0],(i//cols)*size[1],*size],'part_visible_pixels':{r:int(np.count_nonzero(np.array(parts[r])[:,:,3]))for r in roles},'retained_hidden_body_pixels':hidden_count,'recomposition_changed_pixels':0})
    for r,sheet in sheets.items():sheet.save(a.output/f'{r}-sheet.png')
    gif(reviews,a.output/'layers-normal.gif',durations);gif(reviews,a.output/'layers-slow.gif',[d*3 for d in durations]);gif(masters,a.output/'assembled-game-scale.gif',durations);reviews[8 if len(reviews)>8 else 0].save(a.output/'layers-contact.png')
    verify_inputs(pinned)
    report={'status':'VISIBLE_CUTOUT_SHEETS_REQUIRE_SEMANTIC_AND_CONTINUITY_REVIEW','canvas':size,'shared_mask_viewport':a.viewport,'roles':roles,'columns':cols,'rows':sheet_rows,'frames':rows,'source_tracking_receipt_sha256':pinned[str(receipt_path.resolve())],'master_pixel_changes':0,'part_pixel_resampling':False,'figure_fitting':False,'hidden_surfaces_complete':False,'review_timing_only':True,'owner_approved':False,'runtime_admitted':False}
    (a.output/'sheet-map.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'frames':len(files),'roles':roles,'master_pixel_changes':0}))
if __name__=='__main__':main()
