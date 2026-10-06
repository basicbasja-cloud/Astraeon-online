"""Redraw the reviewed capital blueprint from its actual active plan."""
import json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,box
from shapely.affinity import translate,rotate
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'docs/review/wayfarer-capital-v75/plan.json').read_text())
s=json.loads(subprocess.check_output(['git','show','7b72b3f:world/v3/wayfarer-spatial.json'],cwd=ROOT))
parks=[(p['name'],Polygon(p['polygon'])) for p in plan['parks']]
landmarks=plan['landmarks'];lots=plan['lots'];fixed=plan['fixedTranslations'];existing_ids={l['id'] for l in lots if l['existing']};houses=[o for o in s['objects'] if o['id'] in existing_ids]
plaza=box(104,128,152,160);civiczone=box(97,34,159,74);marketzone=box(164,128,196,160)
# Draw complete building silhouettes and original civic relationships for review.
im=Image.new('RGB',(1160,1320),'#203444');d=ImageDraw.Draw(im);scale=3.85;ox=85;oy=115;xy=lambda p:(ox+p[0]*scale,oy+p[1]*scale)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
d.text((52,25),'WAYFARER • ROYAL REGIONAL CAPITAL',fill='#ead4a5',font=font);d.text((52,57),'One city • Ceremonial axis • Formal districts • Original layout • Hard RO3 quality target',fill='#bdc9ce',font=small)
d.polygon([xy(p) for p in plan['land']],fill='#b5b292',outline='#ede0be',width=5)
if plan.get('neighborhoodRefinement'):
 native=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text())
 for block in native['ownedBlocks']:
  d.polygon([xy(v) for v in block['outer']],fill='#a69e81',outline='#ddd0ac',width=2)
  for hole in block['holes']:d.polygon([xy(v) for v in hole],fill='#b5b292')
for p in parks:d.polygon([xy(v) for v in p[1].exterior.coords],fill='#6b8558')
for r in plan['roads']:d.line([xy(v) for v in r['centerline']],fill='#ece0c0',width=int(r['width']*scale),joint='curve')
# Public center and retained raised courts connect directly into the streets.
for reg in [plaza,civiczone,marketzone]:d.polygon([xy(v) for v in reg.exterior.coords],fill='#d8caa7')
for l in lots:
 if not plan.get('neighborhoodRefinement'):d.polygon([xy(v) for v in l['lot']],fill='#9f997c',outline='#c9bfa0')
 if l.get('fixed'):
  o=next(o for o in houses if o['id']==l['id']);dx,dy=fixed[l['id']]
  for p in o['parts']:
   if p.get('visible')==False or p['role']!='overhead':continue
   for f in p['faces']:d.polygon([xy((p['vertices'][j][0]+dx,p['vertices'][j][1]+dy)) for j in f],fill='#ba794f',outline='#6e503b')
 else:
  w,dep=l['width'],l['depth'];poly=translate(rotate(box(-w/2,-dep/2,w/2,dep/2),l['angle']*180/math.pi,origin=(0,0)),xoff=l['center'][0],yoff=l['center'][1]);d.polygon([xy(v) for v in poly.exterior.coords],fill='#ba794f' if l['existing'] else '#c48f60',outline='#6e503b');
  # Frontage marker makes street-facing orientation inspectable.
  x,y=l['center'];fx,fy=-math.sin(l['angle']),math.cos(l['angle']);d.line([xy((x,y)),xy((x+fx*dep*.65,y+fy*dep*.65))],fill='#f1d3a2',width=2)
# Ordered avenues and parterres give the plan a dignified ceremonial rhythm.
for park in plan['parks']:
 if park.get('wallGarden'):continue
 ps=park['polygon'];x0,x1=min(v[0] for v in ps),max(v[0] for v in ps);y0,y1=min(v[1] for v in ps),max(v[1] for v in ps)
 d.rectangle([xy((x0+1.1,y0+1.1)),xy((x1-1.1,y1-1.1))],outline='#cccaab',width=2)
 d.line([xy(((x0+x1)/2,y0+1)),xy(((x0+x1)/2,y1-1))],fill='#d2caa9',width=3)
