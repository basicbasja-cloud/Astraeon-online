"""Actual evaluated source-bone filmstrip; one fixed projection/scale, no retarget."""
import gzip,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
s=json.loads(gzip.decompress((ROOT/'new-preset-samples.json.gz').read_bytes()));inv=json.loads((ROOT/'new-preset-inventory.json').read_text())
rows=[]
for bank in s['banks']:
 for c in bank['clips']:
  kind='rest' if c['name']=='T-Pose' else 'terminal_or_inactive_pose_name' if c['name'].endswith('_Pose') else 'motion_candidate'
  rows.append({'source_file':bank['source_file'],'source_sha256':bank['source_sha256'],'clip':c['name'],'category':kind,'sample_count':len(c['samples']),'time_seconds':[p['source_time_seconds'] for p in c['samples']],'contact':'unknown','target_retarget_executed':False})
(ROOT/'preset-clip-index.json').write_text(json.dumps({'records':rows,'serialized_record_count':len(rows),'unique_names':len({r['clip'] for r in rows}),'sample_count':sum(r['sample_count'] for r in rows),'categories':{k:sum(r['category']==k for r in rows) for k in sorted({r['category'] for r in rows})},'production_pass':False},indent=2)+'\n')
selected=['Walking_A','Dodge_Forward','Melee_1H_Attack_Slice_Diagonal','Melee_Block_Hit','Ranged_Bow_Draw','Ranged_Magic_Spellcasting','Hit_A','Death_A','PickUp','Use_Item','Sit_Floor_Down','Chopping']
pairs=[]
for name in selected:
 bank=next(b for b in s['banks'] if 'Medium' in b['source_file'] and any(c['name']==name for c in b['clips']));clip=next(c for c in bank['clips'] if c['name']==name);pairs.append((bank,clip))
def project(v):x,y,z=v;return ((x-y)*.7071,-z*.90+(x+y)*.22)
points=[project(v) for b,c in pairs for f in c['samples'] for v in f['world_joints'].values()];minx=min(p[0] for p in points);maxx=max(p[0] for p in points);miny=min(p[1] for p in points);maxy=max(p[1] for p in points);scale=min(116/(maxx-minx),146/(maxy-miny));cx=(minx+maxx)/2;cy=(miny+maxy)/2
im=Image.new('RGB',(9*150,len(pairs)*200),(29,35,47));d=ImageDraw.Draw(im);manifest=[]
for row,(b,c) in enumerate(pairs):
 d.text((6,row*200+3),c['name']+' / external source projection, not our character',fill='white')
 for col,f in enumerate(c['samples']):
  ox=col*150+75;oy=row*200+110;coords={n:(ox+(project(v)[0]-cx)*scale,oy+(project(v)[1]-cy)*scale) for n,v in f['world_joints'].items()}
  for n,p in coords.items():
   parent=b['bones'][n]['parent'];color='#349eff' if n.endswith('.r') else '#ff9839' if n.endswith('.l') else '#bbc6d5'
   if parent:d.line((*coords[parent],*p),fill=color,width=2)
   d.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill=color)
  d.text((col*150+5,row*200+182),f"{f['source_time_seconds']:.3f}s",fill='white')
 manifest.append({'clip':c['name'],'source_sha256':b['source_sha256'],'times_seconds':[f['source_time_seconds'] for f in c['samples']]})
im.save(ROOT/'preset-source-bone-grid.png');(ROOT/'preset-grid-manifest.json').write_text(json.dumps({'rows':manifest,'fixed_projection':[.7071,-.7071,-.9,.22],'one_global_scale':scale,'per_pose_fitting':False,'sample_file_sha256':hashlib.sha256((ROOT/'new-preset-samples.json.gz').read_bytes()).hexdigest(),'anatomical_identity_source_names_only':True,'contact':'unknown','production_pass':False},indent=2)+'\n');print(json.dumps({'records':len(rows),'sampled_poses':sum(r['sample_count'] for r in rows),'grid_clips':len(pairs)}))
