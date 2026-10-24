"""Seal recorded pose and visible-RGBA identities independently of PNG metadata.

A new seal requires the original byte-pinned manifest and declared PNGs. Later
captures may change packaging metadata only: every recorded pose/control,
relevant job field, camera and visible RGBA pixel must still match exactly.
This is source identity, never art, anatomy or runtime acceptance.
"""
import argparse,hashlib,io,json
from pathlib import Path
import numpy as np
from PIL import Image

ALGORITHM='recorded-geometry-and-visible-rgba-v1'
PIXEL_CACHE={}
DIRECTIONS={'S','SW','W','NW','N','NE','E','SE'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def reference_sidecar(artifact):return artifact.with_name(artifact.name+'.capture-reference.json')


def capture_identity(guide):
    path=guide/'manifest.json';raw=path.read_bytes();original_manifest=hashlib.sha256(raw).hexdigest();manifest=json.loads(raw);count=manifest['frame_count'];job=manifest['job']
    if type(count)is not int or count<1 or not isinstance(job.get('id'),str)or not job['id']:raise ValueError('Invalid capture identity')
    if not manifest['views']or set(manifest['views'])-DIRECTIONS:raise ValueError('Invalid source directions')
    snapshot={'algorithm':ALGORITHM,'job':{k:v for k,v in job.items()if k not in ['uses','directions']},'frame_count':count,'views':{}}
    for key in ['source_rig','guide_rig','retargeting','mirroring','root_policy']:
        if key in manifest:snapshot[key]=manifest[key]
    checks=[]
    for direction,view in sorted(manifest['views'].items()):
        if len(view['frames'])!=count:raise ValueError('Incomplete source pose records')
        frames=[]
        for i,record in enumerate(view['frames']):
            if record.get('image') not in [None,f'{direction}/{i:03d}.png']:raise ValueError('Noncanonical source image path')
            image=guide/direction/f'{i:03d}.png';data=image.read_bytes();file_sha=hashlib.sha256(data).hexdigest();checks.append((image,file_sha))
            if file_sha not in PIXEL_CACHE:
                im=Image.open(io.BytesIO(data))
                if im.mode!='RGBA' or im.width!=im.height or('resolution'in job and im.size!=(job['resolution'],job['resolution'])):raise ValueError('Source capture canvas/mode differs')
                pixels=np.array(im);pixels[pixels[:,:,3]==0]=0;PIXEL_CACHE[file_sha]={'size':tuple(im.size),'visible_rgba_sha256':hashlib.sha256(pixels.tobytes()).hexdigest()}
            cached=PIXEL_CACHE[file_sha]
            if 'resolution'in job and cached['size']!=(job['resolution'],job['resolution']):raise ValueError('Source capture canvas/mode differs')
            frames.append({'pose':{k:v for k,v in record.items()if k!='image'},'size':list(cached['size']),'visible_rgba_sha256':cached['visible_rgba_sha256']})
        snapshot['views'][direction]={'camera':view.get('camera'),'frames':frames}
    if sha(path)!=original_manifest or any(sha(path)!=expected for path,expected in checks):raise ValueError('Source capture changed while deriving identity')
    return {'identity_sha256':digest(snapshot),'snapshot':snapshot,'current_manifest_sha256':original_manifest}


def declared_image_bytes_match(artifact,guide,manifest):
    inputs=artifact.get('all_source_frame_inputs')
    if inputs is None:return None
    count=manifest['frame_count'];direction=artifact.get('direction')
    if direction not in manifest['views']or not isinstance(inputs,list)or len(inputs)!=count or any(type(r.get('index'))is not int for r in inputs)or {r.get('index')for r in inputs}!=set(range(count)):raise ValueError('Incomplete declared source PNG identity')
    return all(sha(guide/direction/f"{r['index']:03d}.png")==r.get('sha256')for r in inputs)


def verify_source_reference(artifact_path,guide):
    artifact=json.loads(artifact_path.read_text());manifest=json.loads((guide/'manifest.json').read_text());current_sha=sha(guide/'manifest.json')
    if artifact.get('guide_job')!=manifest['job']['id']:raise ValueError('Source guide identity differs')
    exact_manifest=artifact.get('guide_manifest_sha256')==current_sha;exact_images=declared_image_bytes_match(artifact,guide,manifest);sidecar=reference_sidecar(artifact_path)
    if sidecar.exists():
        seal=json.loads(sidecar.read_text())
        if seal.get('algorithm')!=ALGORITHM or seal.get('artifact_sha256')!=sha(artifact_path):raise ValueError('Sealed source artifact changed')
        if seal.get('original_raw_manifest_sha256')!=artifact.get('guide_manifest_sha256')or seal['snapshot']['job']['id']!=artifact['guide_job']:raise ValueError('Sealed source lineage differs')
        if digest(seal['snapshot'])!=seal.get('identity_sha256'):raise ValueError('Sealed source snapshot changed')
        current=capture_identity(guide)
        if current['identity_sha256']!=seal['identity_sha256']:raise ValueError('Source pose, implementation, camera or visible RGBA changed')
        mode='EXACT_DECLARED_REFERENCE_BYTES'if exact_manifest and exact_images is not False else'EXACT_POSE_AND_VISIBLE_RGBA'
        return {'mode':mode,'identity_sha256':current['identity_sha256'],'reference_sidecar_sha256':sha(sidecar),'current_manifest_sha256':current_sha,'original_manifest_sha256':artifact['guide_manifest_sha256'],'declared_png_bytes_match':exact_images,'art_approval_implied':False}
    if not exact_manifest or exact_images is False:raise ValueError('Source reference changed and has no pre-existing sealed identity')
    return {'mode':'EXACT_DECLARED_REFERENCE_BYTES','identity_sha256':None,'current_manifest_sha256':current_sha,'original_manifest_sha256':artifact['guide_manifest_sha256'],'declared_png_bytes_match':exact_images,'art_approval_implied':False}


def seal_source_reference(artifact_path,guide):
    sidecar=reference_sidecar(artifact_path)
    if sidecar.exists():return verify_source_reference(artifact_path,guide)
    artifact_sha=sha(artifact_path);artifact=json.loads(artifact_path.read_text());manifest=json.loads((guide/'manifest.json').read_text())
    if artifact.get('guide_job')!=manifest['job']['id']or artifact.get('guide_manifest_sha256')!=sha(guide/'manifest.json'):raise ValueError('Only the original byte-pinned source reference may be sealed')
    exact=declared_image_bytes_match(artifact,guide,manifest)
    if exact is False:raise ValueError('Original declared source PNG bytes differ; cannot create a retrospective seal')
    identity=capture_identity(guide)
    if sha(artifact_path)!=artifact_sha:raise ValueError('Artifact changed while sealing source reference')
    seal={'algorithm':ALGORITHM,'artifact_sha256':artifact_sha,'original_raw_manifest_sha256':artifact['guide_manifest_sha256'],'identity_sha256':identity['identity_sha256'],'snapshot':identity['snapshot'],'implementation_sha256':sha(Path(__file__)),'invisible_rgb_at_zero_alpha_ignored':True,'visible_rgba_or_recorded_pose_changes_allowed':False,'art_approval_implied':False}
    temp=sidecar.with_suffix(sidecar.suffix+'.tmp');temp.write_text(json.dumps(seal,indent=2)+'\n');temp.replace(sidecar);return verify_source_reference(artifact_path,guide)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['seal','verify']);p.add_argument('--guide',type=Path,required=True);p.add_argument('--artifact',type=Path,action='append',required=True);a=p.parse_args()
    for artifact in a.artifact:
        result=(seal_source_reference if a.operation=='seal'else verify_source_reference)(artifact,a.guide);print(json.dumps({'artifact':str(artifact),**result}))
