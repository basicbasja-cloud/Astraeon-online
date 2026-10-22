"""Rigidly reuse an authored visible accessory; body pixels are never warped."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
from build_fixed_grid_sequence_review import frames_from_sheet,gif


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sheet',type=Path,required=True);p.add_argument('--annotations',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    annotation=json.loads(a.annotations.read_text());size=768;scale=size/annotation['canvas'];frames,_,_=frames_from_sheet(a.sheet,a.output/'original')
    donor=frames[annotation['donor_frame']];mask=Image.new('L',(size,size));ImageDraw.Draw(mask).polygon([(round(x*scale),round(y*scale)) for x,y in annotation['donor_polygon']],fill=255)
    pixels=np.array(donor);pixels[np.array(mask)==0]=0;accessory=Image.fromarray(pixels);accessory.save(a.output/'BackAccessory-donor.png');records=[];composed=[];contact=Image.new('RGBA',(1536,1536),'#e8e8e8')
    for i,base in enumerate(frames):
        item=next((r for r in annotation['placements'] if r['index']==i),None);part=Image.new('RGBA',(size,size));occluder=Image.new('RGBA',(size,size));merged=base.copy()
        if item:
            dx,dy=[round(v*scale) for v in item['translation']];rotated=accessory.rotate(item.get('rotation',0),Image.Resampling.BICUBIC,center=tuple(v*scale for v in annotation['donor_pivot']));part.alpha_composite(rotated,(dx,dy))
            if item.get('front_occlusion_polygon'):
                front=Image.new('L',(size,size));ImageDraw.Draw(front).polygon([(round(x*scale),round(y*scale)) for x,y in item['front_occlusion_polygon']],fill=255);array=np.array(base);array[np.array(front)==0]=0;occluder=Image.fromarray(array)
            merged.alpha_composite(part);merged.alpha_composite(occluder)
        for role,image in [('Master',merged),('BodyCostume',base),('BackAccessory',part),('BackAccessoryFrontOccluder',occluder)]:
            d=a.output/role;d.mkdir(exist_ok=True);image.save(d/f'{i:03d}.png')
        composed.append(merged);contact.alpha_composite(merged.resize((384,384)),((i%4)*384,(i//4)*384));records.append({'index':i,'placement':item,'body_pixels_warped':False})
    contact.save(a.output/'contact.png');gif(composed,a.output/'normal.gif',[90]*16);gif(composed,a.output/'slow.gif',[270]*16)
    (a.output/'receipt.json').write_text(json.dumps({'status':'VISIBLE_ACCESSORY_REUSE_STUDY_REQUIRES_OCCLUSION_REVIEW','donor_frame':annotation['donor_frame'],'hidden_accessory_surfaces_generated':False,'body_pixels_warped':False,'other_body_pixels_preserved':True,'not_a_complete_cutout_package':True,'source_pose_registered':False,'owner_approved':False,'runtime_admitted':False,'frames':records},indent=2)+'\n')

if __name__=='__main__':main()
