from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib
sys.path.insert(0,'tools/character_factory_v3')
from extract_transparent_component_sheet import extract
from source_segment_timing import source_timing
base=Path('authoring/characters/factory-v3/patch-0.0.1');src=base/'painted-candidates/mage-sw-full-sequence-pilot-20261027';out=base/'review/mage-sw-full-sequence-pilot-20261027';(out/'Master').mkdir(parents=True,exist_ok=True);records=[];previews=[];blockers=[]
manifest=json.loads((base/'guides/ebac492fbc20b608880c/manifest.json').read_text());timing=source_timing(manifest,'SW')
for batch in range(4):
 raw=src/f'batch-{batch}-raw.png';images,receipt=extract(Image.open(raw),[3,2],[768,768],[128,128],minimum_figure_area=10000);(out/f'batch-{batch}-extraction.json').write_text(json.dumps(receipt,indent=2)+'\n');blockers.extend({'batch':batch,'blocker':b} for b in receipt['production_blockers'])
 for j,im in enumerate(images):
  index=batch*6+j;path=out/'Master'/f'{index:03d}.png';im.save(path);records.append({'index':index,'batch':batch,'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'master_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  crop=im.crop((96,96,672,672));bg=Image.new('RGB',(576,604),'#ddd');bg.paste(crop,(0,28),crop);d=ImageDraw.Draw(bg);d.text((8,8),f'Mage male SW | frame {index:02d} | batch {batch} | DRAFT',fill='black');previews.append(bg)
for suffix,factor in [('source-time',1),('slow',3)]:previews[0].save(out/f'{suffix}.gif',save_all=True,append_images=previews[1:],duration=[d*factor for d in timing['gif_durations_ms']],loop=0,disposal=2)
contact=Image.new('RGB',(576*4,604*2),'#ddd')
for k,i in enumerate([0,5,6,11,12,17,18,23]):contact.paste(previews[i],((k%4)*576,(k//4)*604))
contact.save(out/'batch-boundary-contact.jpg',quality=96)
(out/'receipt.json').write_text(json.dumps({'status':'FULL_24_FRAME_PILOT_REQUIRES_ART_AND_TRANSITION_REVIEW','frames':records,'timing':timing,'source_job':'ebac492fbc20b608880c','native_cell':[512,512],'master_canvas':[768,768],'shared_offset':[128,128],'viewport':[96,96,672,672],'per_frame_scaling_or_fitting':False,'extraction_blockers':blockers,'runtime_admitted':False,'note':'Batch-to-batch scale/design changes must be reviewed, not hidden with per-batch figure fitting. GIF repeats a one-shot for inspection.'},indent=2)+'\n');print('Frames',len(records),'blockers',blockers)
