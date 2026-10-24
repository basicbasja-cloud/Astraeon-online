"""Pack one actual imported factory action for the real runtime draw API.

This bounded review never creates missing Idle/Walk clips or a fake complete
character definition. References remain independent original painted files.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from patch001_factory import ROOT,BASE,read,filehash
from pack_patch001_character import atlas_pages,trimmed_source,composed_draw_order


def package(job_id,intake_path,output):
    if output.exists():raise ValueError('Choose a fresh review destination')
    ledger=read(BASE/'ledger.json');job=ledger['paint_jobs'][job_id];folder=BASE/'cutouts'/job_id
    receipt=read(folder/'import-receipt.json');bindings=read(folder/'bindings.json');intake=read(intake_path);index=read(BASE/'cutout-store/index.json')
    if receipt['input_manifest_sha256']!=filehash(intake_path)or receipt['guide_job']!=job['guide_job']or not receipt['all_frames_present']:raise ValueError('Actual intake differs from imported action')
    expected={(d,i)for d in job['directions']for i in range(job['frame_count'])};references={(r['direction'],r['index']):r for r in intake['frames']}
    if {(r['direction'],r['index'])for r in bindings['frames']}!=expected or set(references)!=expected:raise ValueError('Incomplete imported action')
    guide=read(BASE/'guides'/job['guide_job']/'manifest.json');pixels=[];objects={};frames=[]
    def relative(path):
        path=path.resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Review reference escaped repository')
        return path.relative_to(ROOT).as_posix()
    for frame in bindings['frames']:
        direction=frame['direction'];i=frame['index'];reference=references[direction,i];ordered=composed_draw_order(frame['base_draw_order'],list(frame['assets']),frame.get('layer_draw_order'));parts=[]
        for role in ordered:
            asset=index['assets'][frame['assets'][role]]
            for key,value in {'role':role,'fit_id':job['fit_id'],'pose_id':frame['pose_id'],'camera_id':frame['camera_id'],'root':frame['sockets']['root'],'canvas':[768,768]}.items():
                if asset.get(key)!=value:raise ValueError('Incompatible imported slot: '+key)
            obj=index['objects'][asset['object']];path=(ROOT/obj['file']).resolve();relative(path)
            if asset['object']not in objects:
                im=Image.open(path)
                if im.mode!='RGBA' or im.size!=(768,768):raise ValueError('Stored canonical object differs')
                a=np.array(im);a[a[:,:,3]==0]=0
                import hashlib
                if hashlib.sha256(a.tobytes()).hexdigest()!=asset['object']:raise ValueError('Stored object pixels changed')
                trimmed,offset=trimmed_source(Image.fromarray(a));objects[asset['object']]=(len(pixels),offset);pixels.append(trimmed)
            number,offset=objects[asset['object']]
            parts.append({'role':role,'object_index':number,'offset':offset,'asset_id':frame['assets'][role],'source_file':relative(path)})
        captured=guide['views'][direction]['frames'][i]
        frames.append({'action':job['actions'][0],'direction':direction,'index':i,'source_action':captured['action'],'source_frame':captured['source_frame'],
                       'parts':parts,'master_file':relative(intake_path.parent/reference['master']),
                       'reference_part_files':[relative(intake_path.parent/reference['parts'][role])for role in ordered]})
    output.mkdir(parents=True);atlases={};placements={}
    for number,(page,slots)in enumerate(atlas_pages(pixels,limit=2048)):
        name=f'page-{number:02d}';path=output/(name+'.png');page.save(path);atlases[name]={'file':path.name,'width':page.width,'height':page.height,'sha256':filehash(path)}
        for i,rect in slots:placements[i]=(name,rect)
    for frame in frames:
        for part in frame['parts']:part['atlasId'],part['rect']=placements[part.pop('object_index')]
    data={'status':'IMPORTED_ACTION_RUNTIME_DRAW_REVIEW_NOT_COMPLETE_CHARACTER','paint_job':job_id,'guide_job':job['guide_job'],'character':job['character'],'canvas':{'frameWidth':240,'frameHeight':240,'compositionWidth':768,'compositionHeight':768,'rootAnchorX':120,'rootAnchorY':172},
          'atlases':atlases,'frames':frames,'unique_pixel_objects':len(pixels),'part_bindings':sum(len(r['parts'])for r in frames),
          'bindings_sha256':filehash(folder/'bindings.json'),'import_receipt_sha256':filehash(folder/'import-receipt.json'),'intake_sha256':filehash(intake_path),'implementation_sha256':filehash(Path(__file__)),
          'playable_characters_verified':0,'runtime_admitted':False}
    (output/'samples.json').write_text(json.dumps(data,indent=2)+'\n');return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paint-job',required=True);p.add_argument('--intake',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=package(a.paint_job,a.intake.resolve(),a.output.resolve());print(json.dumps({'poses':len(r['frames']),'actual_imported_paint_job':r['paint_job'],'part_bindings':r['part_bindings']}))
