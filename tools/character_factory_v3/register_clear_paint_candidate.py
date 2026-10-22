"""Apply one recorded source-viewport transform to a complete painted action.

Canvas alignment is not an anatomical fit certificate. No figure bounding-box
registration, individual pose scaling, or pixel body warping is performed.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
from build_fixed_grid_sequence_review import frames_from_sheet,gif

def validated_pose_map(recipe,manifest,direction):
    indices=list(range(manifest['frame_count']))
    if recipe is None:return indices
    if recipe['guide_job']!=manifest['job']['id'] or recipe['direction']!=direction:
        raise ValueError('Pose recipe belongs to a different guide or view')
    indices=recipe['source_pose_indices']
    if len(indices)!=manifest['frame_count']:raise ValueError('Pose recipe length mismatch')
    for destination,source in enumerate(indices):
        if not isinstance(source,int) or isinstance(source,bool) or not 0<=source<len(indices):raise ValueError('Invalid source pose index')
        if source==destination:continue
        certificate_path=Path(recipe['certificates'][f'{source}:{destination}'])
        certificate=json.loads(certificate_path.read_text())
        if (certificate['guide_job']!=manifest['job']['id'] or certificate['from_index']!=source or certificate['to_index']!=destination
            or certificate['status']!='ELIGIBLE_FOR_SUBPIXEL_RPG_POSE_HOLD' or 'Weapon' not in certificate['eligible_roles']):
            raise ValueError('Pose hold lacks compatible complete-character evidence')
        if certificate['guide_manifest_sha256']!=recipe['guide_manifest_sha256']:raise ValueError('Stale pose certificate')
    return indices


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pose-recipe',type=Path);p.add_argument('--paint',type=Path,required=True);p.add_argument('--guide',type=Path,required=True);p.add_argument('--direction',required=True);p.add_argument('--viewport',type=int,nargs=4,required=True);p.add_argument('--timing',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--factory',type=Path,default=Path('authoring/characters/factory-v3/patch-0.0.1/factory.json'));a=p.parse_args()
    config=json.loads(a.factory.read_text());manifest=json.loads((a.guide/'manifest.json').read_text());source_size=manifest['job']['resolution'];author_size=config['canvas']['authoring'][0];runtime_size=config['canvas']['runtime'][0]
    if manifest['frame_count']!=16:raise ValueError('This sheet adapter expects16 frames')
    if a.direction not in manifest['views']:raise ValueError('Direction not captured')
    recipe=json.loads(a.pose_recipe.read_text()) if a.pose_recipe else None
    if recipe and recipe['guide_manifest_sha256']!=hashlib.sha256((a.guide/'manifest.json').read_bytes()).hexdigest():raise ValueError('Pose recipe guide digest mismatch')
    pose_indices=validated_pose_map(recipe,manifest,a.direction)
    viewport=a.viewport;side=viewport[2]-viewport[0]
    if side!=viewport[3]-viewport[1]:raise ValueError('Viewport must be square')
    scale=author_size/source_size;extent=round(side*scale);placement=(round(viewport[0]*scale),round(viewport[1]*scale))
    timing=json.loads(a.timing.read_text());durations=timing['preview_durations_ms']
    if len(durations)!=16:raise ValueError('Timeline mismatch')
    detail,records,sheet_size=frames_from_sheet(a.paint,a.output/'detail',768)
    canonical,_,_=frames_from_sheet(a.paint,a.output/'viewport-samples',extent)
    canonical=[canonical[i] for i in pose_indices];detail=[detail[i] for i in pose_indices]
    runtime=[];comparisons=[];contact=Image.new('RGBA',(1536,1536),'#e8e8e8');reports=[]
    for i,cell in enumerate(canonical):
        master=Image.new('RGBA',(author_size,author_size));master.alpha_composite(cell,placement);d=a.output/'Master';d.mkdir(exist_ok=True);master.save(d/f'{i:03d}.png')
        small=master.convert('RGBa').resize((runtime_size,runtime_size),Image.Resampling.LANCZOS).convert('RGBA');d=a.output/'runtime';d.mkdir(exist_ok=True);small.save(d/f'{i:03d}.png');runtime.append(small)
        source=Image.open(a.guide/a.direction/f'{pose_indices[i]:03d}.png').convert('RGBA').resize((author_size,author_size),Image.Resampling.LANCZOS)
        pair=Image.new('RGBA',(1536,800),'#e8e8e8');pair.alpha_composite(source,(0,32));pair.alpha_composite(master,(768,32));draw=ImageDraw.Draw(pair);draw.text((16,10),'CURRENT3D GUIDE',fill='black');draw.text((784,10),'PAINT CANDIDATE - CANVAS ALIGNED, ANATOMY REVIEW PENDING',fill='black');comparisons.append(pair)
        contact.alpha_composite(master.resize((384,384)),((i%4)*384,(i//4)*384))
        reports.append({'index':i,'source_pose_index':pose_indices[i],'authoring_alpha_bbox':master.getchannel('A').getbbox(),'runtime_alpha_bbox':small.getchannel('A').getbbox(),'source_action':manifest['views'][a.direction]['frames'][pose_indices[i]]['action'],'source_frame':manifest['views'][a.direction]['frames'][pose_indices[i]]['source_frame']})
    contact.save(a.output/'contact.png');gif(runtime,a.output/'game-scale-normal.gif',durations);gif(detail,a.output/'detail-normal.gif',durations);gif(detail,a.output/'detail-slow.gif',[d*3 for d in durations]);gif(comparisons,a.output/'guide-vs-paint.gif',durations)
    runtime[0].save(a.output/'game-scale-lossless.webp',save_all=True,append_images=runtime[1:],duration=durations,loop=0,lossless=True,method=4)
    receipt={'status':'CANVAS_ALIGNED_PAINT_CANDIDATE_REQUIRES_ANATOMY_AND_CUTOUT_REVIEW','guide_job':manifest['job']['id'],'direction':a.direction,'master_sha256':hashlib.sha256(a.paint.read_bytes()).hexdigest(),'native_sheet_size':sheet_size,'uniform_source_viewport':viewport,'authoring_canvas':[author_size,author_size],'authoring_viewport_extent':extent,'authoring_viewport_placement':placement,'authoring_root':config['canvas']['authoring_root'],'runtime_canvas':[runtime_size,runtime_size],'runtime_root':config['canvas']['runtime_root'],'per_frame_fitting':False,'anatomy_registration_approved':False,'modular_parts_complete':False,'source_pose_registered':False,'frames':reports,'pose_recipe':recipe,'unique_source_pose_count':len(set(pose_indices)),'timeline_slots':len(pose_indices),'preview_durations_ms':durations,'owner_approved':False,'runtime_admitted':False,'limitations':['Only the recorded source viewport has been inverted into the canonical canvas; this does not correct image-generation pose drift.','Detail preview uses shared resampling of native painted pixels, not newly authored high-resolution detail.','No final cutout package or game admission is claimed.']}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'output':str(a.output),'guide':manifest['job']['id'],'anatomy_registration_approved':False,'modular_parts_complete':False}))

if __name__=='__main__':main()
