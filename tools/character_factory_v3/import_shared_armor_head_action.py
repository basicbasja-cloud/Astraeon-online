"""Assemble a covered-armor head variant, derive same-frame cuts, and import.

Source body art is reused without geometric transforms. The independently
painted head library is a cosmetic component, not a same-pose full repaint.
Imported does not mean visually approved or a complete playable character.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from patch001_factory import BASE,ROOT,read,status
from import_patch001_cutouts import import_job
from track_visible_cutouts import pin_inputs,verify_inputs

BASE_ORDER=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']
FULL_ORDER=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder']


def build(job_id,baseline_intake,review,source,effects,output):
    baseline_intake,review,source,effects,output=[p.resolve()for p in [baseline_intake,review,source,effects,output]]
    if output.exists():raise ValueError('Choose a new cosmetic intake directory')
    ledger=read(BASE/'ledger.json');job=ledger['paint_jobs'][job_id];intake=read(baseline_intake);receipt=read(review/'receipt.json')
    if job['guide_job']!=intake['guide_job'] or receipt['guide_job']!=job['guide_job']:raise ValueError('Cosmetic source pose family differs')
    records={(r['direction'],r['index']):r for r in receipt['frames']}
    expected={(d,i)for d in job['directions']for i in range(job['frame_count'])}
    if set(records)!=expected:raise ValueError('Incomplete cosmetic head action')
    inputs=[Path(__file__),baseline_intake,review/'receipt.json']
    for row in intake['frames']:
        d,i=row['direction'],row['index'];inputs += [review/d/r/f'{i:03d}.png'for r in ['HeadHair','CollarOwnershipPatch']]+[source/d/r/f'{i:03d}.png'for r in ['BodyCostume','Weapon','WeaponHandOccluder']]+[effects/d/r/f'{i:03d}.png'for r in ['WeaponLightBack','WeaponLightFront']]
    pins=pin_inputs(inputs);output.mkdir(parents=True);export=[];sheets={};overlap_pixels=0
    for row in intake['frames']:
        d,i=row['direction'],row['index'];parts={'BodyCostume':Image.open(source/d/'BodyCostume'/f'{i:03d}.png').convert('RGBA'),'HeadHair':Image.open(review/d/'HeadHair'/f'{i:03d}.png').convert('RGBA'),'Weapon':Image.open(source/d/'Weapon'/f'{i:03d}.png').convert('RGBA'),'WeaponHandOccluder':Image.open(source/d/'WeaponHandOccluder'/f'{i:03d}.png').convert('RGBA')}
        parts['BodyCostume'].alpha_composite(Image.open(review/d/'CollarOwnershipPatch'/f'{i:03d}.png').convert('RGBA'))
        master=Image.new('RGBA',(768,768));owner=np.zeros((768,768),np.uint8)
        coverage=np.zeros((768,768),np.uint8)
        for n,role in enumerate(BASE_ORDER,1):
            if parts[role].size!=master.size:raise ValueError('Cosmetic part canvas differs')
            master.alpha_composite(parts[role]);mask=np.array(parts[role].getchannel('A'))>0;owner[mask]=n;coverage+=mask
        overlap_pixels+=int((coverage>1).sum());pixels=np.array(master)
        cut={}
        for n,role in enumerate(BASE_ORDER,1):
            a=pixels.copy();a[owner!=n]=0;cut[role]=Image.fromarray(a)
        check=Image.new('RGBA',master.size)
        for role in BASE_ORDER:check.alpha_composite(cut[role])
        if check.tobytes()!=master.tobytes():raise ValueError('Same-frame cosmetic cutouts fail exact reconstruction')
        for role in ['WeaponLightBack','WeaponLightFront']:cut[role]=Image.open(effects/d/role/f'{i:03d}.png').convert('RGBA')
        paths={}
        for role,im in {'Master':master,**cut}.items():
            folder=output/d/role;folder.mkdir(parents=True,exist_ok=True);path=folder/f'{i:03d}.png';im.save(path);paths[role]=os.path.relpath(path,output)
            if role!='Master':
                if (d,role)not in sheets:sheets[d,role]=Image.new('RGBA',(3072,3072))
                sheets[d,role].alpha_composite(im,((i%4)*768,(i//4)*768))
        export.append({**row,'master':paths.pop('Master'),'parts':paths,'base_draw_order':BASE_ORDER,'layer_draw_order':FULL_ORDER})
    for (d,role),im in sheets.items():im.save(output/d/(role+'-sheet.png'))
    manifest={'guide_job':job['guide_job'],'fit_id':job['fit_id'],'frames':export,'provenance':{'method':'Shared covered armor, observed original painted head placement and independently authored rigid cosmetic head-angle library; full master assembled first, then exact visible cuts.','head_review_receipt':str((review/'receipt.json').relative_to(ROOT)),'body_pose_or_pixels_warped':False,'same_pose_full_repaint_claimed':False,'independent_head_cosmetic':True,'hidden_surfaces_authored':False},'hidden_surfaces_authored':False,'owner_approved':False,'runtime_admitted':False}
    manifest_path=output/'import-manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');verify_inputs(pins)
    import_job(job_id,manifest_path.resolve())
    proof={'status':'COSMETIC_ACTION_IMPORTED_REQUIRES_SEMANTIC_REVIEW','paint_job':job_id,'poses':len(export),'separated_sheets':len(sheets),'authoring_overlap_pixels_resolved_in_visible_cuts':overlap_pixels,'recomposition_changed_pixels':0,'source_pins':pins,'body_warped':False,'full_character_complete':False,'owner_approved':False,'runtime_admitted':False}
    (output/'assembly-proof.json').write_text(json.dumps(proof,indent=2)+'\n');status(ledger);return {k:v for k,v in proof.items()if k!='source_pins'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paint-job',required=True)
    for name in ['baseline-intake','review','source','effects','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.paint_job,a.baseline_intake,a.review,a.source,a.effects,a.output)))
