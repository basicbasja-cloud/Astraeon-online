"""Content-addressed visible-cutout storage with explicit fitting compatibility.

Sharing file bytes is separate from permission to swap a part into another pose.
No missing part is synthesized, and no hidden anatomy is claimed.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/cutout-store'
ROLES={'HeadHair','BodyCostume','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront','BackAccessory','Headgear','WeaponBack'}
REQUIRED={'HeadHair','BodyCostume','Weapon'}


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def register(image_path,metadata,index=None):
    if metadata.get('role')not in ROLES:raise ValueError('Unknown cutout role')
    for field in ['fit_id','pose_id','camera_id','root','source_reference']:
        if field not in metadata:raise ValueError('Missing compatibility field '+field)
    image=Image.open(image_path)
    canvas=metadata.get('canvas',[512,512])
    if list(image.size)!=canvas or image.mode!='RGBA'or canvas not in [[512,512],[768,768]]:raise ValueError('Cutouts must match an explicit full canonical 512px or 768px RGBA canvas')
    if metadata['role']in REQUIRED and not image.getbbox()and not metadata.get('occlusion_reason'):raise ValueError('Required cutout is empty without a recorded visibility reason')
    pixels=np.asarray(image).copy();pixels[pixels[:,:,3]==0]=0
    pixel_hash=hashlib.sha256(pixels.tobytes()).hexdigest();key=hashlib.sha256(canonical({'pixels':pixel_hash,'compatibility':metadata})).hexdigest()
    folder=STORE/'objects';folder.mkdir(parents=True,exist_ok=True);target=folder/(pixel_hash+'.png')
    if target.is_symlink():raise ValueError('Stored cutout object must not be a symlink')
    if target.exists():
        # A filename alone does not prove that a shared object is intact.
        # Reject damage before publishing any binding to it.
        try:
            with Image.open(target) as existing:
                if existing.mode!='RGBA' or existing.size!=image.size:raise ValueError('Stored cutout object has invalid format or dimensions')
                stored=np.asarray(existing).copy()
        except (OSError,ValueError) as exc:raise ValueError('Stored cutout object is unreadable or invalid') from exc
        stored[stored[:,:,3]==0]=0
        if hashlib.sha256(stored.tobytes()).hexdigest()!=pixel_hash:raise ValueError('Stored cutout object pixels changed')
    else:Image.fromarray(pixels).save(target)
    index_path=STORE/'index.json';owned=index is None
    if owned:index=json.loads(index_path.read_text())if index_path.exists()else{'version':1,'assets':{},'objects':{}}
    index['assets'][key]={'object':pixel_hash,**metadata};index['objects'][pixel_hash]={'file':str(target.relative_to(ROOT)),'rgba_sha256':pixel_hash,'canvas':list(image.size)}
    if owned:save_index(index)
    return key


def save_index(index):
    STORE.mkdir(parents=True,exist_ok=True);path=STORE/'index.json';temporary=STORE/'index.json.tmp';temporary.write_text(json.dumps(index,indent=2)+'\n');temporary.replace(path)


def resolve(asset_id,request):
    index=json.loads((STORE/'index.json').read_text());asset=index['assets'][asset_id]
    for field in ['role','fit_id','pose_id','camera_id','root']+(['canvas']if'canvas'in asset else[]):
        if request.get(field)!=asset[field]:raise ValueError('Incompatible cutout '+field)
    path=ROOT/index['objects'][asset['object']]['file'];pixels=np.array(Image.open(path).convert('RGBA'));pixels[pixels[:,:,3]==0]=0
    if hashlib.sha256(pixels.tobytes()).hexdigest()!=asset['object']:raise ValueError('Stored pixels changed')
    return path


def import_frame(master_path,labels_path,part_paths):
    """Validate an artist's same-frame parts before storage (no warping)."""
    master=Image.open(master_path).convert('RGBA')
    if master.size not in [(512,512),(768,768)]:raise ValueError('Master is not on a supported canonical canvas')
    # IDs 1..6 retain their legacy meanings; optional 7 is the rear weapon pass.
    labels=Image.open(labels_path)
    if labels.size!=master.size or labels.mode not in ['L','P']:raise ValueError('Expected a same-frame integer label map')
    a=np.asarray(master);ids=np.asarray(labels);visible=a[:,:,3]>0
    allowed=[1,2,3,4,5,6]+([7]if 'WeaponBack'in part_paths else [])
    if np.any(visible&~np.isin(ids,allowed)):raise ValueError('Visible master pixels lack semantic labels')
    masks={role:ids==i for i,role in enumerate(['BodyCostume','HeadHair','Weapon','BackAccessory','Headgear','WeaponHandOccluder'],1)}
    if 'WeaponBack'in part_paths:masks['WeaponBack']=ids==7
    merged=np.zeros_like(a)
    for role,mask in masks.items():
        pixels=np.zeros_like(a);pixels[mask]=a[mask];image=Image.fromarray(pixels);path=part_paths[role];path.parent.mkdir(parents=True,exist_ok=True);image.save(path);merged[mask]=pixels[mask]
    if not np.array_equal(merged[visible],a[visible]):raise ValueError('Visible recomposition mismatch')
    return {'visible_recomposition_mismatches':0,'hidden_surfaces_authored':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--image',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True);a=p.parse_args();print(register(a.image,json.loads(a.metadata.read_text())))
