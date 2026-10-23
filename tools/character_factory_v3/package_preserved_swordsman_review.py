"""Pack actual retained-art cutouts for the real runtime draw API review.

This exports bounded review samples, not a character definition with invented
Idle/Walk/other clips. Pixel-object reuse does not imply pose compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from pack_patch001_character import atlas_pages, trimmed_source

ROOT=Path(__file__).resolve().parents[2]
ORDER=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon']


def package(source,output):
    source=source.resolve();output=output.resolve()
    if output.exists():raise ValueError('Choose a fresh output folder')
    receipt=json.loads((source/'receipt.json').read_text())
    output.mkdir(parents=True);images=[];objects={};frames=[]
    for view in receipt['frames']:
        action=view['action'];direction=view['direction']
        for record in view['frames']:
            i=record['index'];parts=[]
            for role in ORDER:
                path=source/action/direction/role/f'{i:03d}.png'
                im,offset=trimmed_source(Image.open(path).convert('RGBA'))
                key=hashlib.sha256(im.tobytes()+str(im.size).encode()).hexdigest()
                if key not in objects:objects[key]=len(images);images.append(im)
                parts.append({'role':role,'object_index':objects[key],'offset':offset,
                              'source_file':str(path.relative_to(ROOT)),
                              'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            frames.append({'action':action,'direction':direction,'index':i,'source_frame':record['source_frame'],
                           'source_action':record['source_action'],'parts':parts,
                           'master_file':str((source/action/direction/'Master'/f'{i:03d}.png').relative_to(ROOT))})
    placements={};atlases={}
    for number,(page,slots)in enumerate(atlas_pages(images,limit=2048)):
        name=f'page-{number:02d}';path=output/(name+'.png');page.save(path)
        atlases[name]={'file':path.name,'width':page.width,'height':page.height,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        for index,rect in slots:placements[index]=(name,rect)
    for frame in frames:
        for part in frame['parts']:
            index=part.pop('object_index');part['atlasId'],part['rect']=placements[index]
    report={'status':'ACTUAL_RETAINED_ART_RUNTIME_DRAW_REVIEW_NOT_FULL_CHARACTER',
            'canvas':{'frameWidth':240,'frameHeight':240,'compositionWidth':768,'compositionHeight':768,
                      'rootAnchorX':120,'rootAnchorY':172},
            'frames':frames,'atlases':atlases,'draw_order':ORDER,
            'unique_pixel_objects':len(objects),'part_bindings':sum(len(f['parts'])for f in frames),
            'source_receipt':str((source/'receipt.json').relative_to(ROOT)),
            'same_pixels_reused_only':True,'pose_compatibility_implied_by_pixel_reuse':False,
            'playable_character':False,'runtime_admitted':False}
    (output/'samples.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=package(a.source,a.output)
    print(json.dumps({k:r[k]for k in ['unique_pixel_objects','part_bindings','playable_character']}))
