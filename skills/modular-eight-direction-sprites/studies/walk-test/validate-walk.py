"""Decode review artifacts and verify source/mesh/part receipts; never approve art."""
import argparse,hashlib,json,re
from pathlib import Path
import numpy as np
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);a=p.parse_args();r=a.package
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'motion.json').read_text());q=json.loads((r/'saved-rig-check.json').read_text())
pkg=json.loads((r/'rig-preview/package.json').read_text())
assert q['blend_sha256']==sha(r/'original-modular-walk.blend')
assert m['capture_sha256']==sha(Path('research/sprite-animation/preset-retarget-v8/source-transforms.json.gz'))
assert q['source_samples_replayed']==41 and q['gate_floor_clearance'] and not q['floor_contact_verified']
receipts={}
for name,total in [('body-render-receipt.json',64),('part-render-receipt.json',104)]:
    receipt=json.loads((r/name).read_text())
    assert receipt['blend_sha256']==q['blend_sha256'] and receipt['rendered']==total
    receipts[name]=total
motions={}
for path in sorted(r.rglob('*')):
    if path.suffix=='.gif' or path.name in ['walk-SE.png','walk-painted-SE.png']:
        im=Image.open(path);times=[];pixels=[]
        for i in range(im.n_frames):
            im.seek(i);times.append(im.info['duration']);pixels.append(hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
        assert im.n_frames==8,(path,im.n_frames)
        assert sum(times)==(1330 if path.suffix=='.gif' else 1333),(path,times)
        assert len(set(pixels))==8,(path,'duplicate composed exposures')
        motions[str(path.relative_to(r))]={'decoded_frames':8,'decoded_delays_ms':times,'cycle_ms':sum(times),'unique_decoded_images':8}
for view in pkg['views']:
    files=list((r/'rig-preview/frames'/view).glob('*.png'))
    assert len(files)==8 and len({sha(path) for path in files})==8
    for path in files:assert Image.open(path).size==(128,128)
assert len(pkg['slots'])==13
for slot in pkg['slots']:
    dr=r/'rig-preview/parts/SE'/slot;assert len(list(dr.glob('*.png')))==16
    for k in range(8):assert Image.open(dr/f'{k:02}.png').size==Image.open(dr/f'{k:02}-depth.png').size==(128,128)
hair_changes=[]
for k in range(8):
    silver=np.array(Image.open(r/f'rig-preview/layer-preview/silver-{k:02}.png'))
    auburn=np.array(Image.open(r/f'rig-preview/layer-preview/auburn-{k:02}.png'))
    changed=np.any(silver!=auburn,axis=2)
    assert changed.sum()>0 and not changed[65:].any();hair_changes.append(int(changed.sum()))
link_files=[r/'README.md',Path('skills/modular-eight-direction-sprites/studies/walk-test/README.md'),Path('skills/modular-eight-direction-sprites/references/one-motion-acceptance.md')]
for path in link_files:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        # This report is generated below; all other links must exist beforehand.
        if '://' not in link and link!='artifact-check.json':
            assert (path.parent/link.split('#')[0]).exists(),(str(path),link)
result={'status':'TECHNICAL_REVIEW_CHECKS_PASS_ART_AND_RELEASE_BLOCKED','source_hash_verified':True,
        'saved_blend_hash_verified':True,'render_receipt_counts':receipts,'full_body_native_frames':64,
        'complete_SE_part_RGBA_depth_pairs':104,'hair_swap_changed_pixels_per_key':hair_changes,
        'hair_swap_changed_pixels_below_native_row_65':0,'animations':motions,
        'relative_review_links_exist':True,'exact_layer_RGB_pass':pkg['layer_comparison']['exact_color_pass'],
        'painted_pose_verified':False,'painted_parts_complete':False,'release_ready':False}
(r/'artifact-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert (r/'artifact-check.json').exists()
print('ARTIFACT_CHECK',len(motions),'decoded eight-exposure animations; 64 original native frames; 104 SE part/depth pairs; actual hair changes',hair_changes)
