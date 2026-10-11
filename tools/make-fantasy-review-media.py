"""Publish contact sheets and animated review GIFs from actual delivered strips."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
package=json.loads((OUT/'package.json').read_text());audit=json.loads((OUT/'factory/source-audit.json').read_text())
assert package['nativeSHA256']==audit['nativeSHA256'] and audit['technicalVerdict']=='PASS'
dest=OUT/'renders';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',12)
clips={c['name']:c for c in package['clips']};directions=['SE','W','NW','N'];cell=180
sheet=Image.new('RGB',(cell*4,94+cell*4),(24,37,50));draw=ImageDraw.Draw(sheet)
draw.text((16,12),'ASTRAEON · Supplied fantasy base · Motion/grip review',font=font,fill='#edf1f4')
draw.text((16,40),'CC0 presets on our rig · Neutral wrist · Grip perpendicular to forearm',font=small,fill='#e6be68')
draw.text((16,62),'Actual 2D combinations at common game scale · Art approval pending',font=small,fill='#b8c5d0')
for row,(action,index) in enumerate([('Idle',0),('Walk',4),('BasicAttack',7),('Death',11)]):
    clip=clips[action]
    for col,direction in enumerate(directions):
        strip=Image.open(OUT/clip['strips'][direction]['Composite']).convert('RGBA')
        tile=strip.crop((index*320,0,(index+1)*320,320)).resize((160,160),Image.Resampling.LANCZOS)
        x=col*cell+10;y=94+row*cell
        sheet.paste(tile,(x,y+18),tile);draw.text((x,y),f'{action} {direction} · {index+1}',font=small,fill='#edf1f4')
sheet.save(dest/'motion-contact.png')
for action in ['Walk','BasicAttack','Death']:
    clip=clips[action];strips={d:Image.open(OUT/clip['strips'][d]['Composite']).convert('RGBA') for d in directions};frames=[]
    for index in range(clip['frames']):
        canvas=Image.new('RGB',(cell*4,cell+44),(24,37,50));draw=ImageDraw.Draw(canvas)
        draw.text((12,8),f'{action} · Frame {index+1}/{clip["frames"]} · Owner art review pending',font=small,fill='#e6be68')
        for col,direction in enumerate(directions):
            draw.text((col*cell+10,30),direction,font=small,fill='#edf1f4')
            tile=strips[direction].crop((index*320,0,(index+1)*320,320)).resize((160,160),Image.Resampling.LANCZOS)
            canvas.paste(tile,(col*cell+10,50),tile)
        frames.append(canvas)
    # Review GIFs use a shared palette and repeat for inspection. They retain
    # the contract frame durations; GIF centisecond precision is approximate.
    palette=frames[0].quantize(colors=256);indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(dest/(action.lower()+'-review.gif'),save_all=True,append_images=indexed[1:],duration=clip['durationsMs'],loop=0,disposal=2)
(OUT/'factory/review-media.json').write_text(json.dumps({'nativeSHA256':package['nativeSHA256'],'contactSheet':'renders/motion-contact.png',
    'animations':['renders/walk-review.gif','renders/basicattack-review.gif','renders/death-review.gif'],
    'scope':'Actual packed source combinations; not alternate outfit and not owner approval.'},indent=2)+'\n')
print('REVIEW_MEDIA_COMPLETE')
