from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
b=Path('authoring/characters/factory-v3/patch-0.0.1/review');src=b/'archer-remaining-view-head-complete-proposals-v5-20261027';out=b/'archer-remaining-view-head-complete-proposals-v6-20261027';out.mkdir(exist_ok=True);a=json.loads((src/'proposal-receipt.json').read_text());polygons={'female/SW/007':[[(180,169),(229,169),(229,176),(180,182)],[(180,176),(231,176),(231,205),(180,205)]],'male/NE/007':[[(300,172),(335,172),(335,205),(300,205),(299,185),(296,182),(298,177)]],'female/SE/010':[[(306,129),(325,129),(325,190),(283,190),(284,167),(290,167),(293,161),(296,158),(298,151),(299,144),(302,138)]]}
for r in a['frames']:
 s,v,i=r['sex'],r['view'],r['index'];d=out/s/v;d.mkdir(parents=True,exist_ok=True);(d/'BodyRest').mkdir(exist_ok=True);key=f'{s}/{v}/{i:03d}';p=b/'archer-coherent-recovery-masters-v2-20261026'/s/v/'Master'/f'{i:03d}.png';assert hashlib.sha256(p.read_bytes()).hexdigest()==r['master_sha256']
 if key not in polygons:
  shutil.copy2(src/s/v/f'{i:03d}.png',d/f'{i:03d}.png');shutil.copy2(src/s/v/'BodyRest'/f'{i:03d}.png',d/'BodyRest'/f'{i:03d}.png');continue
 master=np.array(Image.open(p).convert('RGBA'));head=np.array(Image.open(src/s/v/f'{i:03d}.png'));mask=head[:,:,3]>0;ex=Image.new('L',(512,512));draw=ImageDraw.Draw(ex)
 for poly in polygons[key]:draw.polygon(poly,fill=255)
 returned=mask&(np.array(ex)>0);mask&=~returned;h=master.copy();h[~mask]=0;rest=master.copy();rest[mask]=0;Image.fromarray(h).save(d/f'{i:03d}.png');Image.fromarray(rest).save(d/'BodyRest'/f'{i:03d}.png');re=Image.new('RGBA',(512,512));re.alpha_composite(Image.fromarray(rest));re.alpha_composite(Image.fromarray(h));visible=master[:,:,3]>0;assert np.array_equal(np.array(re)[visible],master[visible]);r['native_foreign_ownership_repair']={'exclude_polygons':polygons[key],'returned_to_bodyrest_visible_pixels':int(returned.sum()),'reason':'Native source comparison: forearm/shaft/white raised sleeve belongs outside HeadHair. No replacement pixels.'};r['visible_recomposition_mismatch_pixels']=0
(out/'proposal-receipt.json').write_text(json.dumps(a,indent=2)+'\n');(out/'repair-source.py').write_bytes(Path(__file__).read_bytes());(out/'native-ownership-repairs.json').write_text(json.dumps(polygons,indent=2)+'\n')