for x in (119,137):
 for y in (100,116,176,200,224,244):
  q=xy((x,y));d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill='#557758',outline='#95a57a',width=1)
# Original Hall and shrine silhouettes: same assets, new integrated placement.
for n in ['guild-hall','moon-shrine']:
 o=next(o for o in s['objects'] if o['id']==n);dx,dy=fixed[n]
 for p in o['parts']:
  if p.get('visible')!=False and p['role']=='overhead':
   for f in p['faces']:d.polygon([xy((p['vertices'][j][0]+dx,p['vertices'][j][1]+dy)) for j in f],fill='#41677a',outline='#d1b56f')
# Monumental civic masses, aligned wings and forecourts show the civic hierarchy.
for landmark in landmarks:
 x,y=landmark['center'];w,dep=landmark['width'],landmark['depth']
 d.rectangle([xy((x-w/2-3,y-dep/2-3)),xy((x+w/2+3,y+dep/2+6))],fill='#d8caa7',outline='#e9dabb',width=2)
 d.rectangle([xy((x-w/2,y-dep/2)),xy((x+w/2,y+dep/2))],fill='#42667c',outline='#d6b978',width=3)
 d.rectangle([xy((x-w*.20,y-dep*.64)),xy((x+w*.20,y+dep*.64))],fill='#34576d',outline='#dfc989',width=2)
 for side in (-1,1):
  xx=x+side*w*.40;d.rectangle([xy((xx-2.2,y+dep/2-2.2)),xy((xx+2.2,y+dep/2+2.2))],fill='#b9ae8a',outline='#dfc989',width=2)
 q=xy((x,y));d.ellipse((q[0]-11,q[1]-11,q[0]+11,q[1]+11),fill='#557d91',outline='#e3ca83',width=3)
q=xy((128,144));d.ellipse((q[0]-14,q[1]-14,q[0]+14,q[1]+14),fill='#66b4bd',outline='#e9d99d',width=3)
for court in plan.get('courtyards',[]):
 d.polygon([xy(v) for v in court['polygon']],outline='#e3ca83',width=2)
 q=xy(court['center']);d.ellipse((q[0]-7,q[1]-7,q[0]+7,q[1]+7),fill='#557d91',outline='#e3ca83',width=2)
labels=[('CONSORTIUM HALL',(106,52)),('COUNCIL CHAMBERS',(45,73)),('GRAND ARCHIVE',(168,73)),('TRADE EXCHANGE',(171,137)),('LUNA SHRINE',(178,101)),("SEAFARER’S REST",(48,108)),('WAYFARER SQUARE',(106,157)),('LANTERN MARKET',(166,164)),('BRONZE ANVIL',(50,179)),('SOUTH COMMONS',(65,224)),('WILLOW BOROUGH',(166,224)),('WEST GATE',(1,141)),('NORTH GATE',(113,12)),('SOUTH GATE',(110,276)),('EAST GATE',(218,141))]
for label,p in labels:
 q=xy(p);b=d.textbbox(q,label,font=small);d.rectangle((b[0]-4,b[1]-3,b[2]+4,b[3]+3),fill='#263c4a');d.text(q,label,font=small,fill='#f4dfb4')
d.text((52,1240),f'{len(lots)} houses: {len(houses)} reorganized + {plan["newHouses"]} new • Three major civic buildings • One integrated city',font=small,fill='#ead4a5');d.text((52,1270),'The fountain, civic precinct and service buildings retain their actual model scale.',font=small,fill='#bdc9ce')
if plan.get('courtyards'):d.text((52,1296),'Owned gathering courts: Artisans’ Court · Willow Court · Frontages face their shared features',font=small,fill='#ead4a5')
im.save(ROOT/'docs/review/wayfarer-capital-v75/blueprint.png');print('ROYAL PLAN',len(lots),'houses',len(houses),'existing',plan['newHouses'],'new; land',plan['landArea'])
