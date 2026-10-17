from pathlib import Path
import json,hashlib
p=Path('work/all-actions-v61/generation/S-candidate7');e=json.loads((p/'extraction.json').read_text());scale=e['one_bank_matrix'][0];dx=e['one_bank_matrix'][4];dy=e['one_bank_matrix'][5]
r=[]
for i,k in enumerate(e['keys']):
 f=p/'keys'/f'{i:02}.png';c=k['native_bbox'][1]
 if i==0:box=[170,91,340,218];points=[[255,130],[230,145],[280,140],[255,189],[255,223],[180,210],[330,210]];labels=[1,1,1,1,0,0,0]
 else:
  def xy(x,y):return [round(x*scale+dx),round(y*scale+dy)]
  box=xy(122,c-5)+xy(240,c+100)
  points=[xy(180,c+30),xy(156,c+45),xy(209,c+43),xy(183,c+73),xy(186,c+110),xy(132,c+101),xy(242,c+95)];labels=[1,1,1,1,0,0,0]
 r.append({'path':f'keys/{i:02}.png','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'box':box,'points':points,'labels':labels})
(p/'head-prompts.json').write_text(json.dumps({'checkpoint_sha256':'6dbb90523a35330fedd7f1d3dfc66f995213d81b29a5ca8108dbcdd4e37d6c2f','frames':r},indent=2))
