"""Prepare real rig pose controls and fixed-canvas masters for a precise editor.

This makes no image-service calls and admits no art. Missing facial landmarks
remain absent; bone origins are never relabeled as sole-contact measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
from scipy.spatial.transform import Rotation
from normalize_fixed_viewport_batch import normalize_batch
from qualify_cropped_paint_resolution import qualify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
# COCO18: no native nose/eye/ear points exist in this source rig.
BONES={1:'neck_01',2:'upperarm_r',3:'lowerarm_r',4:'hand_r',5:'upperarm_l',6:'lowerarm_l',7:'hand_l',8:'thigh_r',9:'calf_r',10:'foot_r',11:'thigh_l',12:'calf_l',13:'foot_l'}
LIMBS=[(1,2),(2,3),(3,4),(1,5),(5,6),(6,7),(1,8),(8,9),(9,10),(1,11),(11,12),(12,13)]
COLORS=['#ff0000','#ff8000','#ffff00','#80ff00','#00ff00','#00ff80','#00ffff','#0080ff','#0000ff','#8000ff','#ff00ff','#ff0080']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def project(point,camera,size=768):
    rotation=Rotation.from_euler('xyz',camera['rotation']).as_matrix()
    local=rotation.T@(np.asarray(point)-np.asarray(camera['location']))
    return [(0.5+local[0]/camera['ortho_scale'])*size,(0.5-local[1]/camera['ortho_scale'])*size]


def build(output):
    if output.exists()or output.is_symlink():raise ValueError('Choose fresh handoff output')
    candidate=BASE/'painted-candidates/swordsman-hit-snapshot-wholesheet-20261102'
    guide=BASE/'guides/f21a6dab07976b27ec15'
    manifest=json.loads((candidate/'source-manifest.json').read_text())
    audit_path=BASE/'research/swordsman-hit-native-recovery-20261102/audit.json';audit=json.loads(audit_path.read_text())
    if sha(candidate/'source-manifest.json')!=audit['manifest_sha256']:raise ValueError('Source manifests disagree')
    recipe={'grid':[4,3],'source_size':[768,768],'viewport':[224,260,544,580],
        'source_pose_indices':list(range(12)),'frame_space':'canonical-authoring','canonical_root':[384,550.4]}
    with Image.open(candidate/'raw.png')as raw:
        qualification=qualify(list(raw.size),[4,3],[1536,1536],[448,520,1088,1160],[768,768])
        if qualification['requires_upsampling']:raise ValueError('Insufficient native crop detail')
        drafts,normalization=normalize_batch(raw,recipe)
    if normalization['production_blockers']:raise ValueError('Draft touches shared viewport edge')
    camera=manifest['views']['SW']['camera'];records=[];max_error=0
    inputs=[candidate/'raw.png',candidate/'source-manifest.json',audit_path,Path(__file__),
            Path(__file__).with_name('normalize_fixed_viewport_batch.py'),Path(__file__).with_name('qualify_cropped_paint_resolution.py')]
    for i,reference in enumerate(manifest['views']['SW']['frames']):
        source=guide/'SW'/f'{i:03d}.png';row=min(audit['frames'],key=lambda v:abs(v['source_frame']-reference['source_frame']))
        if abs(row['source_frame']-reference['source_frame'])>1e-6:raise ValueError('Missing exact native sample')
        world=row['world_bone_origins'];projected={name:project(point,camera)for name,point in world.items()}
        for name,point in reference['landmarks'].items():
            if name=='root':continue
            max_error=max(max_error,float(np.linalg.norm(np.asarray(point)/2-projected[name])))
        if max_error>1e-4:raise ValueError('Camera projection no longer matches the source guide')
        folder=output/f'{i:03d}';folder.mkdir(parents=True)
        drafts[i].save(folder/'draft.png')
        with Image.open(source)as image:
            source_image=image.convert('RGBA').resize((768,768),Image.Resampling.LANCZOS)
            source_image.save(folder/'source-guide.png')
        keypoints=[0.]*54;pose=Image.new('RGB',(768,768),'black');draw=ImageDraw.Draw(pose)
        for index,name in BONES.items():keypoints[index*3:index*3+3]=[*map(float,projected[name]),1.]
        for (left,right),color in zip(LIMBS,COLORS):
            a=tuple(keypoints[left*3:left*3+2]);b=tuple(keypoints[right*3:right*3+2]);draw.line([a,b],fill=color,width=4)
        for index in BONES:
            x,y=keypoints[index*3:index*3+2];draw.ellipse((x-3,y-3,x+3,y+3),fill='white')
        pose.save(folder/'body-pose.png')
        pose_json={'version':1.3,'canvas_width':768,'canvas_height':768,'people':[{'pose_keypoints_2d':keypoints,
            'face_keypoints_2d':[],'hand_left_keypoints_2d':[],'hand_right_keypoints_2d':[]}],
            'source':'Exact projected native rig joints, not detector predictions; confidence marks known source joints, including occluded ones.',
            'missing_landmarks':'Nose, eyes, ears and facial keypoints are unknown, zero confidence and not invented.'}
        (folder/'body-pose.json').write_text(json.dumps(pose_json,indent=2)+'\n')
        targets={name:[float(v/2)for v in p]for name,p in reference['weapon_guide'].items()}
        edges=Image.new('L',(768,768));drawing=ImageDraw.Draw(edges);drawing.line([tuple(targets['grip']),tuple(targets['tip'])],fill=255,width=2);edges.save(folder/'weapon-axis.png')
        mask=binary_dilation((np.asarray(drafts[i])[:,:,3]>0)|(np.asarray(source_image)[:,:,3]>0),iterations=8)
        Image.fromarray(mask.astype('uint8')*255).save(folder/'whole-master-edit-mask.png')
        target={'direction':'SW','index':i,'source_frame':reference['source_frame'],'source_action':reference['action'],
                'projected_rig_bone_origins_authoring_px':projected,'weapon_targets_authoring_px':targets,
                'sole_contacts_verified':False,'face_keypoints_inferred':False}
        (folder/'source-targets.json').write_text(json.dumps(target,indent=2)+'\n')
        inputs.append(source);records.append({'index':i,'source_frame':reference['source_frame'],'source_png_sha256':sha(source)})
    receipt={'status':'EDITOR_HANDOFF_NOT_PAINT_OR_CHARACTER_APPROVAL','frames':records,'resolution_qualification':qualification,
        'normalization':normalization,'max_projection_difference_authoring_px':max_error,
        'fixed_canvas':[768,768],'global_root':[384,550.4],'per_frame_bbox_or_limb_fit':False,
        'face_keypoints_inferred':False,'sole_contacts_approved':False,'runtime_admitted':False,
        'input_sha256':{str(p.relative_to(ROOT)):sha(p)for p in inputs},
        'output_sha256':{str(p.relative_to(output)):sha(p)for p in sorted(output.rglob('*'))if p.is_file()},
        'requirements':['Use actual pose conditioning, explicit edit mask and fixed output canvas.',
                        'Preserve original pixels outside the supplied whole-master mask.',
                        'Use the approved tall identity reference and preserve style and materials.',
                        'Verify anatomy, actual visible sole points, grip/tip, temporal consistency and hidden surfaces before admission.',
                        'Missing facial points must remain absent; edit-mask coverage does not imply a valid correction.']}
    (output/'handoff-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=build(args.output)
    print(json.dumps({'frames':len(result['frames']),'max_projection_error_authoring_px':result['max_projection_difference_authoring_px'],'files':len(result['output_sha256'])}))
