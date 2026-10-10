"""Export original full-character pose studies for review, never a production pack.

Source cells may be inspected with an explicit horizontal review bleed. Boundary
violations remain blocking findings; bleed preserves the offending pixels for QA.
No frame fitting, limb warping, mirroring, or automatic visual approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']


def export(plan, repository, output):
    repository, output = Path(repository).resolve(), Path(output).resolve()
    if plan.get('schemaVersion') != '1.0' or list(plan['sheets']) != DIRECTIONS:
        raise ValueError('Study requires all eight canonical directions in order')
    motion_file = (repository / plan['motionTemplate']).resolve()
    motion = json.loads(motion_file.read_text(encoding='utf8'))
    action = plan['action']
    sequences = motion['actions'][action]['directions']
    timing = [f['durationMs'] for f in sequences['S']['frames']]
    if any([f['durationMs'] for f in sequences[d]['frames']] != timing for d in DIRECTIONS):
        raise ValueError('Study comparison requires synchronized direction clocks')
    mapping = plan['timelineToPose']
    if len(mapping) != len(timing) or any(type(i) is not int or i < 0 or i >= 6 for i in mapping):
        raise ValueError('Every motion frame needs an explicit six-pose study mapping')
    sw, sh = plan['sourceCell']
    scale, bleed = plan['sharedScale'], plan.get('reviewBleedX', 0)
    if not (0 < scale <= 1) or type(bleed) is not int or not 0 <= bleed <= sw//4:
        raise ValueError('Invalid fixed scale or review bleed')
    width, height = motion['registration']['canvas']
    target = motion['registration']['root']
    alpha_floor=plan.get('alphaFloor',0)
    if type(alpha_floor) is not int or not 0 <= alpha_floor <= 16:
        raise ValueError('Review alpha noise floor must be explicitly bounded to 0..16')
    rendered, records, findings, sources = {}, [], [], []
    for direction, source in plan['sheets'].items():
        scale=source.get('scale',plan['sharedScale'])
        if not isinstance(scale,(int,float)) or not 0 < scale <= 1:
            raise ValueError('Invalid fixed source-sheet scale')
        path = (repository / source['file']).resolve()
        if not path.is_relative_to(repository) or 'private-ro-reference' in path.parts or '.git' in path.parts:
            raise ValueError('Review exports require original repository artwork')
        image = Image.open(path)
        if image.mode != 'RGBA' or image.size != (sw*3, sh*2):
            raise ValueError('Expected RGBA six-cell source sheet: ' + direction)
        alpha=image.getchannel('A');removed=sum(alpha.histogram()[1:alpha_floor+1])
        if alpha_floor:
            image.putalpha(alpha.point(lambda value:0 if value<=alpha_floor else value))
        sources.append(dict(direction=direction,file=source['file'],sharedScale=scale,alphaNoisePixelsRemoved=removed,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        root = source['root']
        frames = []
        for i in range(6):
            x, y = (i%3)*sw, (i//3)*sh
            alpha = image.getchannel('A').crop((x,y,x+sw,y+sh))
            if not alpha.getbbox() or alpha.getextrema()[0] != 0:
                raise ValueError('Study cell must contain visible art and transparent exterior: '+direction+'/'+str(i))
            borders = [(0,0,sw,1),(0,sh-1,sw,sh),(0,0,1,sh),(sw-1,0,sw,sh)]
            if any(alpha.crop(b).getextrema()[1] > 16 for b in borders):
                findings.append(dict(direction=direction, pose=i, severity='BLOCKING', code='SOURCE_CELL_BOUNDARY',
                    message='Paint crosses nominal source cell; review bleed is not production acceptance'))
            rect = [x-bleed,y,x+sw+bleed,y+sh]
            cell = image.crop(rect).resize((round((sw+2*bleed)*scale),round(sh*scale)),Image.Resampling.LANCZOS)
            dx,dy = round(target['x']-(root[0]+bleed)*scale),round(target['y']-root[1]*scale)
            painted=cell.getchannel('A').getbbox()
            if painted and (painted[0]+dx<0 or painted[1]+dy<0 or painted[2]+dx>width or painted[3]+dy>height):
                raise ValueError(f'Review would clip source pixels: {direction}/{i}')
            frame=Image.new('RGBA',(width,height));frame.paste(cell,(dx,dy));frames.append(frame)
            records.append(dict(direction=direction,pose=i,sourceRect=rect,sourceRoot=root,
                translation=[dx,dy],pixelSHA256=hashlib.sha256(frame.tobytes()).hexdigest()))
        rendered[direction]=frames
    # Finish validation before writing anything.
    output.mkdir(parents=True,exist_ok=True)
    tiles=[]
    for pose in range(6):
        board=Image.new('RGB',(width*4,height*2+48),'#263440');draw=ImageDraw.Draw(board)
        draw.text((10,8),'ORIGINAL POSE STUDY / NOT PRODUCTION / '+plan['phases'][pose],fill='white')
        for i,d in enumerate(DIRECTIONS):
            x,y=(i%4)*width,(i//4)*height+48
            board.paste(rendered[d][pose],(x,y),rendered[d][pose])
            draw.text((x+8,y+5),d,fill='white')
            draw.line((x+target['x']-5,y+target['y'],x+target['x']+5,y+target['y']),fill='#5e7a8a')
        tiles.append(board)
        board.save(output/f'pose-{pose}.png')
    timeline=[tiles[i] for i in mapping]
    for speed,multiplier in [('normal',1),('half',2)]:
        durations=[n*multiplier for n in timing]
        timeline[0].save(output/f'{action}-{speed}.png',save_all=True,append_images=timeline[1:],duration=durations,loop=0)
        elapsed=previous=0;gif_times=[]
        for ms in durations:
            elapsed+=ms;rounded=round(elapsed/10)*10;gif_times.append(rounded-previous);previous=rounded
        timeline[0].save(output/f'{action}-{speed}.gif',save_all=True,append_images=timeline[1:],duration=gif_times,loop=0)
    receipt=dict(schemaVersion='1.0',status='STUDY_ONLY',visualApproval=False,
        action=action,directions=DIRECTIONS,sourcePoseCount=48,timelineToPose=mapping,durationMs=sum(timing),
        timingSource=plan['motionTemplate'],motionSHA256=hashlib.sha256(motion_file.read_bytes()).hexdigest(),
        defaultSourceScale=plan['sharedScale'],alphaFloor=alpha_floor,findings=findings,frames=records,sources=sources,
        limitations=['Combined art; head and weapon are not independently swappable in this study',
                    'Six authored poses held on the existing motion clock, not sixteen independently painted frames',
                    'Fixed registration intentionally exposes painted foot drift',
                    'Anatomy, trajectory, foreshortening and occlusion still require visual review'])
    (output/'study-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    result=export(json.loads(args.plan.read_text(encoding='utf8')),args.repository,args.output)
    print(f"Exported 48 study poses; {len(result['findings'])} blocking source findings; not a production master")
