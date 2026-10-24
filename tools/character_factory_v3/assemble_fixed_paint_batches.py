"""Assemble complete canonical paint batches without position or scale fitting.

Every frame is recomputed from its pinned raw sheet and fixed viewport before
copying. Source identity, full timeline coverage and original guide PNG hashes
must agree. Assembly does not imply semantic masks or visual acceptance.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from normalize_fixed_viewport_batch import normalize_batch
from track_visible_cutouts import pin_inputs,verify_inputs,sha
from source_capture_identity import verify_source_reference,seal_source_reference,reference_sidecar


def assemble(guide,batches,output):
    if output.exists():raise ValueError('Choose a fresh assembly destination')
    manifest_path=guide/'manifest.json';manifest=json.loads(manifest_path.read_text());digest=sha(manifest_path);count=manifest['frame_count'];collected={};inputs=[manifest_path,Path(__file__),Path(__file__).with_name('normalize_fixed_viewport_batch.py')];common=None;batch_records=[]
    for folder in batches:
        recipe_path=folder/'viewport.json';recipe=json.loads(recipe_path.read_text());receipt_path=folder/'frames/receipt.json';receipt=json.loads(receipt_path.read_text());raw=folder/'raw.png'
        if recipe.get('frame_space')!='canonical-authoring':raise ValueError('Canonical paint batch required')
        source_verification=verify_source_reference(recipe_path,guide)
        identity={k:recipe[k]for k in ['direction','source_size','viewport','canonical_root']}
        if common is None:common=identity
        elif identity!=common:raise ValueError('Paint batches do not share one source viewport and camera')
        for key,path in [('sheet',raw),('recipe',recipe_path)]:
            if receipt['inputs'][key]['sha256']!=sha(path):raise ValueError('Normalized batch input changed')
        expected={i:sha(guide/recipe['direction']/f'{i:03d}.png')for i in range(count)}
        if source_verification['mode']=='EXACT_DECLARED_REFERENCE_BYTES' and {r['index']:r['sha256']for r in recipe['all_source_frame_inputs']}!=expected:raise ValueError('Pinned source PNGs changed')
        images,recalculated=normalize_batch(Image.open(raw),recipe,white_edge_unmatting=receipt.get('white_edge_unmatting',False))
        if recalculated['production_blockers']:raise ValueError('Paint is clipped at a shared viewport edge')
        for image,i in zip(images,recipe['source_pose_indices']):
            if i in collected:raise ValueError('Duplicate painted source pose')
            path=folder/'frames'/f'{i:03d}.png';actual=Image.open(path).convert('RGBA')
            if image.size!=actual.size or not np.array_equal(np.array(image),np.array(actual)):raise ValueError('Frame differs from its fixed raw-sheet normalization')
            collected[i]=path;inputs.append(path)
        inputs += [recipe_path,receipt_path,raw]
        if reference_sidecar(recipe_path).exists():inputs.append(reference_sidecar(recipe_path))
        batch_records.append({'folder':str(folder),'raw_sha256':sha(raw),'recipe_sha256':sha(recipe_path),'indices':recipe['source_pose_indices'],'source_capture_verification':source_verification})
    if common is None or set(collected)!=set(range(count)):raise ValueError('Complete source timeline required; missing poses cannot be fabricated')
    inputs += [guide/common['direction']/f'{i:03d}.png'for i in range(count)];pinned=pin_inputs(inputs);output.mkdir(parents=True);frames=output/'frames';frames.mkdir();width,height=common['source_size'];columns=4;sheet=Image.new('RGBA',(width*columns,height*((count+columns-1)//columns)));records=[]
    for i in range(count):
        path=collected[i];destination=frames/f'{i:03d}.png';shutil.copy2(path,destination);image=Image.open(path);sheet.paste(image,((i%columns)*width,(i//columns)*height));source=manifest['views'][common['direction']]['frames'][i]
        records.append({'index':i,'source_action':source['action'],'source_frame':source['source_frame'],'from_normalized_frame':str(path),'sha256':sha(destination)})
    sheet.save(output/'Master-sheet.png');recipe={**common,'grid':[count,1],'source_pose_indices':list(range(count)),'frame_space':'canonical-authoring','guide_job':manifest['job']['id'],'guide_manifest_sha256':digest,'per_frame_figure_fitting':False,'runtime_admitted':False}
    # This recipe describes the normalized frames, not an inversion of Master-sheet.
    # The sheet layout is independently recorded to avoid a misleading grid recipe.
    recipe['grid']=[columns,(count+columns-1)//columns];recipe['assembly_only_not_raw_sheet_inversion']=True
    recipe['all_source_frame_inputs']=[{'index':i,'sha256':sha(guide/common['direction']/f'{i:03d}.png')}for i in range(count)]
    recipe_path=output/'review-recipe.json';recipe_path.write_text(json.dumps(recipe,indent=2)+'\n')
    seal_source_reference(recipe_path,guide)
    verify_inputs(pinned)
    result={'status':'COMPLETE_FIXED_PAINT_TIMELINE_REVIEW_NOT_APPROVED','guide_job':manifest['job']['id'],'direction':common['direction'],'frames':records,'batches':batch_records,'implementation_sha256':sha(Path(__file__)),'source_manifest_sha256':digest,'frame_space':'canonical-authoring','per_frame_figure_fitting':False,'normalized_pixel_positions_preserved':True,'paint_anatomy_matches_source_certified':False,'runtime_admitted':False,'semantic_masks_approved':False,'input_hashes':pinned}
    (output/'assembly-receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--batch',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=assemble(a.guide,a.batch,a.output);print(json.dumps({'frames':len(r['frames']),'direction':r['direction'],'per_frame_fitting':False}))
