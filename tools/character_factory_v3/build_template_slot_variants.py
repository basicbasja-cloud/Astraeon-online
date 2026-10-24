"""Assemble actual head/costume alternatives against same-pose cutout templates.

No pose fitting or body warping. Protected weapons and visible gloves reuse the
same pixels. New costume art is intersected with the recorded body template;
missing interior coverage is reported and never silently filled.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion
from review_fixed_paint_sequence import shared_palette_gif
from track_visible_cutouts import pin_inputs,verify_inputs,sha


def template_costume(template,new_master):
    if template.mode!='RGBA' or new_master.mode!='RGBA' or template.size!=new_master.size:raise ValueError('Same canonical RGBA canvas required')
    a=np.array(template);b=np.array(new_master);inside=a[:,:,3]>0
    result=b.copy();result[:,:,3]=np.minimum(a[:,:,3],b[:,:,3]);result[result[:,:,3]==0]=0
    missing=inside&(b[:,:,3]==0);interior=binary_erosion(inside,iterations=3)
    return Image.fromarray(result),{'template_pixels_without_new_paint':int(missing.sum()),'uncovered_interior_pixels':int((missing&interior).sum()),'body_pixel_positions_changed':False}


def build(masters,parts,new_heads,costume_masters,fx,recipe_path,output):
    if output.exists():raise ValueError('Choose a fresh bundle destination')
    recipe=json.loads(recipe_path.read_text());indices=recipe['source_pose_indices'];roles=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']
    if indices!=list(range(len(indices))):raise ValueError('Use one complete ordered timeline')
    files=[Path(__file__),recipe_path]+[p for i in indices for p in [masters/f'{i:03d}.png',new_heads/f'{i:03d}.png',costume_masters/f'{i:03d}.png',*[parts/r/f'{i:03d}.png'for r in roles],*[fx/r/f'{i:03d}.png'for r in ['WeaponLightBack','WeaponLightFront']]]]
    pinned=pin_inputs(files);output.mkdir(parents=True);previews=[];runtime=[];rows=[];sheets={};size=None
    names=['Original','Head only','Costume only','Head + costume'];left,top,right,bottom=recipe['viewport'];w,h=right-left,bottom-top
    for i in indices:
        base={r:Image.open(parts/r/f'{i:03d}.png').convert('RGBA')for r in roles};master=Image.open(masters/f'{i:03d}.png').convert('RGBA')
        if size is None:size=master.size;sheets={r:Image.new('RGBA',(size[0]*4,size[1]*((len(indices)+3)//4)))for r in ['HeadHair','BodyCostume']}
        if master.size!=size or any(im.size!=size for im in base.values()):raise ValueError('Canonical canvas changed')
        merged=Image.new('RGBA',size)
        for r in roles:merged.alpha_composite(base[r])
        if merged.tobytes()!=master.tobytes():raise ValueError('Original visible parts do not reconstruct the master')
        head=Image.open(new_heads/f'{i:03d}.png').convert('RGBA');costume,coverage=template_costume(base['BodyCostume'],Image.open(costume_masters/f'{i:03d}.png').convert('RGBA'))
        if head.size!=size:raise ValueError('Head slot canvas differs')
        for role,im in [('HeadHair',head),('BodyCostume',costume)]:
            folder=output/role;folder.mkdir(exist_ok=True);im.save(folder/f'{i:03d}.png');sheets[role].paste(im,((i%4)*size[0],(i//4)*size[1]))
        back=Image.open(fx/'WeaponLightBack'/f'{i:03d}.png');front=Image.open(fx/'WeaponLightFront'/f'{i:03d}.png')
        panel=Image.new('RGB',(w*4,h+32),'#e5e5e5');small=Image.new('RGB',(960,272),'#e5e5e5');draw=ImageDraw.Draw(panel)
        for column,(body,chosen_head)in enumerate([(base['BodyCostume'],base['HeadHair']),(base['BodyCostume'],head),(costume,base['HeadHair']),(costume,head)]):
            image=Image.new('RGBA',size)
            for layer in [back,body,front,chosen_head,base['Weapon'],base['WeaponHandOccluder']]:image.alpha_composite(layer)
            crop=image.crop((left,top,right,bottom));panel.paste(crop,(column*w,32),crop);draw.text((column*w+8,8),names[column],fill='black')
            game=image.resize((240,240),Image.Resampling.LANCZOS);small.paste(game,(column*240,32),game);ImageDraw.Draw(small).text((column*240+8,8),names[column],fill='black')
        previews.append(panel);runtime.append(small)
        rows.append({'index':i,**coverage,'weapon_reused_sha256':sha(parts/'Weapon'/f'{i:03d}.png'),'glove_occluder_reused_sha256':sha(parts/'WeaponHandOccluder'/f'{i:03d}.png'),'fx_front_reused_sha256':sha(fx/'WeaponLightFront'/f'{i:03d}.png'),'fx_back_reused_sha256':sha(fx/'WeaponLightBack'/f'{i:03d}.png'),'new_body_sha256':sha(output/'BodyCostume'/f'{i:03d}.png'),'new_head_sha256':sha(output/'HeadHair'/f'{i:03d}.png')})
    for role,sheet in sheets.items():sheet.save(output/(role+'-sheet.png'))
    shared_palette_gif(previews,output/'four-slot-combinations-normal.gif',80);shared_palette_gif(previews,output/'four-slot-combinations-slow.gif',240);shared_palette_gif(runtime,output/'game-scale-normal.gif',80)
    previews[5 if len(previews)>5 else 0].save(output/'cut-contact-with-trail.png');previews[0].save(output/'ready-contact.png')
    verify_inputs(pinned)
    result={'status':'SAME_POSE_SLOT_VARIANT_REVIEW_NOT_RELEASE','direction':recipe['direction'],'guide_job':recipe['guide_job'],'frames':rows,'input_hashes':pinned,
            'variants':names,'gloves_kept_by_design':True,'new_costume_is_drawn_design_not_hue_shift':True,'per_frame_pose_fitting':False,
            'camera_or_body_transform':False,'hidden_surfaces_complete':False,'four_direction_variant_complete':False,'runtime_admitted':False,
            'remaining_review':['neck and wrist seams','occlusion around raised free arm','clipped new costume silhouette','source-to-paint temporal registration']}
    (output/'variant-manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['masters','parts','new-heads','costume-masters','fx','recipe','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=build(a.masters,a.parts,a.new_heads,a.costume_masters,a.fx,a.recipe,a.output);print(json.dumps({'frames':len(r['frames']),'variants':r['variants'],'uncovered_interior_pixels':sum(f['uncovered_interior_pixels']for f in r['frames'])}))
