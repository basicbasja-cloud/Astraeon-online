"""Export separate, lossless per-role sheets from real native draw samples.

Transparent trimming in runtime atlases never changes the editor sheets' full
canonical cells. Source hashes and every exported cell are verified.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def export(samples_path,output,repository=ROOT):
    if output.exists():raise ValueError('Preserve previous sheet exports')
    data=json.loads(samples_path.read_text());canvas=data['canvas'];w=canvas['compositionWidth'];h=canvas['compositionHeight']
    groups={}
    for f in data['frames']:
        key=(f['action'],f['direction']);groups.setdefault(key,[]).append(f)
    output.mkdir(parents=True);records=[]
    for (action,direction),frames in groups.items():
        frames=sorted(frames,key=lambda f:f['index'])
        if [f['index']for f in frames]!=list(range(len(frames))):raise ValueError('Duplicate or missing frame index')
        roles=[p['role']for p in frames[0]['parts']]
        if any([p['role']for p in f['parts']]!=roles for f in frames):raise ValueError('Role order changes across frames')
        for role in roles:
            cols=4;rows=(len(frames)+cols-1)//cols;sheet=Image.new('RGBA',(w*cols,h*rows));cells=[]
            for f in frames:
                p=next(p for p in f['parts']if p['role']==role);path=(repository/p['source_file']).resolve()
                if not path.is_relative_to(repository.resolve()):raise ValueError('Source part escaped repository')
                if hashlib.sha256(path.read_bytes()).hexdigest()!=p['source_sha256']:raise ValueError('Source part changed')
                image=Image.open(path)
                if image.mode!='RGBA'or image.size!=(w,h):raise ValueError('Source part canvas differs')
                i=f['index'];rect=[i%cols*w,i//cols*h,w,h];sheet.paste(image,tuple(rect[:2]))
                cells.append({'index':i,'rect':rect,'source_pose_action':f['source_action'],
                              'source_pose_frame':f['source_frame'],'source_sha256':p['source_sha256']})
            folder=output/action/direction;folder.mkdir(parents=True,exist_ok=True);path=folder/(role+'.png');sheet.save(path)
            with Image.open(path)as actual:
                for f,c in zip(frames,cells):
                    p=next(p for p in f['parts']if p['role']==role);x,y,cw,ch=c['rect']
                    if actual.crop((x,y,x+cw,y+ch)).tobytes()!=Image.open(repository/p['source_file']).tobytes():raise ValueError('Sheet cell pixel mismatch')
            records.append({'action':action,'direction':direction,'role':role,'file':str(path.relative_to(output)),
                            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'canvas':sheet.size,'cells':cells,
                            'cell_pixel_mismatches':0})
    receipt={'status':'LOSSLESS_EDITOR_PART_SHEETS_NOT_SEMANTIC_APPROVAL','sheets':records,
             'cell_size':[w,h],'root':[canvas['rootAnchorX']*w/canvas['frameWidth'],canvas['rootAnchorY']*h/canvas['frameHeight']],
             'source_samples_sha256':hashlib.sha256(samples_path.read_bytes()).hexdigest(),
             'runtime_uses_trimmed_atlases':True,'semantic_review_required':True,'runtime_admitted':False}
    (output/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--samples',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=export(a.samples,a.output)
    print(json.dumps({'sheets':len(r['sheets']),'cell_checks':sum(len(s['cells'])for s in r['sheets'])}))
