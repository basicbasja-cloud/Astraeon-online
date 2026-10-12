"""Assemble diagnostic eight-facing previews and re-run checks on current image bytes.

Never repairs anatomy, fits pose silhouettes, or invents artwork landmark labels.
Run from repository root after pack-quality and independent annotations.
"""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

root=Path('research/sprite-animation/eight-direction-v11')
views=['S','SE','E','NE','N','NW','W','SW']
checker='skills/modular-eight-direction-sprites/scripts/leg-continuity.py'
summary=[];cards=[Image.new('RGB',(1024,560),'#272727') for _ in range(4)]
comparisons=Image.new('RGB',(2048,8*280),'#272727');cd=ImageDraw.Draw(comparisons)
format_checks=[]
for index,v in enumerate(views):
    dr=root/'master'/v
    subprocess.run(['python',checker,'check','--case',str(dr/'leg-annotations.json'),'--out',str(dr/'check'),'--html',str(dr/'leg-review.html')],check=True)
    r=json.loads((dr/'check'/'continuity-report.json').read_text())
    crossings=[e for f in r['image_review']['frames'] for e in f['crossings']]
    summary.append({'view':v,'status':r['status'],'coordinate_status':r['coordinate_status'],
                    'image_status':r['image_review']['status'],
                    'required_visible_crossings':len(crossings),'reviewed_matches':sum(e['result']=='reviewed_match' for e in crossings),
                    'unresolved_crossings':sum(e['result']=='unresolved' for e in crossings),
                    'image_flags':r['image_review']['flags'],'release_ready':False})
    frames=[Image.open(dr/'frames'/f'{k:02}.png').convert('RGBA') for k in range(4)]
    for k,f in enumerate(frames):
        bg=Image.new('RGBA',f.size,'#272727');bg.alpha_composite(f)
        x,y=index%4*256,index//4*280
        cards[k].paste(bg.resize((256,256)).convert('RGB'),(x,y+24))
        ImageDraw.Draw(cards[k]).text((x+8,y+6),f'{v} / {r["status"]}',fill='#ece8df')
        for column,p in enumerate([root/'source-owners'/v/f'{k:02}'/'visible-color.png',dr/'frames'/f'{k:02}.png']):
            im=Image.open(p).convert('RGBA');b=Image.new('RGBA',im.size,'#272727');b.alpha_composite(im)
            comparisons.paste(b.resize((256,256)).convert('RGB'),(k*512+column*256,index*280+24))
        cd.text((k*512+8,index*280+5),f'{v} pose {k+1}: source owners / new art',fill='#ece8df')
    for suffix,expected_ms in [('png',1333),('webp',1333),('gif',1330)]:
        im=Image.open(dr/('walk-quality.'+suffix));delays=[];pixels=[]
        assert im.n_frames==4 and im.size==(512,512),(v,suffix,im.n_frames,im.size)
        for k in range(4):
            im.seek(k);pixels.append(np.array(im.convert('RGBA')))
            # Pillow loads animated WebP timestamps on load, not seek alone.
            im.load();delays.append(im.info['duration'])
            if suffix!='gif':
                src=np.array(frames[k]);visible=(src[:,:,3]>0)
                assert np.array_equal(src[:,:,3],pixels[-1][:,:,3]),(v,suffix,k,'alpha')
                assert np.array_equal(src[:,:,:3][visible],pixels[-1][:,:,:3][visible]),(v,suffix,k,'visible RGB')
        assert len({hashlib.sha256(p.tobytes()).hexdigest() for p in pixels})==4
        assert abs(sum(delays)-expected_ms)<.01,(v,suffix,delays)
        format_checks.append({'view':v,'format':suffix,'frames':4,'canvas':[512,512],'duration_ms':sum(delays),'four_unique_frames':True,'full_visible_rgba_exact':suffix!='gif'})
palette_strip=Image.new('RGB',(1024*4,560))
for k,c in enumerate(cards):palette_strip.paste(c,(k*1024,0))
palette=palette_strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
gif=[c.quantize(palette=palette,dither=Image.Dither.NONE) for c in cards]
gif[0].save(root/'eight-direction-review.gif',save_all=True,append_images=gif[1:],duration=[330,340,330,330],loop=0,disposal=2,optimize=False)
cards[0].save(root/'eight-direction-first-pose.png')
comparisons.save(root/'source-art-comparison.png')
subprocess.run(['python',checker,'check','--case',str(root/'evidence/rejected-SE/leg-annotations.json'),'--out',str(root/'evidence/rejected-SE/check'),'--html',str(root/'evidence/rejected-SE/leg-review.html')],check=True)
bad=json.loads((root/'evidence/rejected-SE/check/continuity-report.json').read_text())
assert bad['status']=='REJECTED','Known user rejection must survive checker improvements'
subprocess.run(['python',checker,'check','--case',str(root/'evidence/rejected-E-revision1/leg-annotations.json'),'--out',str(root/'evidence/rejected-E-revision1/check'),'--html',str(root/'evidence/rejected-E-revision1/leg-review.html')],check=True)
bad_e=json.loads((root/'evidence/rejected-E-revision1/check/continuity-report.json').read_text())
assert bad_e['status']=='REJECTED','The new user-confirmed E pose 3 must remain rejected after replacing its candidate'
aggregate={'schema':'eight-facing-image-review-v1','views':summary,'source_poses':32,'source_render_passes':96,
    'required_visible_crossings':sum(x['required_visible_crossings'] for x in summary),
    'reviewed_matches':sum(x['reviewed_matches'] for x in summary),'unresolved_crossings':sum(x['unresolved_crossings'] for x in summary),
    'known_user_rejected_SE_pose_2_still_rejected':True,'known_user_rejected_E_pose_3_still_rejected':True,'semantic_model_executed':False,
    'all_painted_joints_approved':False,'replaceable_painted_parts_complete':False,'release_ready':False,
    'format_checks':format_checks}
(root/'review-summary.json').write_text(json.dumps(aggregate,indent=2)+'\n')
print('EIGHT_REVIEW',aggregate['reviewed_matches'],'reviewed source-crossing matches;',aggregate['unresolved_crossings'],'unresolved; all release gates blocked')
