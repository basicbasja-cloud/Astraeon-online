"""Draw actual exported roof footprints, rather than generic house glyphs."""
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76'
p=json.loads((O/'native-plan.json').read_text());s=json.loads((R/'world/v3/wayfarer-spatial.json').read_text());objects={o['id']:o for o in s['objects']}
im=Image.new('RGB',(1160,1320),'#203444');d=ImageDraw.Draw(im);scale=3.85;xy=lambda a:(85+a[0]*scale,115+a[1]*scale)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
d.text((52,25),'WAYFARER • ROYAL CAPITAL — DISTINCT NEIGHBORHOODS',fill='#ead4a5',font=font)
d.text((52,57),'Original plan • Actual native roof footprints • Nine building families • Hard RO3 target',fill='#bdc9ce',font=small)
d.polygon([xy(v) for v in p['land']],fill='#ece0c0',outline='#e8d7aa',width=4)
for b in p['ownedBlocks']:
 d.polygon([xy(v) for v in b['outer']],fill='#aaa180',outline='#d8c9a6',width=2)
 for hole in b['holes']:d.polygon([xy(v) for v in hole],fill='#ece0c0')
for park in p['parks']:d.polygon([xy(v) for v in park['polygon']],fill='#6b8558')
for part in objects.get('capital-beta-frontage-groundcover',{}).get('parts',[]):
 for face in part['faces']:d.polygon([xy(part['vertices'][i]) for i in face],fill='#6b8558')
for road in p['roads']:d.line([xy(v) for v in road['centerline']],fill='#ece0c0',width=int(road['width']*scale),joint='curve')
for n in [l['id'] for l in p['lots']]+[l['id'] for l in p['landmarks']]+['guild-hall','moon-shrine']:
 o=objects[n]
 for part in o['parts']:
  if not part.get('visible',True) or part['role']!='overhead':continue
  color='#496c83' if part['material']=='civicSlate' else '#c98c66' if part['material']=='roofClayOchre' else '#aa6b54'
  for face in part['faces']:d.polygon([xy(part['vertices'][i]) for i in face],fill=color,outline='#715344')
for l in p['lots']:
 a=l['angle']+l.get('frontageOffset',0);x,y=l['center'];dep=l.get('depth',6);d.line([xy((x,y)),xy((x-math.sin(a)*dep*.62,y+math.cos(a)*dep*.62))],fill='#f7ddb3',width=1)
for c in p['courtyards']:d.polygon([xy(v) for v in c['polygon']],outline='#d6af59',width=2)
q=xy((128,144));d.ellipse((q[0]-14,q[1]-14,q[0]+14,q[1]+14),fill='#66b4bd',outline='#e9d99d',width=3)
labels=[('CONSORTIUM HALL',(105,52)),('COUNCIL PALAZZO',(43,74)),('GRAND ARCHIVE',(166,74)),('TRADE EXCHANGE',(168,139)),('LUNA SHRINE',(177,103)),('SEAFARER WARD',(48,108)),('WAYFARER SQUARE',(106,149)),('ARTISANS’ COURT',(84,164)),('WILLOW COURT',(144,200)),('SOUTH COMMONS',(64,239)),('WILLOW BOROUGH',(164,239)),('WEST GATE',(1,141)),('NORTH GATE',(113,12)),('SOUTH GATE',(110,276)),('EAST GATE',(219,141))]
for label,pt in labels:
 q=xy(pt);b=d.textbbox(q,label,font=small);d.rectangle((b[0]-3,b[1]-2,b[2]+3,b[3]+2),fill='#263c4a');d.text(q,label,font=small,fill='#f4dfb4')
d.text((52,1240),f'{len(p["lots"])} buildings • 37 originals • 14 paired plots consolidated • Distinct civic landmarks',font=small,fill='#ead4a5')
d.text((52,1270),'8–10-unit public streets • Continuous owned-block curbs • Two gathering courts • Plaza-facing entries',font=small,fill='#bdc9ce')
im.save(O/'blueprint.png')
(O/'blueprint.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest(),'architectureRevision':s.get('architectureRevision'),'buildings':len(p['lots']),'image':'blueprint.png','use':'Planning visualization of actual exported roof footprints; not gameplay or visual acceptance evidence.'},indent=2)+'\n')
print('Saved actual native architecture blueprint',len(p['lots']))
