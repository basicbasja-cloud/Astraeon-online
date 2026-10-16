"""Fresh authoring only. Binary ownership and exposure edits, never pose fitting."""
import copy, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
OLD = P.parent / 'whole-body-v58'
published = subprocess.run(['git','cat-file','-e','HEAD:'+str(Path(__file__).resolve().relative_to(ROOT))],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if published.returncode == 0:
    raise SystemExit('Published case is frozen. Copy authoring into a fresh versioned case first.')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d): p.write_text(json.dumps(d, indent=2) + '\n')
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
review = module('review_pack', ROOT / 'tools/sprite-review-pack.py')
motion = module('motion', ROOT / 'tools/sprite-motion-review.py')
contact = module('contact', ROOT / 'tools/sprite-contact-review.py')

# Authored lower contour, original fixed-grid image coordinates. Above this
# boundary belongs to the head; below belongs to the body/collar. No interpolation
# of pixels, feathering, threshold-color matting, image translation or rescale.
# Full original sources remain the actual art authority.
boundaries = [
 [[80,108],[94,123],[105,133],[116,134],[124,143],[140,150],[155,144],[166,134],[178,124],[191,109],[215,100]],
 [[80,128],[95,145],[108,151],[117,157],[129,165],[144,170],[158,163],[168,151],[180,141],[195,126],[215,120]],
 [[80,146],[95,161],[108,166],[117,175],[128,182],[140,186],[155,180],[166,168],[177,157],[192,144],[215,140]],
 [[80,150],[95,166],[109,170],[119,179],[130,186],[142,189],[155,182],[166,172],[178,160],[192,148],[215,140]],
 [[80,156],[95,172],[108,179],[119,186],[129,193],[139,196],[153,189],[165,178],[177,165],[192,153],[215,145]],
 [[80,162],[95,178],[107,183],[118,193],[130,200],[141,203],[155,196],[167,185],[179,172],[193,159],[215,150]],
 [[80,170],[95,185],[109,190],[121,201],[134,209],[146,212],[160,204],[171,193],[183,180],[197,165],[215,160]],
 [[80,191],[96,207],[110,212],[123,222],[135,228],[147,232],[161,224],[173,212],[185,199],[199,185],[215,175]],
 [[80,117],[95,135],[108,141],[119,151],[130,158],[142,162],[156,154],[168,142],[180,129],[194,114],[215,105]],
 [[80,103],[95,118],[108,123],[119,134],[131,141],[143,144],[157,136],[169,125],[181,112],[195,98],[215,90]],
 [[80,105],[95,122],[108,128],[119,137],[132,143],[144,146],[158,138],[170,126],[182,113],[196,100],[215,90]],
 [[80,97],[95,114],[108,120],[120,130],[132,136],[145,139],[159,131],[171,119],[183,105],[197,93],[215,85]],
 [[80,83],[95,99],[108,105],[120,114],[132,120],[144,123],[157,115],[169,103],[182,90],[196,77],[215,70]],
 [[80,87],[95,103],[108,109],[120,118],[133,124],[146,127],[159,119],[171,107],[184,94],[198,81],[215,75]],
 [[80,88],[95,104],[108,110],[120,119],[133,125],[146,128],[159,120],[171,108],[184,95],[198,82],[215,75]],
 [[80,84],[95,100],[108,106],[120,115],[133,121],[146,124],[159,116],[171,104],[184,91],[198,78],[215,70]],
]
# First hand trace retained in negative-first-contour: the deep-pose right edge
# still assigned the shoulder to the head. Trace the actual visible hair/ear
# silhouette instead of extending the diagonal through the gold pauldron.
right_edges = [
 [[166,134],[174,126],[184,116],[191,103]],
 [[168,151],[176,142],[182,132],[189,119]],
 [[166,168],[173,158],[180,146],[186,132]],
 [[166,172],[173,161],[180,149],[186,136]],
 [[165,178],[172,166],[178,153],[185,140]],
 [[167,185],[174,172],[180,159],[185,146]],
 [[171,193],[178,181],[183,169],[186,157]],
 [[173,208],[180,200],[183,190],[183,179],[179,168]],
 [[168,142],[175,130],[181,117],[186,104]],
 [[169,125],[176,114],[182,101],[187,89]],
 [[170,126],[177,115],[183,102],[188,90]],
 [[171,119],[178,108],[184,95],[189,83]],
 [[169,103],[176,92],[182,79],[187,67]],
 [[171,107],[178,96],[184,83],[189,71]],
 [[171,108],[178,97],[184,84],[189,72]],
 [[171,104],[178,93],[184,80],[189,68]],
]
for i, line in enumerate(boundaries):
    line[2][1] -= 3
    line[5][1] -= 3
    line[4][1] -= 1
    line[6][1] -= 1
    boundaries[i] = line[:7] + right_edges[i]
