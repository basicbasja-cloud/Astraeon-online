"""Recheck source depth, actual redraw bytes and the user's exact W approval."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
r=Path('research/sprite-animation/profile-depth-v12');checker='skills/modular-eight-direction-sprites/scripts/leg-continuity.py'
cards=[Image.new('RGB',(1024,280),'#272727') for _ in range(4)];board=Image.new('RGB',(2048,560),'#272727');results=[];formats=[]
for index,v in enumerate(['E','W']):
    dr=r/'master'/v;subprocess.run(['python',checker,'check','--case',str(dr/'leg-annotations.json'),'--out',str(dr/'check'),'--html',str(dr/'leg-review.html')],check=True)
    report=json.loads((dr/'check/continuity-report.json').read_text());assert report['status']==('USER_ACCEPTED_LEG_READABILITY' if v=='W' else 'REVIEW_REQUIRED')
    frames=[Image.open(dr/'frames'/f'{k:02}.png').convert('RGBA') for k in range(4)]
    for k,im in enumerate(frames):
        for column,file in enumerate([r/'source-depth'/v/f'{k:02}/proximal-guide.png',dr/'frames'/f'{k:02}.png']):
            f=Image.open(file).convert('RGBA');bg=Image.new('RGBA',f.size,'#272727');bg.alpha_composite(f);small=bg.resize((256,256)).convert('RGB')
            cards[k].paste(small,(index*512+column*256,24));board.paste(small,(k*512+column*256,index*280+24))
        text=v+' / '+report['status'];ImageDraw.Draw(cards[k]).text((index*512+8,5),text,fill='white');ImageDraw.Draw(board).text((k*512+8,index*280+5),v+f' pose {k+1}: source pelvis / art',fill='white')
    for suffix,ms in [('png',1333),('webp',1333),('gif',1330)]:
        im=Image.open(dr/('walk-quality.'+suffix));assert im.n_frames==4 and im.size==(512,512);durations=[];hashes=[]
        for k in range(4):
            im.seek(k);arr=np.array(im.convert('RGBA'));im.load();durations.append(im.info['duration']);hashes.append(hashlib.sha256(arr.tobytes()).hexdigest())
            if suffix!='gif':
                src=np.array(frames[k]);valid=src[:,:,3]>0;assert np.array_equal(src[:,:,3],arr[:,:,3]);assert np.array_equal(src[:,:,:3][valid],arr[:,:,:3][valid])
        assert len(set(hashes))==4 and abs(sum(durations)-ms)<.01
        formats.append({'view':v,'format':suffix,'frames':4,'duration_ms':sum(durations),'visible_RGBA_exact':suffix!='gif'})
    results.append({'view':v,'status':report['status'],'measurement_status':report['image_review']['status'],'coordinate_status':report['coordinate_status'],
        'approved_hidden_joint_coordinates':False,'user_acceptance':report['image_review']['user_acceptance'],'release_ready':False})
palette_strip=Image.new('RGB',(4096,280))
for k,c in enumerate(cards):palette_strip.paste(c,(k*1024,0))
palette=palette_strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);gif=[c.quantize(palette=palette,dither=Image.Dither.NONE) for c in cards]
gif[0].save(r/'profile-review.gif',save_all=True,append_images=gif[1:],duration=[330,340,330,330],loop=0,optimize=False,disposal=2)
board.save(r/'profile-source-art-comparison.png')
depth=json.loads((r/'source-depth/depth-index.json').read_text());assert len(depth['records'])==8 and all(p['isolated_depth_order_mismatch_pixels']==0 for p in depth['records'])
old=json.loads(Path('research/sprite-animation/eight-direction-v11/master/E/check/continuity-report.json').read_text());assert old['status']=='REJECTED'
assert old['image_review']['frames'][2]['crossings'][0]['result']!='reviewed_match'
failure=json.loads((r/'evidence/E-from-approved-W-failed/failure.json').read_text());assert failure['status']=='REJECTED' and not failure['complete_four_frame_package']
(r/'review-summary.json').write_text(json.dumps({'schema':'profile-depth-review-v1','views':results,'source_poses':8,'source_render_passes':40,
    'source_metric_depth_overlap_pixels':sum(p['overlap_depth_pixels'] for p in depth['records']),'source_depth_order_mismatch_pixels':0,
    'hip_depth_difference_scene_units_range':[min(p['hip_depth_difference_scene_units'] for p in depth['records']),max(p['hip_depth_difference_scene_units'] for p in depth['records'])],
    'prior_E_correction_user_rejection_preserved':True,'prior_local_identity_conclusion_withdrawn':True,'new_wrong_facing_and_clipped_generation_rejected':True,
    'source_geometry_is_not_generated_image_depth':True,'formats':formats,'automatic_semantic_detector':False,'complete_replaceable_painted_parts':False,'release_ready':False},indent=2)+'\n')
print('PROFILE_REVIEW W user accepted; E pending; old E rejected; source depth verified; all production gates blocked')
