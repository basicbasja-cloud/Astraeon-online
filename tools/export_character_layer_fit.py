"""Capture a partial layer-fit study through its real browser renderer.

This does not compile a production pack or infer missing directions/actions.
"""
import argparse
import base64
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import urlencode
from PIL import Image
from playwright.sync_api import sync_playwright


def export(config, output, base_url='http://127.0.0.1:8022'):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base_url+'/character-layer-fit.html?'+urlencode({'config':config}))
        page.wait_for_function('window.characterLayerFit')
        description=page.evaluate('characterLayerFit.describe()')
        for name,layers in [('composite',['body','head','weapon']),('body',['body']),('head',['head']),('weapon',['weapon']),('body-weapon',['body','weapon'])]:
            poses=[]
            for i in range(len(description['poseNames'])):
                encoded=page.evaluate('([i,layers])=>characterLayerFit.render(i,layers)',[i,layers]).split(',')[1]
                image=Image.open(BytesIO(base64.b64decode(encoded))).convert('RGBA');poses.append(image)
            timeline=[poses[i] for i in description['timelineToPose']]
            for speed,factor in [('normal',1),('half',2)]:
                timeline[0].save(output/f'{name}-{speed}.png',save_all=True,append_images=timeline[1:],duration=[n*factor for n in description['timing']],loop=0)
            board=Image.new('RGBA',(960*3,640*2))
            for i,pose in enumerate(poses):board.paste(pose,(i%3*960,i//3*640))
            board.save(output/f'{name}-board.png')
        assert not errors,errors
        browser.close()
    receipt=dict(status='PARTIAL_STUDY',visualApproval=False,config=config,description=description,browserErrors=errors,
                 limitations=['Only explicitly authored direction/action; never extrapolates production coverage','Numeric export success does not approve source anatomy or registration'])
    (output/'export.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Captured five independent layer modes at normal and half speed; partial study only.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',required=True);parser.add_argument('--output',required=True);parser.add_argument('--base-url',default='http://127.0.0.1:8022')
    args=parser.parse_args();export(args.config,args.output,args.base_url)
