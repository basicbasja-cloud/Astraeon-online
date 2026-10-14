"""Static proportion review only. Never normalize animation keys independently."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(image):
    ys,xs=np.nonzero(np.array(image.convert('RGBA'))[:,:,3]>=128)
    if not len(xs):
        raise ValueError('Missing visible image: unknown, not a proportion pass')
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]


def transform(m,p):
    return [m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]


case=json.loads((P/'observations.json').read_text())
rows=[]
board=Image.new('RGB',(1320,790),'#1d2935')
draw=ImageDraw.Draw(board)
draw.text((20,16),'Proportion review / same full-character height / unchanged source images',font=font,fill='white')
draw.text((20,47),'Original concept: conversation-only visual reference. No exact concept-pixel score or matched-camera claim.',font=small,fill='#ffd082')
for i,record in enumerate(case['candidates']):
    paths={key:ROOT/value['path'] for key,value in record['images'].items()}
    assert all(sha(paths[key])==value['sha256'] for key,value in record['images'].items())
    image=Image.open(paths['full']).convert('RGBA')
    fullbox=bbox(image)
    headbox=bbox(Image.open(paths['head']))
    height=fullbox[3]-fullbox[1]
    jaw=transform(record['head_matrix'],case['visible_jaw_tip_native'])
    headheight=jaw[1]-headbox[1]
    row=dict(name=record['name'],full_alpha128_bbox=fullbox,head_alpha128_bbox=headbox,
             total_visible_height_px=height,visible_crown_to_jaw_px=headheight,
             crown_to_jaw_fraction=headheight/height,heads_per_height=height/headheight,
             projected_head_width_px=headbox[2]-headbox[0],
             head_width_per_height=(headbox[2]-headbox[0])/height,
             jaw_definition='Manually reviewed visible chin tip in head texture; not inferred head/neck bone',
             jaw_uncertainty_display_px=2,
             approved_against_concept=False)
    if 'visible_pauldron_span_xy' in record:
        a,b=record['visible_pauldron_span_xy']
        span=abs(b[0]-a[0])
        row.update(projected_pauldron_span_px=span,head_width_per_projected_pauldron_span=(headbox[2]-headbox[0])/span,
                   pauldron_scope='Manual outer visible armor edges; perspective-dependent, not anatomical shoulder breadth',
                   crown_to_belt_fraction=(record['belt_center_y']-headbox[1])/height,
                   near_boot_top_to_sole_fraction=(fullbox[3]-record['near_boot_top_y'])/height)
    rows.append(row)
    crop=image.crop(fullbox)
    scale=430/height
    size=(round(crop.width*scale),430)
    crop=crop.resize(size,Image.Resampling.LANCZOS)
    x=i*660+(660-size[0])//2
    y=118
    draw.text((i*660+24,85),record['name'],font=font,fill='white')
    for yy,label,color in [(y,'Crown','#90caff'),(y+430,'Sole','#90caff'),(y+(jaw[1]-fullbox[1])*scale,'Jaw','#ffcf76')]:
        draw.line((i*660+24,round(yy),i*660+636,round(yy)),fill=color,width=1)
        draw.text((i*660+28,round(yy)+3),label,font=small,fill=color)
    board.paste(crop,(x,y),crop)
    if 'visible_pauldron_span_xy' in record:
        endpoints=[(x+(p[0]-fullbox[0])*scale,y+(p[1]-fullbox[1])*scale) for p in record['visible_pauldron_span_xy']]
        draw.line(endpoints,fill='#76ffcf',width=2)
        for px,py in endpoints:
            draw.ellipse((px-3,py-3,px+3,py+3),fill='#76ffcf')
        draw.text((i*660+28,round(endpoints[0][1])+6),'Visible armor edges (manual)',font=small,fill='#76ffcf')
    lines=[f'Actual visible height: {height}px',
           f'Crown to visible jaw: {headheight:.1f}px / {headheight/height*100:.1f}% of height',
           f'Projected head width: {headbox[2]-headbox[0]}px / {(headbox[2]-headbox[0])/height*100:.1f}% of height']
    if 'projected_pauldron_span_px' in row:
        lines.append(f'Visible armor span: {span}px / head width is {(headbox[2]-headbox[0])/span:.2f}x span')
    else:
        lines.append('Body is a different painted pose/view; armor-span comparison unknown')
    lines.append('Static review scaling only; no root fitting or source-art edit')
    for k,line in enumerate(lines):
        draw.text((i*660+24,590+k*26),line,font=small,fill='#d5dfeb')
report=dict(schema='static-proportion-review-v1',candidates=rows,
            exact_concept_pixel_comparison=False,matched_camera_reference_available=False,
            decision='NOT_LOCKED_CONCEPT_COMPARISON_REQUIRES_MATCHED_NEUTRAL_REFERENCE',
            reason='Head height is visually close; hairstyle width and shoulder projection still differ. Attachment PASS is not proportion approval.',
            concept_observation=case['concept_observation'],
            manual_landmarks_are_not_anatomical_detection=True,
            animation_keys_modified=False,production_pass=False)
(P/'proportion-report.json').write_text(json.dumps(report,indent=2)+'\n')
board.save(P/'proportion-review.png')
print(json.dumps(rows,indent=2))
