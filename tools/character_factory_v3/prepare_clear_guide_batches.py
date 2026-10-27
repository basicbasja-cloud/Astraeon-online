"""Create clear paint references with one shared viewport across all poses/views."""
import argparse,json,hashlib,math
from pathlib import Path
from PIL import Image


def checked_viewport(bounds,viewport,source_size):
    if not bounds:raise ValueError('No visible source poses')
    if len(viewport)!=4 or any(type(v)is not int for v in viewport):raise ValueError('Integer source viewport required')
    left,top,right,bottom=viewport
    if not(0<=left<right<=source_size[0]and 0<=top<bottom<=source_size[1]):raise ValueError('Viewport exceeds source canvas; regenerate overscan without changing camera scale')
    if right-left!=bottom-top:raise ValueError('Shared viewport must be square')
    margins=[min(b[0]-left,b[1]-top,right-b[2],bottom-b[3])for b in bounds]
    if min(margins)<1:raise ValueError('Shared viewport clips or touches a source body/weapon; include every pose before painting')
    return min(margins)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--cell',type=int,default=768);p.add_argument('--viewport',type=int,nargs=4);a=p.parse_args();manifest=json.loads((a.guide/'manifest.json').read_text());job=manifest['job'];bounds=[]
    if a.output.exists():raise ValueError('Choose a fresh reference output')
    if a.cell<1:raise ValueError('Positive reference cell size required')
    source_size=None;source_inputs=[]
    for direction in job['directions']:
        for i in range(manifest['frame_count']):
            path=a.guide/direction/f'{i:03d}.png';im=Image.open(path).convert('RGBA');b=im.getchannel('A').getbbox()
            if source_size is None:source_size=im.size
            if im.size!=source_size:raise ValueError('Source canvases differ')
            if not b:raise ValueError('Empty source pose')
            if b[0]==0 or b[1]==0 or b[2]==im.width or b[3]==im.height:raise ValueError('Source render itself touches its canvas edge')
            bounds.append(b);source_inputs.append({'direction':direction,'index':i,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'foreground_bbox':list(b)})
    if not bounds:raise ValueError('No captured source poses')
    x0=min(b[0] for b in bounds);y0=min(b[1] for b in bounds);x1=max(b[2] for b in bounds);y1=max(b[3] for b in bounds);side=math.ceil(max(x1-x0,y1-y0)*1.16/2)*2;cx=(x0+x1)/2;cy=(y0+y1)/2;viewport=[round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2)];viewport=a.viewport or viewport;side=viewport[2]-viewport[0]
    minimum_margin=checked_viewport(bounds,viewport,source_size)
    scale=a.cell/side;records=[]
    a.output.mkdir(parents=True,exist_ok=True)
    for direction in job['directions']:
        d=a.output/direction;d.mkdir(exist_ok=True);frames=[]
        for i in range(manifest['frame_count']):
            source=a.guide/direction/f'{i:03d}.png';im=Image.open(source).convert('RGBA').crop(viewport).resize((a.cell,a.cell),Image.Resampling.LANCZOS);im.save(d/f'{i:03d}.png');frames.append(im)
        for start in range(0,len(frames),4):
            contact=Image.new('RGBA',(a.cell*2,a.cell*2),'white')
            for k,im in enumerate(frames[start:start+4]):contact.alpha_composite(im,((k%2)*a.cell,(k//2)*a.cell))
            name=f'batch-{start:03d}-{min(start+3,len(frames)-1):03d}.png';contact.save(d/name);records.append({'direction':direction,'indices':list(range(start,min(start+4,len(frames)))),'file':str((d/name).relative_to(a.output))})
    receipt={'status':'SOURCE_GUIDE_PAINT_REFERENCE_ONLY','guide_job':job['id'],'manifest_sha256':hashlib.sha256((a.guide/'manifest.json').read_bytes()).hexdigest(),'uniform_source_viewport':viewport,'source_to_cell_scale':scale,'cell_size':a.cell,'per_frame_fitting':False,'same_transform_for_all_views':True,'first_frame_joint_roots_in_cell':{direction:[(value-viewport[axis])*scale for axis,value in enumerate(manifest['views'][direction]['frames'][0]['landmarks']['root'])] for direction in job['directions']},'root_note':'Projected skeleton root from source manifest; no silhouette-based root fitting','batches':records}
    receipt.update({'all_source_frame_inputs':source_inputs,'minimum_foreground_margin_source_px':minimum_margin,'source_bodies_and_weapons_complete':True,'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'viewport':viewport,'scale':scale,'batches':len(records)}))

if __name__=='__main__':main()
