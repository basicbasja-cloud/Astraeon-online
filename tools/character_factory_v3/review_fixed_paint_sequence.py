"""Review canonical painted frames against their pinned source capture.

No position, scale or anatomy corrections are applied. Socket-to-alpha distance
is a diagnostic only: a sleeve covering a wrist does not prove a correct grip.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from source_capture_identity import verify_source_reference


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shared_palette_gif(images,path,duration):
    """Quantize all frames against one palette to avoid palette flicker."""
    if not images or any(im.size!=images[0].size for im in images):raise ValueError('GIF frames differ or are empty')
    columns=math.ceil(math.sqrt(len(images)));rows=math.ceil(len(images)/columns)
    width,height=images[0].size
    sheet=Image.new('RGB',(columns*width,rows*height),'#e5e5e5')
    for i,image in enumerate(images):sheet.paste(image.convert('RGB'),((i%columns)*width,(i//columns)*height))
    palette=sheet.quantize(colors=255)
    frames=[im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)for im in images]
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=2,optimize=False)


def alpha_distances(image, sockets):
    alpha=np.asarray(image.getchannel('A'))>16
    if not alpha.any():raise ValueError('Empty painted pose')
    distance=distance_transform_edt(~alpha)
    result={}
    for name,value in sockets.items():
        point=np.asarray(value,dtype=float)
        if point.shape!=(2,) or not np.isfinite(point).all():raise ValueError('Invalid socket '+name)
        x,y=np.rint(point).astype(int)
        if not 0<=x<image.width or not 0<=y<image.height:raise ValueError('Socket outside canonical canvas')
        result[name]=float(distance[y,x])
    return result


def review(guide,recipe_path,frames_folder,output,duration_ms=80):
    if output.exists():raise ValueError('Preserve existing reviews; choose a fresh output')
    if type(duration_ms)is not int or duration_ms<10 or duration_ms%10:raise ValueError('Use positive GIF timing in whole 10ms units')
    recipe=json.loads(recipe_path.read_text());manifest_path=guide/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    if recipe.get('frame_space')!='canonical-authoring':raise ValueError('Only direct canonical-frame recipes are accepted')
    source_verification=verify_source_reference(recipe_path,guide)
    direction=recipe['direction'];indices=recipe['source_pose_indices']
    if not indices or len(indices)!=len(set(indices)):raise ValueError('Invalid pose map')
    count=manifest['frame_count']
    if len(recipe['all_source_frame_inputs'])!=count:raise ValueError('Incomplete source hash inventory')
    expected={i:sha(guide/direction/f'{i:03d}.png')for i in range(count)}
    if source_verification['mode']=='EXACT_DECLARED_REFERENCE_BYTES' and {r['index']:r['sha256']for r in recipe['all_source_frame_inputs']}!=expected:raise ValueError('Source images changed')
    canvas=tuple(recipe['source_size']);native=manifest['job']['resolution']
    if canvas[0]!=canvas[1] or native%canvas[0]:raise ValueError('Incompatible source canvas')
    factor=native/canvas[0];records=[];comparisons=[];painted=[]
    colors={'head':'#3485eb','hand_r':'#df3636','hand_l':'#329e53','foot_r':'#ef9924','foot_l':'#be6be0','grip':'#df3636','tip':'#df3636'}
    for index in indices:
        if type(index)is not int or not 0<=index<count:raise ValueError('Unexpected source index')
        path=frames_folder/f'{index:03d}.png'
        with Image.open(path)as opened:
            if opened.mode!='RGBA' or opened.size!=canvas:raise ValueError('Paint must be full canonical RGBA')
            art=opened.copy()
        source=Image.open(guide/direction/f'{index:03d}.png').convert('RGBA').resize(canvas,Image.Resampling.LANCZOS)
        record=manifest['views'][direction]['frames'][index]
        sockets={k:[v/factor for v in xy]for k,xy in record['landmarks'].items()if k in colors}
        sockets.update({k:[v/factor for v in xy]for k,xy in record.get('weapon_guide',{}).items()if k in ['grip','tip']})
        distances=alpha_distances(art,sockets)
        rows=[]
        for image in [source,art]:
            image=image.copy();draw=ImageDraw.Draw(image)
            for name,(x,y)in sockets.items():
                draw.ellipse((x-3,y-3,x+3,y+3),fill=colors[name],outline='white',width=1)
            if 'grip'in sockets and'tip'in sockets:draw.line([tuple(sockets['grip']),tuple(sockets['tip'])],fill='#df3636',width=1)
            rows.append(image.resize((384,384),Image.Resampling.LANCZOS))
        panel=Image.new('RGB',(768,418),'#e5e5e5');draw=ImageDraw.Draw(panel)
        draw.text((10,10),f'SOURCE {index} | PAINT + SOURCE SOCKETS | DRAFT',fill='black')
        for x,image in zip([0,384],rows):panel.paste(image,(x,30),image)
        comparisons.append(panel)
        bg=Image.new('RGBA',(240,240),'#e5e5e5');bg.alpha_composite(art.resize(bg.size,Image.Resampling.LANCZOS));painted.append(bg.convert('RGB'))
        records.append({'index':index,'source_action':record['action'],'source_frame':record['source_frame'],
                        'paint_sha256':sha(path),'source_png_sha256':expected[index],
                        'source_socket_to_nearest_painted_alpha_author_px':distances,
                        'sockets_requiring_manual_fit_review':[name for name,d in distances.items()if d>3.2]})
    output.mkdir(parents=True)
    for name,images,duration in [('normal.gif',painted,duration_ms),('slow.gif',painted,duration_ms*3),('source-vs-paint-slow.gif',comparisons,duration_ms*3)]:
        shared_palette_gif(images,output/name,duration)
    comparisons[0].save(output/'first-source-overlay.png')
    report={'status':'DIAGNOSTIC_REVIEW_NOT_VISUAL_APPROVAL','direction':direction,'indices':indices,'source_capture_verification':source_verification,
            'full_source_timeline':indices==list(range(count)),'recipe_sha256':sha(recipe_path),
            'guide_manifest_sha256':sha(manifest_path),'implementation_sha256':sha(Path(__file__)),
            'preview_timing_ms':duration_ms,'preview_timing_is_not_runtime_event_authority':True,
            'one_shared_gif_palette':True,
            'source_socket_alpha_coverage_is_not_anatomy_or_grip_acceptance':True,
            'per_frame_fitting':False,'runtime_admitted':False,'frames':records}
    (output/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['guide','recipe','frames','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--duration-ms',type=int,default=80);a=p.parse_args()
    r=review(a.guide,a.recipe,a.frames,a.output,a.duration_ms)
    print(json.dumps({'frames':len(r['frames']),'full_source_timeline':r['full_source_timeline'],'runtime_admitted':False}))
