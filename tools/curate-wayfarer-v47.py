"""Compress review evidence from actual captures; preserve raw local artifacts."""
from pathlib import Path
import argparse,json,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--raw',type=Path,default=Path.home()/'AppData/Local/Temp/astraeon-local-preparation/wayfarer-v47-gameplay');ap.add_argument('--output',type=Path,default=ROOT/'docs/review/wayfarer-v47');args=ap.parse_args()
raw=args.raw;out=args.output;out.mkdir(parents=True,exist_ok=True)
report=json.loads((raw/'report.json').read_text(encoding='utf-8'))
assert not report['runtime_errors'] and not report['resource_errors']
evidence=report['evidence'];motions=[e for e in evidence if 'mode' in e]
assert report['layout']=='wayfarer-painterly-civic-town-v47'
assert len(motions)==24 and all(len({tuple(e['keys']) for e in motions if e['mode']==mode})==8 for mode in ['walk','run','sprint'])
assert all(e['renderedSole']['samples']>0 and e['renderedSole']['maxErrorWorld']<.025 and e['renderedSole']['maxStanceDriftWorld']<.025 for e in motions)
counts={key:sum(key in e for e in evidence) for key in ['spatial_case','stop','service','reaction_direction']};assert all(v==8 for v in counts.values()),counts
summary={'layout':report['layout'],'nodeTests':71,'gameplayCases':counts,'movementCases':len(motions),'maxRenderedSoleErrorWorld':max(e['renderedSole']['maxErrorWorld'] for e in motions),'maxRenderedStanceDriftWorld':max(e['renderedSole']['maxStanceDriftWorld'] for e in motions),'runtimeErrors':report['runtime_errors'],'resourceErrors':report['resource_errors'],'goldenApproval':'pending human visual review'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
shutil.copyfile(raw/'report.json',out/'gameplay.json')
for name in ['arrival-1280-800','plaza-1280-800','hall-1280-800','market-1280-800','residential-1280-800','shrine-1280-800','blacksmith-1280-800','inn-1280-800','gate-under-arch-1280-800','hall-terrace-1280-800','plaza-390-844','plaza-844-390','plaza-768-1024','field-threshold-1280-800']:
 Image.open(raw/(name+'.png')).convert('RGB').save(out/(name+'.jpg'),quality=90,optimize=True)
# Three ordinary input samples show complete rendered frames, including the
# background/lighting/contact behavior. No source poses are manufactured here.
sheet=Image.new('RGB',(8*144,3*190),'#1b2635');draw=ImageDraw.Draw(sheet)
for row,mode in enumerate(['walk','run','sprint']):
 folder=raw/'motion-series'/(mode+'-d');frames=json.loads((folder/'frames.json').read_text())
 paths=[folder/f'{i:03d}.png' for i in range(len(frames))];assert len(paths)>=8
 for col in range(8):
  index=round(col*(len(paths)-1)/7);im=Image.open(paths[index]).convert('RGB');sheet.paste(im,(col*144,row*190+26))
  draw.text((col*144+5,row*190+6),f'{mode} +{frames[index]["elapsed"]:.2f}s',fill='#eee5d3')
 gif=[Image.open(p).convert('RGB') for p in paths]
 # Inter-sample timing is measured in the gameplay run, not inferred from art.
 durations=[max(20,round((b['time']-a['time'])*1000)) for a,b in zip(frames,frames[1:])];durations.append(durations[-1])
 gif[0].save(out/(mode+'-gameplay.gif'),save_all=True,append_images=gif[1:],duration=durations,loop=0,optimize=True)
sheet.save(out/'movement-frames.jpg',quality=92,optimize=True)
for folder in [out/'views',out/'landmark']:
 records=json.loads((folder/'views.json').read_text())
 for record in records:
  assert not record['errors'];name=record['name'];png=folder/(name+'.png');jpg=folder/(name+'.jpg')
  if png.exists():Image.open(png).convert('RGB').save(jpg,quality=90,optimize=True)
  else:assert jpg.exists(),'Missing original or curated still: '+name
  record['image']=str(jpg.relative_to(ROOT)).replace('\\','/')
 (folder/'views.json').write_text(json.dumps(records,indent=2)+'\n')
for row in ['S','SE','E','NE','N','NW','W','SW']:
 folder=raw/'reaction-series'/row;frames=json.loads((folder/'frames.json').read_text());paths=[folder/f'{i:03d}.png' for i in range(len(frames))]
 indices=[]
 for state in ['hit','death']:
  candidates=[i for i,f in enumerate(frames) if f['state']==state]
  indices.extend(candidates[round(j*(len(candidates)-1)/3)] for j in range(4))
 contact=Image.new('RGB',(8*200,206),'#1b2635');d=ImageDraw.Draw(contact)
 for col,i in enumerate(indices):
  contact.paste(Image.open(paths[i]).convert('RGB'),(col*200,26));d.text((col*200+5,5),f'{row} {frames[i]["state"]} {frames[i]["progress"]:.2f}',fill='#eee5d3')
 contact.save(out/('reaction-'+row+'.jpg'),quality=88,optimize=True)
print('Curated normal-input views, 24 sole reports, 3 animated samples and 8 reaction strips')
