"""Shared-row packing and bound independent grip-axis observations for a pilot."""
import json,hashlib,shutil,base64,math,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/combat-gait-study-v23'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def main():
    raw=OUT/'raw';raw.mkdir(exist_ok=True)
    for name,file in [('attack-gold.png','exec-c1457684-c959-433b-9a07-6cf82a4c07c1.png'),('attack-silver.png','exec-c592907c-aff9-4617-bde1-5a2ac939de5e.png')]:shutil.copyfile(Path('/workspace/generated_images')/file,raw/name)
    im=Image.open(raw/'attack-silver.png').convert('RGBA');assert im.width==im.height and im.width%2==0
    coordinate_scale=im.width/1280;cell_size=im.width//2
    # Correct a measured whole-row layout shift, not independent per-pose matching.
    scale=.75/coordinate_scale;translations=[[16,3.75],[16,52.5]];frames=[];directory=OUT/'attack/frames';directory.mkdir(parents=True,exist_ok=True)
    points=[{'palm':[239,139],'hilt':[239,139],'tip':[416,25],'wrist':[241,175],'knuckles':[236,140]},
            {'palm':[124,224],'hilt':[124,224],'tip':[182,35],'wrist':[150,252],'knuckles':[122,220]},
            {'palm':[225,297],'hilt':[225,297],'tip':[49,287],'wrist':[252,279],'knuckles':[222,297]},
            {'palm':[238,384],'hilt':[238,384],'tip':[117,525],'wrist':[248,350],'knuckles':[235,385]}]
    source=json.loads((OUT/'source/flare-swing/source-motion.json').read_text());tip_index=32
    for i in range(4):
        cell=im.crop((i%2*cell_size,i//2*cell_size,i%2*cell_size+cell_size,i//2*cell_size+cell_size));dx,dy=translations[i//2]
        original_alpha=np.array(cell.getchannel('A'))
        if any((original_alpha[edge]>1).any() for edge in [0,-1]):raise ValueError('Cell foreground touches row border')
        result=cell.transform((512,512),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BICUBIC)
        p=directory/f'{i:02}.png';result.save(p)
        f=source['frames'][i];xyz=np.array(f['weapon_vertices_world']);xy=np.array(f['weapon_vertices_px'])[:,:2];projection=np.linalg.lstsq(np.column_stack([xyz,np.ones(len(xyz))]),xy,rcond=None)[0]
        grip=np.r_[np.array(f['weapon_matrix_world'])[:3,3],1]@projection;tip=xy[tip_index]
        hand=np.subtract(f['joints_px']['Hand.Right']['tail'][:2],f['joints_px']['Hand.Right']['head'][:2]);blade=tip-grip
        angle=lambda a:math.degrees(math.atan2(a[1],a[0]));relative=(angle(blade)-angle(hand)+180)%360-180
        transformed={k:[v[0]*coordinate_scale*scale+dx,v[1]*coordinate_scale*scale+dy] for k,v in points[i].items()}
        frames.append({'time_ms':i*100,'duration_ms':100,'image':bind(p),'source_image':bind(OUT/'source/flare-swing'/f'{i:02}.png'),
            'visible_points':transformed,'uncertainty_px':5,'angle_uncertainty_deg':15,'reference_relative_blade_angle_deg':relative,
            'right_hand_identity_reviewed':False,'palm_hilt_same_feature_calibration':True,'scope':'Manual visible grip-axis estimates; shared palm/handle point is calibration, not independent zero-gap proof. Owner/palm surfaces and finger wrapping need independent review. No painted 3D transforms recovered.'})
    case={'schema':'motion-mechanics-v1','action':'attack','bindings':[bind(raw/'attack-silver.png'),bind(OUT/'source/flare-swing/source-motion.json')],
        'angle_tolerance_deg':25,'grip_tolerance_px':8,'frames':frames,'user_status':'REVIEW_REQUIRED'}
    dump(OUT/'evidence/painted-attack-case.json',case)
    script=ROOT/'skills/modular-eight-direction-sprites/scripts/motion-mechanics.py';spec=importlib.util.spec_from_file_location('mechanics',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    dump(OUT/'evidence/painted-attack-report.json',m.audit(case,ROOT))
    dump(OUT/'evidence/attack-packing.json',{'raw':bind(raw/'attack-silver.png'),'global_scale':scale,'shared_row_translations':translations,'observed_coordinate_canvas':[1280,1280],'observations_to_actual_raw_scale':coordinate_scale,
        'calibration':'Supporting-boot row origins chosen from first key of each row; excludes them from independent floor validation. Neither pose-by-pose fitting nor warp.',
        'source_frame_map':[13,14,15,16],'durations_ms':[100]*4,'complete_painted_parts':False})
    ims=[Image.open(directory/f'{i:02}.png').convert('RGBA') for i in range(4)]
    ims[0].save(OUT/'attack/pilot.png',save_all=True,append_images=ims[1:],duration=[100]*4,disposal=0,blend=0)
    rgb=[]
    for f in ims:
        background=Image.new('RGB',f.size,'#272727');background.paste(f,(0,0),f);rgb.append(background)
    rgb[0].save(OUT/'attack/pilot.gif',save_all=True,append_images=rgb[1:],duration=[100]*4,disposal=2)
    board=Image.new('RGB',(2048,552),'#272727');draw=ImageDraw.Draw(board)
    annotated=Image.new('RGB',(2048,552),'#272727');ad=ImageDraw.Draw(annotated)
    for i,f in enumerate(ims):
        board.paste(f,(i*512,40),f);annotated.paste(f,(i*512,40),f);draw.text((i*512+10,10),f'Own pilot key {i+1} / {100*i}ms / REVIEW REQUIRED',fill='white')
        for name,pt in frames[i]['visible_points'].items():
            x,y=pt;x+=i*512;y+=40;ad.ellipse((x-3,y-3,x+3,y+3),fill='#00dbff');ad.text((x+4,y+2),name,fill='white')
    board.save(OUT/'attack/four-key-review.png');annotated.save(OUT/'attack/observed-grip-review.png')
    # The appearance edit is not an exact lock; quantify alpha changes rather than claim pose identity.
    a=np.array(Image.open(raw/'attack-gold.png').getchannel('A'))>128;b=np.array(im.getchannel('A'))>128
    dump(OUT/'evidence/material-edit-difference.json',{'before':bind(raw/'attack-gold.png'),'after':bind(raw/'attack-silver.png'),
        'foreground_mask_iou':float((a&b).sum()/(a|b).sum()),'mask_changed_pixels':int((a!=b).sum()),'exact_pixels_preserved':False,
        'scope':'Generator material correction also changes pixels/contours; fresh selected-bank review required.'})
    print('ATTACK_PILOT_READY',m.audit(case,ROOT)['metrics'])
if __name__=='__main__':main()
