"""Study references: same-frame masked repairs, never production admission."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

BASE = Path('authoring/characters/factory-v3/patch-0.0.1')
OUT = Path(__file__).parent
GUIDE = BASE/'research/tall-guide-proportion-pilot-20261027/mage130-colored-high1536-capture'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads((GUIDE/'manifest.json').read_text())
    for batch in range(4):
        dest = OUT/f'batch-{batch:02d}'
        dest.mkdir(exist_ok=True)
        (dest/'Masks').mkdir(exist_ok=True)
        plates = {k: Image.new('RGBA',(1536,1024)) for k in ('arm','erase','original','guide')}
        records = []
        for slot, index in enumerate(range(batch*6,(batch+1)*6)):
            path = BASE/'review/mage-female-sw-canonical-pilot-20261027/Master'/f'{index:03d}.png'
            original = Image.open(path).convert('RGBA')
            a = np.asarray(original)
            r,g,b = a[:,:,:3].astype(float).transpose((2,0,1))
            yy,xx = np.indices(a.shape[:2])
            cyan=(a[:,:,3]>128)&(g>r*1.2)&(b>r*1.2)&(yy>280)&(yy<400)&(xx>350)&(xx<445)
            labels,_=ndimage.label(cyan)
            sizes=np.bincount(labels.ravel());sizes[0]=0
            y,x=np.where(labels==sizes.argmax());cx=float(x.mean())
            erase=Image.new('L',original.size)
            d=ImageDraw.Draw(erase)
            # Actual old prop/extra hanging hand stop above the lower robe.
            d.rectangle((cx-18, min(300,int(y.min())-18), cx+34,449),fill=255)
            frame=manifest['views']['SW']['frames'][index]
            grip=np.asarray(frame['weapon_guide']['grip'])*.5
            tip=np.asarray(frame['weapon_guide']['tip'])*.5
            axis=(tip-grip)/np.linalg.norm(tip-grip)
            arm=erase.copy();d=ImageDraw.Draw(arm)
            d.polygon([(282,367),(351,367),(391,380),(397,421),(390,445),(298,445),(282,427)],fill=255)
            d.line([tuple(tip),tuple(grip-axis*112)],fill=255,width=18)
            normal=np.array([-axis[1],axis[0]])*19
            jewel_base=tip-axis*54
            d.polygon([tuple(p) for p in (tip+normal,tip-normal,jewel_base-normal,jewel_base+normal)],fill=255)
            record={'index':index,'master':str(path),'master_sha256':sha(path),'old_staff_center_x':cx,'target_guide_grip_authoring':grip.tolist()}
            for kind, mask in [('arm',arm),('erase',erase)]:
                mask_path=dest/'Masks'/f'{index:03d}-{kind}.png';mask.save(mask_path)
                record[kind+'_mask_sha256']=sha(mask_path)
                marked=original.copy();marked.paste((255,0,255,255),(0,0,768,768),mask)
                plates[kind].paste(marked.crop((224,224,576,576)).resize((512,512),Image.Resampling.LANCZOS),((slot%3)*512,(slot//3)*512))
            plates['original'].paste(original.crop((224,224,576,576)).resize((512,512),Image.Resampling.LANCZOS),((slot%3)*512,(slot//3)*512))
            guide_path=GUIDE/frame['image'];record['guide_sha256']=sha(guide_path)
            guide=Image.open(guide_path).convert('RGBA').crop((448,448,1152,1152)).resize((512,512),Image.Resampling.LANCZOS)
            plates['guide'].paste(guide,((slot%3)*512,(slot//3)*512))
            records.append(record)
        for kind,plate in plates.items():
            plate.save(dest/f'{kind}.png')
            display=Image.new('RGBA',plate.size,'#ddd');display.alpha_composite(plate)
            display.convert('RGB').save(dest/f'{kind}-gray.jpg',quality=97)
        recipe={'indices':[r['index'] for r in records],'viewport':[224,224,576,576],'grid':[3,2],'cell':[512,512],'canonical_canvas':[768,768],'frames':records,'guide_manifest_sha256':sha(GUIDE/'manifest.json'),'runtime_admitted':False,'art_approved':False}
        (dest/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')

if __name__=='__main__':
    main()