clip = json.loads((OLD / 'pickup-S-four-slot.json').read_text())
rows = []
for i, boundary in enumerate(boundaries):
    full = Image.open(OLD / f'frames/full/{i:02}.png').convert('RGBA')
    mask = Image.new('L', full.size)
    ImageDraw.Draw(mask).polygon([(0,0),(full.width,0),(full.width,boundary[-1][1]),
                                 *reversed([tuple(p) for p in boundary]),(0,boundary[0][1])], fill=255)
    empty = Image.new('RGBA', full.size)
    head = Image.composite(full, empty, mask)
    body = Image.composite(empty, full, mask)
    reconstructed = Image.alpha_composite(body, head)
    a, b = np.array(full), np.array(reconstructed)
    assert np.array_equal(a[:,:,3], b[:,:,3]) and np.array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0])
    assert not np.any((np.array(head)[:,:,3] > 0) & (np.array(body)[:,:,3] > 0))
    for slot, im in [('head',head),('body',body)]:
        dest = P / 'corrected-ownership' / slot / f'{i:02}.png'
        dest.parent.mkdir(parents=True, exist_ok=True); im.save(dest)
        clip['frames'][i]['slots'][slot] = {'asset':str(dest.relative_to(P)), 'sha256':sha(dest)}
    oldhead = np.array(Image.open(OLD/f'frames/head/{i:02}.png').convert('RGBA'))
    newhead = np.array(head)
    rows.append({'index':i, 'full_source_sha256':sha(OLD/f'frames/full/{i:02}.png'),
                 'lower_head_boundary':boundary, 'visible_recomposition_exact':True,
                 'pixels_transferred_head_to_body':int(np.sum((oldhead[:,:,3]>0)&(newhead[:,:,3]==0))),
                 'pixels_restored_body_to_head':int(np.sum((oldhead[:,:,3]==0)&(newhead[:,:,3]>0)))})
clip.update(art_status='rejected_motion_no_new_drawing',
            head_extraction_status='manual_contour_revision_requires_visual_review_not_swap_approval')
save(P/'pickup-corrected-slots.json',clip)
save(P/'ownership-review.json',{'technical_partition_pass':True,'frames':rows,
    'full_figure_pixels_changed':False,'head_swap_pass':False,'production_pass':False})

def exposure_clip(title, source_frames, mapping, durations):
    return {'title':title,'canvas':list(Image.open(source_frames[0]).size),
            'minimum_unique_drawings':0,
            'frames':[{'path':str(source_frames[i].relative_to(ROOT)), 'sha256':sha(source_frames[i]),
                       'duration_ms':duration} for i,duration in zip(mapping,durations)]}
def localize(data):
    for row in data['frames']:
        row['path'] = '../../../' + row['path']
    return data
original = [OLD/f'frames/full/{i:02}.png' for i in range(16)]
duration = [90]*15+[550]
mapping = list(range(8)) + list(reversed(range(8)))
for name, mapping_, title in [('original',list(range(16)),'v58 original / REJECTED'),
        ('reverse-recovery',mapping,'Reverse-recovery experiment / NOT APPROVED')]:
    data = localize(exposure_clip(title,original,mapping_,duration))
    save(P/f'{name}.json',data)
    target=P/f'{name}-review'
    if target.exists():shutil.rmtree(target)
    review.build(P/f'{name}.json',target)
    case = json.loads((OLD/'motion-case.json').read_text())
    case['frames'] = [{k:r[k] for k in ['path','sha256']} for r in data['frames']]
    save(P/f'{name}-motion-case.json',case)
    save(P/f'{name}-motion-review.json',motion.evaluate(case,P))
    c = json.loads((OLD/'contact-case.json').read_text());c['frames']=case['frames']
    save(P/f'{name}-contact-review.json',contact.evaluate(c,P))

# Same whole body pixels, new explicit exposure order; no new native drawings.
candidate = copy.deepcopy(clip)
candidate['frames'] = [copy.deepcopy(clip['frames'][i]) for i in mapping]
for f,d in zip(candidate['frames'],duration):f['duration_ms']=d
candidate['art_status']='reverse_recovery_diagnostic_rejected_contact_not_new_16_drawings'
save(P/'reverse-recovery-slots.json',candidate)
dest = P/'reverse-recovery-frames';dest.mkdir(exist_ok=True)
for i,source in enumerate(mapping):shutil.copyfile(original[source],dest/f'{i:02}.png')

# Approved old one-view control. Splitting holds doubles exposure count without
# inventing drawings or changing source-clock motion. Explicitly not a16newpose fix.
control_dir=P.parent/'recovery-key-v39/renders/review/full'
control_images=[control_dir/f'{i:02}.png'for i in range(8)]
contract=json.loads((P.parent/'recovery-key-v39/motion-contract.json').read_text())
times=contract['clocks']['source']
split=[d//20*10 for d in times]
control_map=[i for i in range(8)for _ in range(2)]
control_durations=[v for d,s in zip(times,split)for v in [s,d-s]]
data=localize(exposure_clip('v39 whole-body control /16 holds,7 unique drawings',control_images,control_map,control_durations))
save(P/'accepted-control.json',data)
target=P/'accepted-control-review'
if target.exists():shutil.rmtree(target)
review.build(P/'accepted-control.json',target)

# Ownership previews, including original contaminated masks as retained negative.
for name, paths in [('old-head',[OLD/f'frames/head/{i:02}.png'for i in range(16)]),
                    ('corrected-head',[P/f'corrected-ownership/head/{i:02}.png'for i in range(16)])]:
    data=localize(exposure_clip(name+' / contour diagnostic',paths,list(range(16)),duration))
    save(P/f'{name}.json',data)
    target=P/f'{name}-review'
    if target.exists():shutil.rmtree(target)
    review.build(P/f'{name}.json',target)

save(P/'exposure-edit.json',{'source':'whole-body-v58','mapping':mapping,
     'method':'Reuse original complete figures, reverse descent as recovery. No image editing.',
     'new_drawings':0,'unique_rgba_drawings':8,'logical_exposures':16,
     'contact_pass':False,'production_pass':False,
     'scope':'Crown discontinuity experiment only; reverse motion has no prop pickup or secondary recovery acting.'})
print('Built five local GIF review packs and corrected ownership; production remains false')
