"""Split deliverable below GitHub's individual-file limit and verify every ZIP member."""
from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2];KIT=ROOT/'work/final-delivery';OUT=P/'delivery';rows=[]
for name,iswalk in [('astraeon-walk-png.zip',True),('astraeon-core-and-tools.zip',False)]:
 target=OUT/name
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for f in sorted(KIT.rglob('*')):
   if f.is_file()and'__pycache__'not in f.parts and (str(f.relative_to(KIT)).startswith('frames/walk/')==iswalk):z.write(f,str(f.relative_to(KIT)))
 assert target.stat().st_size<100*1024*1024
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).digest()==hashlib.sha256((KIT/n).read_bytes()).digest(),n
  rows.append({'path':name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'members':len(z.namelist()),'every_member_matches_staging':True,'crc_pass':True})
(OUT/'archives-review.json').write_text(json.dumps({'pass':True,'archives':rows},indent=2)+'\n');print(rows)
