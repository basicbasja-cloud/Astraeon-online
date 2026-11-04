"""Put actual guide geometry inside same-frame corrective painting masks."""
from pathlib import Path
import hashlib
import json
from PIL import Image

BASE=Path('authoring/characters/factory-v3/patch-0.0.1')
OUT=Path(__file__).parent
GUIDE=BASE/'research/tall-guide-proportion-pilot-20261027/mage130-colored-high1536-capture'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=json.loads((GUIDE/'manifest.json').read_text())
    records=[]
    for batch in range(4):
        dest=OUT/f'batch-{batch:02d}'
        recipe=json.loads((dest/'recipe.json').read_text())
        plate=Image.new('RGBA',(1536,1024))
        for slot,index in enumerate(recipe['indices']):
            source=BASE/'review/mage-female-sw-canonical-pilot-20261027/Master'/f'{index:03d}.png'
            mask_path=dest/'Masks'/f'{index:03d}-arm.png'
            guide_path=GUIDE/manifest['views']['SW']['frames'][index]['image']
            original=Image.open(source).convert('RGBA')
            mask=Image.open(mask_path).convert('L')
            guide=Image.open(guide_path).convert('RGBA').resize((768,768),Image.Resampling.LANCZOS)
            replacement=Image.new('RGBA',original.size,(255,0,255,255))
            replacement.alpha_composite(guide)
            original.paste(replacement,(0,0),mask)
            plate.paste(original.crop((224,224,576,576)).resize((512,512),Image.Resampling.LANCZOS),((slot%3)*512,(slot//3)*512))
            records.append({'index':index,'master_sha256':sha(source),'mask_sha256':sha(mask_path),'guide_sha256':sha(guide_path)})
        plate.save(dest/'hybrid.png')
        display=Image.new('RGBA',plate.size,'#ddd');display.alpha_composite(plate)
        display.convert('RGB').save(dest/'hybrid-gray.jpg',quality=97)
    (OUT/'hybrid-reference-proof.json').write_text(json.dumps({'status':'GUIDE_PAINTOVER_REFERENCES_ONLY','source_guide_manifest_sha256':sha(GUIDE/'manifest.json'),'viewport':[224,224,576,576],'all_frames_share_camera_and_viewport':True,'no_per_frame_fit':True,'inputs':records,'plate_sha256':{str(i):sha(OUT/f'batch-{i:02d}'/'hybrid.png')for i in range(4)},'runtime_admitted':False},indent=2)+'\n')

if __name__=='__main__':
    main()
