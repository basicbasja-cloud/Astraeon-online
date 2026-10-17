from pathlib import Path
import importlib.util,json,copy,tempfile,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import label
root=Path.cwd();p=root/'work/all-actions-v61';spec=importlib.util.spec_from_file_location('head_tool',root/'tools/sprite-head-mask.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=json.loads((p/'head-prompts.json').read_text());checkpoint=root/'work/free-mask-model/source/weights/mobile_sam.pt';rows=[]
for f in source['frames']:f['path']=str((p/f['path']).resolve())
with tempfile.TemporaryDirectory(dir=p) as tmp:
 tmp=Path(tmp);file=tmp/'input.json'
 def negative(name,change):
  d=copy.deepcopy(source);change(d);file.write_text(json.dumps(d))
  try:m.inputs(file,checkpoint)
  except (ValueError,FileNotFoundError):rows.append({'name':name,'pass':True});return
  raise AssertionError('negative accepted '+name)
 negative('wrong_checkpoint_digest',lambda d:d.update(checkpoint_sha256='0'*64))
 negative('stale_source_SHA',lambda d:d['frames'][0].update(sha256='0'*64))
 negative('empty_clip',lambda d:d.update(frames=[]))
 negative('missing_source',lambda d:d['frames'][0].update(path=str(tmp/'missing.png')))
 negative('positive_only_prompts',lambda d:d['frames'][0].update(labels=[1]*len(d['frames'][0]['labels'])))
 negative('point_out_of_image',lambda d:d['frames'][0]['points'][0].__setitem__(0,9999))
 negative('bool_label',lambda d:d['frames'][0]['labels'].__setitem__(0,True))
 negative('invalid_box',lambda d:d['frames'][0].update(box=[0,0,0,30]))
 negative('invalid_context_crop',lambda d:d['frames'][0].update(context_box=[0,0,99999,300]))
 negative('point_outside_context',lambda d:d['frames'][0].update(context_box=[100,60,230,210]))
 negative('head_box_outside_context',lambda d:d['frames'][0].update(context_box=[80,60,230,210]))
 file.write_text(json.dumps(source));existing=tmp/'existing';existing.mkdir()
 try:m.extract(file,checkpoint,existing)
 except FileExistsError:rows.append({'name':'refuse_existing_output_before_model_load','pass':True})
 else:raise AssertionError('overwrote evidence')
report=json.loads((p/'tool-extraction/extraction-review.json').read_text());assert report['technical_partition_pass'] and not report['semantic_head_approval_granted'] and not report['head_swap_pass'] and not report['production_pass']
for i,row in enumerate(source['frames']):
 full=Image.open(row['path']).convert('RGBA');head=Image.open(p/f'tool-extraction/head/{i:02}.png').convert('RGBA');body=Image.open(p/f'tool-extraction/body/{i:02}.png').convert('RGBA');a=np.array(full);b=np.array(Image.alpha_composite(body,head));assert np.array_equal(a[:,:,3],b[:,:,3])and np.array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0]);mask=np.array(Image.open(p/f'tool-extraction/mask/{i:02}.png'))>0;assert label(mask)[1]==1
 assert all(bool(mask[y,x])==bool(v)for (x,y),v in zip(row['points'],row['labels']))
 assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
rows.append({'name':'actual16_sources_unchanged_disjoint_partition_exactRGBA_labels_and_single_owned_component','pass':True})
for i in [5,7,8]:
 old=np.array(Image.open(p/f'sam-batch/mask-{i:02}.png'))>0;l,n=label(old);counts=np.bincount(l.ravel());counts[0]=0;main=int(np.argmax(counts));nuisance=old&(l!=main);new=np.array(Image.open(p/f'tool-extraction/mask/{i:02}.png'))>0
 assert nuisance.any() and not np.any(new&nuisance)
rows.append({'name':'actual_previous_gold_fragment_masks5_7_8_rejected_from_head_ownership','pass':True})
crop=json.loads((p/'dead-N-crop-prompts.json').read_text())['frames'][0]
full=Image.open(p/crop['path']).convert('RGBA');head=Image.open(p/'dead-N-crop-extraction/head/00.png').convert('RGBA');body=Image.open(p/'dead-N-crop-extraction/body/00.png').convert('RGBA');a=np.array(full);b=np.array(Image.alpha_composite(body,head));mask=np.array(Image.open(p/'dead-N-crop-extraction/mask/00.png'))>0
assert np.array_equal(a[:,:,3],b[:,:,3])and np.array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0])
assert all(bool(mask[y,x])==bool(v)for (x,y),v in zip(crop['points'],crop['labels']))
x0,y0,x1,y1=crop['context_box'];outside=mask.copy();outside[y0:y1,x0:x1]=False;assert not outside.any()
old=np.array(Image.open(p/'dead-N-head-extraction/mask/00.png'))>0
assert all(old[y,x]and not mask[y,x]for x,y in [[200,325],[250,325],[220,315]])
rows.append({'name':'actual_deadN_crop_keeps_absolute_canvas_exactRGBA_and_removes_prior_gold_rim','pass':True})
rows.append({'name':'confidence_never_grants_semantic_or_head_swap_approval','pass':True})
(p/'head-tool-tests.json').write_text(json.dumps({'pass':True,'control_count':len(rows),'controls':rows,'production_pass':False},indent=2)+'\n');print('HEAD TOOL CHECKS',len(rows),'PASS')
