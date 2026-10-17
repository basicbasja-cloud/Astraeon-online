from pathlib import Path
import json,hashlib
p=Path('work/all-actions-v61/generation')
for name,v,lefts in [('W-candidate2','W',[123,97,99,89,77,74,70,70]),('E-candidate1','E',[156,177,197,216,211,232,235,235])]:
 f=p/name;e=json.loads((f/'extraction.json').read_text());m=e['one_bank_matrix'];scale=m[0];dx=m[4];dy=m[5];rows=[]
 for i,k in enumerate(e['keys']):
  path=f/'keys'/f'{i:02}.png';c=k['native_bbox'][1];left=lefts[i]
  def xy(x,y):return [round(x*scale+dx),round(y*scale+dy)]
  if i==0:
   old=json.loads(Path('work/all-actions-v61/static-head-prompts.json').read_text());r=next(r for r in old['frames']if '/idle/'+v+'/' in r['path']);box=r['box'];points=r['points'];labels=r['labels']
  else:
   if v=='W':points=[xy(left+55,c+30),xy(left+25,c+43),xy(left+80,c+42),xy(left+43,c+76),xy(left+78,c+100),xy(left+100,c+118),xy(left+125,c+133)]
   else:points=[xy(left+49,c+30),xy(left+25,c+43),xy(left+78,c+43),xy(left+78,c+76),xy(left+45,c+104),xy(left+30,c+122),xy(left+5,c+139)]
   labels=[1,1,1,1,0,0,0];box=xy(left-8,c-5)+xy(left+120,c+105)
  rows.append({'path':f'keys/{i:02}.png','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'box':box,'points':points,'labels':labels})
 (f/'head-prompts.json').write_text(json.dumps({'checkpoint_sha256':'6dbb90523a35330fedd7f1d3dfc66f995213d81b29a5ca8108dbcdd4e37d6c2f','frames':rows},indent=2))
