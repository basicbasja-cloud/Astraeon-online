"""Evaluate a native Mage casting action with independently articulated 2D arms.

Diagnostic only: recorded source joints drive each arm and palm plane, while a
small shared torso field preserves the painted clothing. No frame generation.
Joint caps, depth ordering and perspective deformation need visual acceptance.
"""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage

import derive_bounded_hold_parts as motion
from build_occluded_underlays import composite,sha


def remove_distant_faint_alpha(image):
    pixels=np.array(image.convert('RGBA'));alpha=pixels[:,:,3]
    strong=alpha>64
    if not strong.any():raise ValueError('No meaningful source illustration')
    labels,_=ndimage.label(strong,structure=np.ones((3,3)))
    counts=np.bincount(labels.ravel());counts[0]=0
    main=labels==int(counts.argmax())
    distance=ndimage.distance_transform_edt(~main)
    removed=(alpha>0)&(alpha<=64)&(distance>3)
    pixels[removed]=0
    return Image.fromarray(pixels),int(removed.sum())


def segment_matrix(source,target):
    source=np.asarray(source,float);target=np.asarray(target,float)
    u=source[1]-source[0];v=target[1]-target[0]
    a,b=np.linalg.norm(u),np.linalg.norm(v)
    if min(a,b)<2:raise ValueError('Projected limb is too short for segment transport')
    first=np.column_stack([u/a,[-u[1]/a,u[0]/a]])
    second=np.column_stack([v/b,[-v[1]/b,v[0]/b]])
    linear=second@np.diag([b/a,1.])@first.T
    return np.column_stack([linear,target[0]-linear@source[0]])


def palm_matrix(source,target):
    source=np.asarray(source,float);target=np.asarray(target,float)
    a=np.column_stack([source[1]-source[0],source[2]-source[0]])
    b=np.column_stack([target[1]-target[0],target[2]-target[0]])
    if abs(np.linalg.det(a))<8 or abs(np.linalg.det(b))<8 or np.linalg.det(a)*np.linalg.det(b)<=0:
        raise ValueError('Palm plane is degenerate or changes visible side')
    linear=b@np.linalg.inv(a)
    return np.column_stack([linear,target[0]-linear@source[0]])


def rigid_head_matrix(source,target):
    source=np.asarray(source,float);target=np.asarray(target,float)
    u=source[1]-source[0];v=target[1]-target[0]
    if min(np.linalg.norm(u),np.linalg.norm(v))<2:raise ValueError('Projected head axis is degenerate')
    u=u/np.linalg.norm(u);v=v/np.linalg.norm(v)
    a=np.column_stack([u,[-u[1],u[0]]]);b=np.column_stack([v,[-v[1],v[0]]])
    linear=b@a.T
    return np.column_stack([linear,target[1]-linear@source[1]])


def warp_affine(image,matrix,xx,yy):
    inverse=np.linalg.inv(matrix[:,:2]);offset=matrix[:,2]
    sx=inverse[0,0]*(xx-offset[0])+inverse[0,1]*(yy-offset[1])
    sy=inverse[1,0]*(xx-offset[0])+inverse[1,1]*(yy-offset[1])
    return motion.resample_rgba(image,sy,sx)


