"""Prepare view-specific design references; these are never action pose evidence."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identities',type=Path,default=Path('authoring/characters/factory-v3/patch-0.0.1/identities'));a=p.parse_args();records=[]
    for source in sorted(a.identities.glob('*-turnaround.png')):
        im=Image.open(source).convert('RGBA');name=source.stem.removesuffix('-turnaround');target=a.identities/'views'/name;target.mkdir(parents=True,exist_ok=True);views={}
        for i,direction in enumerate(DIRECTIONS):
            box=tuple(round(v) for v in ((i%4)*im.width/4,(i//4)*im.height/2,(i%4+1)*im.width/4,(i//4+1)*im.height/2));cell=im.crop(box);cell.save(target/f'{direction}.png')
            # The same fractional design crop across all views excludes most posed limbs.
            upper=cell.crop(tuple(round(v)for v in (cell.width*.30,0,cell.width*.70,cell.height*.33)));upper.save(target/f'{direction}-head-upper.png')
            views[direction]={'cell':str((target/f'{direction}.png').relative_to(a.identities)),'head_upper':str((target/f'{direction}-head-upper.png').relative_to(a.identities)),'source_box':box}
        record={'identity':name,'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'direction_order':DIRECTIONS,'head_crop_revision':2,'head_crop_fractions':[.30,0,.70,.33],'status':'IDENTITY_STUDY_DESIGN_REFERENCE_REQUIRES_VIEW_INSPECTION','authority':'Appearance and facing reference only; current Blender action owns geometry and timing','generic_front_portrait_for_rear_views':False,'views':views};(target/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
    (a.identities/'direction-reference-index.json').write_text(json.dumps({'characters':records,'action_coverage_claimed':False},indent=2)+'\n');print(json.dumps({'identities':len(records),'view_reference_pairs':len(records)*8}))

if __name__=='__main__':main()
