"""Export actual browser-composited action frames, GIFs and full-color APNGs.

A single shared viewport is used for every pose/view. No frame fitting, art
synthesis, pose interpolation or source event retiming is performed.
"""
import argparse,base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright


def capture(url,timings_path,output,action='BasicAttack'):
    if output.exists():raise ValueError('Choose a fresh runtime capture destination')
    durations=json.loads(timings_path.read_text())['durations_ms']
    if not durations or any(type(d)is not int or d<10 or d%10 for d in durations):raise ValueError('Use explicit GIF-compatible original frame timings')
    output.mkdir(parents=True);directions=['SW','NW','NE','SE'];images={d:[]for d in directions};errors=[];records=[]
    with sync_playwright()as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page();page.on('pageerror',lambda error:errors.append(str(error)));page.goto(url);page.wait_for_function('window.importedActionReport!==undefined',timeout=180000);report=page.evaluate('window.importedActionReport')
        if report['status']!='ACTUAL_IMPORTED_ACTION_COMPOSITOR_PASS_NOT_FULL_CHARACTER_ACCEPTANCE':raise ValueError('Actual imported-action compositor did not pass')
        page.wait_for_function('window.setImportedActionFrame!==undefined');page.evaluate("() => {const c=document.getElementById('detail');c.width=c.height=768}")
        for direction in directions:
            (output/direction).mkdir()
            for i in range(len(durations)):
                page.evaluate('p=>window.setImportedActionFrame(p.action,p.direction,p.index)',{'action':action,'direction':direction,'index':i});value=page.locator('#detail').evaluate("c=>c.toDataURL('image/png').split(',')[1]");raw=base64.b64decode(value);im=Image.open(io.BytesIO(raw)).convert('RGBA');im.save(output/direction/f'{i:03d}.png');images[direction].append(im);records.append({'direction':direction,'index':i,'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
        browser.close()
    if errors:raise ValueError('Browser errors: '+str(errors))
    boxes=[im.getbbox()for frames in images.values()for im in frames];box=[max(0,min(b[0]for b in boxes)-16),max(0,min(b[1]for b in boxes)-16),min(768,max(b[2]for b in boxes)+16),min(768,max(b[3]for b in boxes)+16)];width,height=box[2]-box[0],box[3]-box[1];boards=[]
    for i in range(len(durations)):
        board=Image.new('RGB',(width*4,height+24),'#e5e5e5');draw=ImageDraw.Draw(board)
        for col,d in enumerate(directions):
            im=images[d][i].crop(tuple(box));board.paste(im,(col*width,24),im);draw.text((col*width+8,4),d,fill='black')
        boards.append(board)
    sample=Image.new('RGB',(boards[0].width*4,boards[0].height*((len(boards)+3)//4)),'#e5e5e5')
    for i,im in enumerate(boards):sample.paste(im,((i%4)*im.width,(i//4)*im.height))
    palette=sample.quantize(colors=255);quantized=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in boards];quantized[0].save(output/'four-views-normal.gif',save_all=True,append_images=quantized[1:],duration=durations,loop=0,disposal=2);boards[0].save(output/'four-views-full-color.png',save_all=True,append_images=boards[1:],duration=durations,loop=0,disposal=0,blend=0)
    single=[]
    for im in images['SE']:
        frame=Image.new('RGB',(width,height),'#e5e5e5');crop=im.crop(tuple(box));frame.paste(crop,(0,0),crop);single.append(frame)
    colors=Image.new('RGB',(width*4,height*((len(single)+3)//4)))
    for i,im in enumerate(single):colors.paste(im,((i%4)*width,(i//4)*height))
    palette=colors.quantize(colors=255);q=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in single];q[0].save(output/'SE-normal.gif',save_all=True,append_images=q[1:],duration=durations,loop=0,disposal=2);single[0].save(output/'SE-full-color.png',save_all=True,append_images=single[1:],duration=durations,loop=0,disposal=0,blend=0)
    result={'status':'REAL_IMPORTED_ACTION_RUNTIME_FRAMES_EXPORTED_NOT_CHARACTER_ACCEPTANCE','action':action,'source_canvas':[768,768],'shared_viewport':box,'per_frame_figure_fitting':False,'duration_ms':durations,'duration_source_sha256':hashlib.sha256(timings_path.read_bytes()).hexdigest(),'total_duration_ms':sum(durations),'frames':records,'browser_report':{k:v for k,v in report.items()if k!='checks'},'page_errors':errors,'runtime_admitted':False};(output/'capture-receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url',required=True);p.add_argument('--timings',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=capture(a.url,a.timings,a.output);print(json.dumps({'frames':len(r['frames']),'shared_viewport':r['shared_viewport'],'total_duration_ms':r['total_duration_ms'],'page_errors':r['page_errors']}))
