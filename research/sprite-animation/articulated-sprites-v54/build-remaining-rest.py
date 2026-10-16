"""Static source-part assembly; original visible limbs over native hidden underlap.
All masks are authored rest-space regions, not image-inferred anatomy or per-frame patches.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
P=Path(__file__).resolve().parent
C={
'S':{'body':('S-parts-cleanup2.png',[384,0,480,512],.48,[159,168]),'arms':[(2,.45,[185,158]),(3,.45,[135,164])],'legs':[(5,.42,[205,323]),(4,.42,[167,323])],
 'arm_poly':[[[290,217],[314,219],[328,239],[328,272],[335,310],[334,339],[326,358],[308,358],[298,345],[305,319],[299,287],[291,263],[280,240]],[[200,217],[219,221],[228,241],[216,266],[211,293],[205,322],[202,347],[193,359],[177,355],[170,343],[174,318],[181,287],[185,264],[184,243]]],
 'arm_inner':[('max',305),('min',204)],'leg_poly':[[[256,388],[336,388],[336,504],[256,504]],[[177,388],[256,388],[256,504],[177,504]]],'order':['right_leg','left_leg','head','body','right_arm','left_arm']},
'NW':{'body':('NW-original-parts-attempt1.png',[384,0,440,512],.59,[138,124]),'arms':[(2,.5,[113,136]),(3,.5,[151,134])],'legs':[(4,.42,[149,325]),(5,.42,[205,315])],
 'arm_poly':[[[204,215],[232,219],[239,241],[226,269],[216,295],[205,324],[201,351],[187,361],[173,354],[174,335],[182,311],[188,282],[194,260],[194,236]],[[294,218],[309,224],[317,245],[319,279],[321,309],[318,334],[305,340],[299,311],[299,278],[296,249]]],
 'arm_inner':[('min',215),('max',307)],'leg_poly':[[[201,385],[240,385],[244,430],[253,500],[174,500],[175,461],[203,447],[204,417],[196,399]],[[257,403],[279,397],[305,389],[316,390],[319,500],[256,500]]],'order':['right_leg','left_leg','right_arm','head','body','left_arm']},
'NE':{'body':('NE-original-parts-attempt1.png',[384,0,384,512],.59,[112,131]),'arms':[(2,.5,[133,132]),(3,.5,[188,132])],'legs':[(4,.42,[129,318]),(5,.42,[198,321])],
 'arm_poly':[[[208,218],[224,224],[226,247],[220,281],[211,311],[208,337],[194,337],[193,315],[200,279],[204,248]],[[282,217],[307,219],[318,239],[322,267],[329,296],[335,326],[333,347],[320,359],[306,354],[302,337],[307,317],[302,294],[296,270],[285,247]]],
 'arm_inner':[('min',211),('max',309)],'leg_poly':[[[213,390],[233,395],[254,407],[256,500],[198,500],[198,450],[210,415],[210,397]],[[270,388],[326,388],[326,423],[312,447],[342,460],[342,500],[263,500],[265,450],[270,423],[268,403]]],'order':['left_leg','right_leg','left_arm','head','body','right_arm']},
'SE':{'body':('SE-original-parts-attempt1.png',[384,0,384,512],.55,[129,137]),'arms':[(2,.47,[192,155]),(3,.47,[105,159])],'legs':[(4,.45,[220,309]),(5,.45,[132,317])],
 'arm_poly':[[[290,218],[307,224],[312,247],[319,277],[328,310],[333,334],[328,346],[315,349],[305,333],[303,307],[299,282],[291,259],[284,241]],[[211,219],[236,222],[247,238],[244,264],[239,290],[242,321],[242,347],[229,360],[213,355],[205,338],[205,313],[200,285],[197,260],[197,239]]],
 'arm_inner':[('min',307),('max',227)],'leg_poly':[[[265,388],[345,388],[345,500],[265,500]],[[211,388],[259,388],[254,431],[254,451],[260,478],[260,505],[201,505],[202,474],[211,451],[211,426]]],'order':['left_leg','right_leg','left_arm','head','body','right_arm']}}
# Far arms have no visible pixels in these rear views. Never label cape pixels as a hidden arm.
C['NW']['arm_poly'][1]=[];C['NE']['arm_poly'][0]=[]
for view,c in C.items():
 out=P/'parts'/view;out.mkdir(parents=True,exist_ok=True);master=Image.open(P.parent/'ro-core-views-v52/stage/idle'/view/'00.png').convert('RGBA');raw=Image.open(P/'raw'/f'{view}-original-parts-attempt1.png').convert('RGBA');spec={};parts={}
 def save(n,a,desc):
  a.save(out/f'{n}.png');spec[n]={**desc,'texture_sha256':hashlib.sha256((out/f'{n}.png').read_bytes()).hexdigest()};parts[n]=a
 head=Image.new('RGBA',(512,512));head.alpha_composite(master.crop((0,0,512,215)));save('head',head,{'source':'exact original visible head/neck with4px covered collar underlap','rect':[0,0,512,215]})
 file,r,s,t=c['body'];im=Image.open(P/'raw'/file).convert('RGBA').crop((r[0],r[1],r[0]+r[2],r[1]+r[3]));a=Image.new('RGBA',(512,512));a.alpha_composite(im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS),tuple(t));save('body',a,{'source':file,'rect':r,'scale':s,'translation':t})
 for kind in ['arm','leg']:
  for j,side in enumerate(['left','right']):
   cell,s,t=c[kind+'s'][j];limbraw=Image.open(P/'raw'/('NW-parts-cleanup2.png' if view=='NW' else 'NE-leg-cleanup3.png')).convert('RGBA') if kind=='leg' and view in ['NW','NE'] else raw;im=limbraw.crop((cell%4*384,cell//4*512,cell%4*384+384,cell//4*512+512));a=Image.new('RGBA',(512,512));a.alpha_composite(im.resize((round(384*s),round(512*s)),Image.Resampling.LANCZOS),tuple(t));poly=c[kind+'_poly'][j];mask=Image.new('L',(512,512));
   if poly:ImageDraw.Draw(mask).polygon(poly,fill=255)
   visible=master.copy();visible.putalpha(ImageChops.multiply(master.getchannel('A'),mask))
   if kind=='arm' and poly:
    mode,cut=c['arm_inner'][j];a.paste((0,0,0,0),(cut,0,512,512) if mode=='max' else (0,0,cut,512));a.paste((0,0,0,0),(0,0,512,225));a.paste((0,0,0,0),(0,295,512,512));a.paste((0,0,0,0),(0,0,cut-20,512) if mode=='max' else (cut+20,0,512,512))
   elif kind=='leg':
    # Original visible calf/boot region replaces the static underlying source pixels.
    top=min(y for x,y in poly);a.paste((0,0,0,0),(0,top,512,512))
   a.alpha_composite(visible);save(side+'_'+kind,a,{'native_cell':cell,'scale':s,'translation':t,'original_visible_polygon':poly,'scope':'One static source composition with hidden native underlap, never frame-dependent shoe/head patch'})
 # Original visible body/cape pixels remain the visual authority. Native body is only hidden armhole underlap.
 support=Image.new('L',(512,512));ImageDraw.Draw(support).rectangle((211,220,305,310),fill=255);under=parts['body'].copy();under.putalpha(ImageChops.multiply(under.getchannel('A'),support));m=Image.new('L',(512,512));q=ImageDraw.Draw(m);q.rectangle((0,211,511,387),fill=255)
 cape_addons={'S':[[335,375],[420,375],[420,410],[335,410]],'NW':[[238,375],[390,355],[384,377],[347,369],[303,391],[252,404],[241,398]],'NE':[[124,375],[273,375],[263,405],[250,404],[218,393],[192,390],[164,383],[127,386]],'SE':[[100,375],[200,375],[200,410],[100,410]]}
 q.polygon(cape_addons[view],fill=255)
 for arm in c['arm_poly']:
  if arm:q.polygon(arm,fill=0)
 visible=master.copy();visible.putalpha(ImageChops.multiply(master.getchannel('A'),m));under.putalpha(ImageChops.multiply(under.getchannel('A'),visible.getchannel('A').point(lambda a:0 if a else 255)));under.alpha_composite(visible);save('body',under,{'source':'Exact original visible body/scarf/cape; native only bounded hidden armhole underlap','original_body_rect':[0,211,512,388],'cape_hem_region':cape_addons[view],'native_hidden_region':[211,220,305,310],'excludes_original_arm_polygons':c['arm_poly'],'scope':'Static authored segmentation, not automatic anatomy or new wardrobe approval'})
 board=Image.new('RGBA',(1024,512))
 for n in c['order']:board.alpha_composite(parts[n])
 board.alpha_composite(master,(512,0));bg=Image.new('RGBA',board.size,(40,43,48,255));bg.alpha_composite(board);bg.convert('RGB').save(P/f'{view}-rest-comparison.png');(P/f'{view}-rest-contract.json').write_text(json.dumps({'view':view,'parts':spec,'order':c['order'],'scope':'Authored rest-space selection and fixed packing. Native hidden art is not anatomically validated by source joints. Requires rest/playback review.','production_pass':False},indent=2)+'\n')