def make_parts(body,recipe,landmarks):
    pixels=np.array(body);yy,xx=np.indices(pixels.shape[:2]);points=np.stack([xx,yy],axis=-1)
    masks={};used=np.zeros(pixels.shape[:2],bool)
    for side in ['L','R']:
        canvas=Image.new('1',body.size);ImageDraw.Draw(canvas).polygon(recipe['arm_polygons'][side],fill=1)
        arm=np.array(canvas)&(pixels[:,:,3]>0)
        if recipe.get('protect_collar',False):
            rgb=pixels[:,:,:3].astype(float)
            cream=(rgb[:,:,0]>140)&(rgb[:,:,1]>120)&(rgb[:,:,2]>90)&(xx>700)&(yy<775)
            arm &= ~cream
        shoulder,elbow,wrist=[np.asarray(recipe['art_joints'].get(k+'.'+side,landmarks[k+'.'+side]))for k in ['UpperArm','Forearm','Hand']]
        axis=(wrist-elbow)/np.linalg.norm(wrist-elbow)
        hand=arm&(((points-wrist)@axis)>-4)if side=='L'else np.zeros_like(arm)
        # Split sleeve at the elbow plane; both independently painted pieces
        # receive a small recorded underlap from the same original opaque art.
        axis=(elbow-shoulder)/np.linalg.norm(elbow-shoulder)
        fore=arm&~hand&(((points-elbow)@axis)>0)
        upper=arm&~hand&~fore
        masks['UpperArm'+side]=upper;masks['Forearm'+side]=fore
        if side=='L':masks['HandL']=hand
        used|=arm
    masks['Torso']=(pixels[:,:,3]>0)&~used
    radius=recipe.get('shoulder_caps_radius_px',0)
    for side in ['L','R']:
        center=np.asarray(recipe['art_joints']['UpperArm.'+side])
        masks['Torso'] |= ((xx-center[0])**2+(yy-center[1])**2<=radius**2)&(pixels[:,:,3]==255)
    parts={}
    for name,mask in masks.items():
        expanded=mask|(ndimage.binary_dilation(mask,iterations=recipe['joint_underlap_px'])&(pixels[:,:,3]==255))
        values=np.zeros_like(pixels);values[expanded]=pixels[expanded]
        parts[name]=Image.fromarray(values)
    return parts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['template','base-guide','target-guide','recipe','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--indices',type=int,nargs='+',help='Diagnostic key poses only; never packaged as full coverage')
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh segmented action study')
    implementation=sha(__file__)
    recipe=json.loads(args.recipe.read_text());direction=recipe['direction']
    base_capture=json.loads((args.base_guide/'pilot-receipt.json').read_text())
    capture=json.loads((args.target_guide/'pilot-receipt.json').read_text())
    for key in ['rig_sha256','actor_scale','leg_scale','weapon']:
        if base_capture[key]!=capture[key]:raise ValueError('Incompatible native base and target: '+key)
    base_view=base_capture['views'][direction];view=capture['views'][direction]
    if base_view['camera']!=view['camera']:raise ValueError('Native camera changed')
    base=base_view['frames'][0];base_points=base['landmarks']
    if (args.template/'kit.json').is_file():
        kit=json.loads((args.template/'kit.json').read_text())
        if kit['status']!='INDEPENDENT_PAINTED_ARM_KIT_NOT_ADMITTED' or kit['direction']!=direction or kit['canonical_guide_receipt_sha256']!=sha(args.base_guide/'pilot-receipt.json'):
            raise ValueError('Independent kit differs from the source camera/rest pose')
        source={name:Image.open(args.template/name/'000.png').convert('RGBA')for name in kit['parts_sha256']}
        for name,digest in kit['parts_sha256'].items():
            if sha(args.template/name/'000.png')!=digest:raise ValueError('Independent painted part changed')
        inputs=[args.template/'kit.json',*[args.template/name/'000.png'for name in source]]
        noise={};input_kind='independently-painted-complete-parts'
    else:
        body,body_noise=remove_distant_faint_alpha(Image.open(args.template/'BodyCostume/000.png'))
        source=make_parts(body,recipe,base_points)
        source['HeadHair']=Image.open(args.template/'HeadHair/000.png').convert('RGBA')
        source['HandR']=Image.open(args.template/'WeaponHandOccluder/000.png').convert('RGBA')
        source['Weapon']=Image.open(args.template/'WeaponComplete-reference.png').convert('RGBA')
        noise={'BodyCostume':body_noise}
        for name in ['HeadHair','HandR','Weapon']:
            source[name],noise[name]=remove_distant_faint_alpha(source[name])
        inputs=[args.template/'receipt.json',args.template/'WeaponComplete-reference.png',*[args.template/r/'000.png'for r in ['BodyCostume','HeadHair','WeaponHandOccluder']]]
        input_kind='legacy-visible-cutout-split'
    inputs += [args.recipe,args.base_guide/'pilot-receipt.json',args.target_guide/'pilot-receipt.json']
    frozen={str(p):sha(p)for p in inputs}
    keys=['Hips','Chest','Head','UpperArm.L','UpperArm.R','Foot.L','Foot.R','Toe.L','Toe.R']
    boundary=np.array([[0,0],[768,0],[1536,0],[0,768],[1536,768],[0,1536],[768,1536],[1536,1536]])
    torso_source=np.vstack([[base_points[k]for k in keys],boundary])
    yy,xx=np.mgrid[:motion.SIZE,:motion.SIZE].astype(np.float32)
    args.output.mkdir(parents=True);records=[];preview=[]
    order=recipe.get('render_order',['Weapon','Torso','UpperArmR','ForearmR','HandR','HeadHair','UpperArmL','ForearmL','HandL'])
    if set(order)!=set(source)or len(order)!=len(set(order)):raise ValueError('Painted primitive order differs')
    selected=view['frames']
    if args.indices is not None:
        if args.indices!=sorted(set(args.indices))or any(i<0 or i>=len(selected)for i in args.indices):raise ValueError('Expected ordered unique native pose indices')
        selected=[selected[i]for i in args.indices]
    for row in selected:
        index=row['index'];points=row['landmarks']
        field,metrics,_=motion.inverse_field(torso_source,np.vstack([[points[k]for k in keys],boundary]))
        if metrics['minimum_jacobian']<.65 or metrics['maximum_jacobian']>1.5 or metrics['maximum_inverse_displacement_px']>64:
            raise ValueError('Torso exceeds bounded casting transport')
        dx,dy=[ndimage.map_coordinates(field[:,:,i],[((yy+.5)/motion.SPACING),((xx+.5)/motion.SPACING)],order=1,prefilter=False)for i in range(2)]
        derived={'Torso':motion.resample_rgba(source['Torso'],yy+dy,xx+dx)}
        transforms={}
        head_policy=recipe.get('head_transport','torso-field')
        if head_policy=='rigid-neck-axis':
            matrix=rigid_head_matrix([base_points[k]for k in ['Neck','Head']],[points[k]for k in ['Neck','Head']])
            derived['HeadHair']=warp_affine(source['HeadHair'],matrix,xx,yy);transforms['HeadHair']=matrix.tolist()
        elif head_policy=='torso-field':derived['HeadHair']=motion.resample_rgba(source['HeadHair'],yy+dy,xx+dx)
        else:raise ValueError('Unknown head transport policy')
        for side in ['L','R']:
            for name,joints in [('UpperArm',['UpperArm','Forearm']),('Forearm',['Forearm','Hand']),('Hand',['Hand','Index1','Pinky1'])]:
                wrist_delta=np.asarray(recipe['art_joints']['Hand.'+side])-base_points['Hand.'+side]
                a=[np.asarray(recipe['art_joints'].get(k+'.'+side,np.asarray(base_points[k+'.'+side])+wrist_delta))for k in joints]
                b=[np.asarray(points[k+'.'+side])+start-base_points[k+'.'+side]for k,start in zip(joints,a)]
                matrix=palm_matrix(a,b)if name=='Hand'else segment_matrix(a,b)
                part=name+side;derived[part]=warp_affine(source[part],matrix,xx,yy);transforms[part]=matrix.tolist()
        a=[motion.project(base[k],base_view['camera'])for k in ['grip_world','staff_tip_world']]
        b=[motion.project(row[k],view['camera'])for k in ['grip_world','staff_tip_world']]
        matrix=segment_matrix(a,b);derived['Weapon']=warp_affine(source['Weapon'],matrix,xx,yy);transforms['Weapon']=matrix.tolist()
        master=composite([derived[k]for k in order]);hashes={}
        for role,image in {**derived,'Master':master}.items():
            folder=args.output/role;folder.mkdir(exist_ok=True);path=folder/f'{index:03d}.png';image.save(path);hashes[role]=sha(path)
        records.append({'index':index,'source_action':row['source_action'],'source_frame':row['source_frame'],'transforms':transforms,'torso_deformation':metrics,'sha256':hashes})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master);preview.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
        print('SEGMENTED_NATIVE_ACTION',index,flush=True)
    gif_options={'loop':0}if args.indices is None else {}
    preview[0].save(args.output/'segmented-casting-study.gif',save_all=True,append_images=preview[1:],duration=80,**gif_options)
    if sha(__file__)!=implementation or any(sha(p)!=v for p,v in frozen.items()):raise ValueError('Segmented action input changed during capture')
    receipt={'status':'SEGMENTED_CASTING_DIAGNOSTIC_NOT_ADMITTED','input_kind':input_kind,'direction':direction,'render_order':order,'input_sha256':frozen,'recipe_sha256':sha(args.recipe),'implementation_sha256':implementation,'frames':records,'distant_faint_alpha_removed':noise,'partial_selection':args.indices is not None,'per_frame_generation':False,'camera_modified':False,'joint_caps_approved':False,'occlusion_approved':False,'runtime_admitted':False}
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    replay=args.output/'replay';replay.mkdir()
    for name in ['render_segmented_mage_action.py','derive_bounded_hold_parts.py','build_occluded_underlays.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)


if __name__=='__main__':main()
