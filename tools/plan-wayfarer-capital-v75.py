"""Reorganize Wayfarer as a geometric royal capital with a ceremonial hierarchy."""
import json,math,subprocess
from pathlib import Path
from shapely.geometry import Polygon,LineString,box,Point
from shapely.ops import unary_union
from shapely.affinity import translate,rotate
from shapely import constrained_delaunay_triangles
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'docs/review/wayfarer-capital-v75/plan.json').exists():
 raise SystemExit('The reviewed capital plan already exists. Edit that plan and run prepare-wayfarer-capital-geometry-v75.py and draw-wayfarer-capital-v75.py; do not regenerate occupied lots.')
s=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
if s.get('layoutId')=='wayfarer-regional-capital-v75':s=json.loads(subprocess.check_output(['git','show','7b72b3f:world/v3/wayfarer-spatial.json'],cwd=ROOT))
assert s['layoutId']=='wayfarer-concept-terraced-town-v49', 'Plan from the source74 checkpoint, not an already-expanded capital';roots=json.loads((ROOT/'docs/review/wayfarer-capital-v75/source74-roots.json').read_text())
land=Polygon([(40,18),(216,18),(240,42),(240,244),(216,268),(40,268),(16,244),(16,42)])
roads=[('royal-boulevard-north',[[128,72],[128,128]],14),('royal-boulevard-south',[[128,160],[128,280]],14),
 ('royal-cross-west',[[3,144],[104,144]],12),('royal-cross-east',[[152,144],[253,144]],12),
 ('capital-circuit',[[48,32],[208,32],[208,240],[48,240],[48,32]],8),
 ('north-arrival',[[128,7],[128,32]],9),('north-civic-road',[[48,32],[208,32]],6),
 ('hall-avenue',[[32,80],[224,80]],8),('district-cross-north',[[32,112],[224,112]],7),
 ('district-cross-south',[[32,184],[224,184]],8),('commons-cross',[[48,216],[208,216]],7),
 ('south-parterre-road',[[64,248],[192,248]],5),
 ('civic-west',[[96,32],[96,80]],7),('civic-east',[[160,32],[160,80]],7),
 ('west-district-spine',[[80,80],[80,240]],7),('east-district-spine',[[176,80],[176,240]],7),
 ('inner-west-street',[[104,96],[104,240]],5.5),('inner-east-street',[[152,96],[152,240]],5.5),
 ('west-wall-lane',[[32,60],[32,228]],4.5),('east-wall-lane',[[224,60],[224,228]],4.5),
]
roadzone=unary_union([LineString(p).buffer(w/2+.75,cap_style=2,join_style=2) for _,p,w in roads])
# Move the actual existing civic and merchant precincts together, including stairs.
civic=['guild-hall','consortium-forecourt-arcades','civic-terrace-retaining','guild-board','planter-a','planter-b','frontage-garden-home','frontage-scribe','district-garden-row-house','district-northern-townhouse']
market=['market-shop','district-east-market-warehouse','district-east-market-tower-house','east-house','west-house','north-house','frontage-market-arcade','frontage-willow-east','east-row-home','merchant-court','district-market-court','food-market','market-spices','market-supplies','market-textiles','market-crates','caravan-cart']
fixed={n:[74,28] for n in civic}
fixed.update({'astral-fountain':[74,91.25],'moon-shrine':[108,75.5],'east-inn':[48,62.2],'artisan-workshop':[45,102.6],'residence':[57,156.6],'market-shop':[80.8,125],'district-east-market-warehouse':[93.6,149.6]})
plaza=box(104,128,152,160);civiczone=box(97,34,159,74);marketzone=box(164,128,196,160)
reserved=unary_union([plaza,civiczone,marketzone,box(181,88,203,108),box(54,94,74,110),box(54,167,74,180),box(85,224,99,237),box(52,46,84,76),box(172,46,204,76),box(172,118,204,140),box(156,165,172,180),box(183,191,202,209)])
parks=[('Royal West Parterre',box(106,78,118,94)),('Royal East Parterre',box(138,78,150,94)),('West Coronation Garden',box(52,120,75,134)),('East Coronation Garden',box(181,120,204,134)),('South West Parterre',box(100,250,119,262)),('South East Parterre',box(137,250,156,262))]
parkzone=unary_union([p for _,p in parks]);buildable=land.buffer(-2.5).difference(roadzone).difference(reserved.buffer(1)).difference(parkzone.buffer(1))
# Formal frontages: cardinal orientations, aligned courses, bilateral cadence.
candidates=[];occupied=[]
for name,path,width in roads:
 for a,b in zip(path,path[1:]):
  if a[0]!=b[0] and a[1]!=b[1]:continue
  horizontal=a[1]==b[1];minimum=min(a[0],b[0]) if horizontal else min(a[1],b[1]);maximum=max(a[0],b[0]) if horizontal else max(a[1],b[1])
  for q in range(21,268,3):
   if q<minimum+5 or q>maximum-5:continue
   for side in (-1,1):
    offset=width/2+5.9;x,y=(q,a[1]+side*offset) if horizontal else (a[0]+side*offset,q)
    angle=(math.pi if side>0 else 0) if horizontal else (math.pi/2 if side>0 else -math.pi/2)
    poly=translate(rotate(box(-5.2,-5.1,5.2,5.1),angle*180/math.pi,origin=(0,0)),xoff=x,yoff=y)
    if buildable.covers(poly) and not any(poly.distance(other)<.6 for other in occupied):
     occupied.append(poly);candidates.append({'center':[round(x,3),round(y,3)],'angle':angle,'lot':list(poly.exterior.coords)[:-1],'road':name})
# Complete each formal block with cardinal courtyard plots. These small courts
# remain walkable, with entrances oriented toward the nearest planned street.
fill=[]
for y in range(29,261,2):
 for x in range(21,237,2):
  p=Point(x,y);r=min(roads,key=lambda r:LineString(r[1]).distance(p));line=LineString(r[1]);q=line.interpolate(line.project(p));dx,dy=q.x-x,q.y-y
  angle=0 if abs(dy)>=abs(dx) and dy>=0 else math.pi if abs(dy)>=abs(dx) else -math.pi/2 if dx>0 else math.pi/2
  poly=translate(rotate(box(-5.2,-5.1,5.2,5.1),angle*180/math.pi,origin=(0,0)),xoff=x,yoff=y)
  if buildable.covers(poly):fill.append((p.distance(q),x,y,angle,poly,r[0]))
for distance,x,y,angle,poly,name in sorted(fill,key=lambda v:(v[0],v[2],v[1])):
 if any(poly.distance(other)<.7 for other in occupied):continue
 occupied.append(poly);candidates.append({'center':[x,y],'angle':angle,'lot':list(poly.exterior.coords)[:-1],'road':name,'sharedCourt':True})
# Existing buildings fill these frontages as whole authored assemblies; additional
# houses use the same detailed facade components with distinct presets.
houses=[]
for o in s['objects']:
 if o['family'] not in ('residential','market','inn','workshop'):continue
 if not any(p['role']=='solid' and max(v[2] for v in p['vertices'])>3 for p in o['parts']):continue
 houses.append(o)
free=[o for o in houses if o['id'] not in fixed]
lots=[]
for i,c in enumerate(candidates):
 old=free[i] if i<len(free) else None;family=old['family'] if old else 'market' if c['center'][0]>145 and c['center'][1]<177 else 'workshop' if c['center'][0]<100 and 145<c['center'][1]<207 else 'residential'
 x,y=c['center'];district='Royal Civic Quarter' if y<90 else 'Seafarer Ward' if x<100 and y<144 else 'Artisan Ward' if x<100 and y<207 else 'Lantern Market' if x>145 and y<177 else 'South Commons' if x<128 else 'Willow Borough'
 lots.append({**c,'id':old['id'] if old else f'capital-{family}-{i:03}','existing':bool(old),'family':family,'district':district,'width':5.2+(i%4)*.65,'depth':6.4+(i%3)*.55,'floors':3 if i%11==0 else 2,'roof':'gable' if i%3 else 'long-ridge','clay':['roofClayWarm','roofClayOchre','roofClayRose','roofClayWarm'][i%4],'balcony':i%4==1,'wing':i%5==2,'garden':i%3!=0})
# Dense outer townhouse rows fill the space between the wall lanes and circuit.
for x,angle in [(40,math.pi/2),(216,-math.pi/2)]:
 for y in range(57,237,11):
  poly=box(x-3.20,y-4.8,x+3.20,y+4.8)
  if not buildable.covers(poly) or any(poly.distance(other)<.5 for other in occupied):continue
  occupied.append(poly);i=len(lots)
  lots.append({'id':f'capital-townhouse-{i:03}','existing':False,'family':'residential','district':'Seafarer Ward' if x<128 and y<144 else 'Artisan Ward' if x<128 else 'Willow Borough','center':[x,y],'angle':angle,'lot':list(poly.exterior.coords)[:-1],'road':'west-wall-lane' if x<128 else 'east-wall-lane','width':5.2,'depth':4.8,'floors':3 if i%4==0 else 2,'roof':'gable','clay':['roofClayWarm','roofClayRose','roofClayOchre'][i%3],'balcony':i%3==0,'wing':False,'garden':True,'denseTownhouse':True})
# Component-authored paired homes occupy selected new neighborhood plots.
# Existing houses and royal-boulevard plots retain their complete model scale.
dense=[]
for i,l in enumerate(lots):
 if l['existing'] or l.get('denseTownhouse') or l['district']=='Royal Civic Quarter' or l['road'].startswith('royal-boulevard') or i%3==0:
  dense.append(l);continue
 x,y=l['center'];angle=l['angle'];w=4.2;offset=2.60
 for side in (-1,1):
  ll={**l,'id':l['id']+('-a' if side<0 else '-b'),'center':[round(x+side*offset*math.cos(angle),4),round(y+side*offset*math.sin(angle),4)],'width':w,'depth':6.4,'roof':'gable','wing':False,'balcony':side>0 and i%4==0,'floors':2 if side<0 else l['floors'],'pairedBlock':l['id'],'garden':side<0,'clay':'roofClayWarm' if side<0 else l['clay']}
  dense.append(ll)
lots=dense
assert len(lots)>=len(free)
# Detailed inherited plots stay visibly integrated in the plan, not a separate island.
for o in houses:
 if o['id'] not in fixed:continue
 ps=[p for p in o['parts'] if p.get('visible')!=False and p['role'] in ('solid','overhead')];vs=[v for p in ps for v in p['vertices']];dx,dy=fixed[o['id']];lo=[min(v[j] for v in vs) for j in (0,1)];hi=[max(v[j] for v in vs) for j in (0,1)];poly=box(lo[0]+dx-.8,lo[1]+dy-.8,hi[0]+dx+.8,hi[1]+dy+.8)
 lots.append({'id':o['id'],'existing':True,'fixed':True,'family':o['family'],'district':'Civic Quarter' if o['id'] in civic else 'Lantern Market' if o['id'] in market else 'City Services','center':[(lo[0]+hi[0])/2+dx,(lo[1]+hi[1])/2+dy],'angle':roots[o['id']]['angle'],'lot':list(poly.exterior.coords)[:-1]})
landmarks=[{'id':'capital-council-chambers','name':'Council Chambers','center':[68,60],'width':28,'depth':20,'height':15,'roofPeak':23,'role':'Regional government','front':[68,77]}, {'id':'capital-grand-archive','name':'Grand Archive','center':[188,60],'width':28,'depth':20,'height':15,'roofPeak':23,'role':'Records and learning','front':[188,77]}, {'id':'capital-trade-exchange','name':'Trade Exchange','center':[188,129],'width':28,'depth':18,'height':11,'roofPeak':18,'role':'Capital commerce','front':[188,143]}]
plan={'version':75,'integratedCity':True,'royalGeometricCity':True,'bounds':{'minX':0,'minY':0,'maxX':256,'maxY':288},'center':[128,144],'landArea':round(land.area,2),'land':list(land.exterior.coords)[:-1],'roads':[{'id':n,'centerline':p,'width':w} for n,p,w in roads],'parks':[{'name':n,'polygon':list(p.exterior.coords)[:-1]} for n,p in parks],'lots':lots,'landmarks':landmarks,'fixedTranslations':fixed,'existingHouses':len(houses),'newHouses':sum(not l['existing'] for l in lots),'densityStrategy':'Townhouse rows and paired neighborhood homes; ceremonial spaces retained','retainedSourcePrecincts':{'civic':[74,28],'plaza':[74,91.25],'shrine':[108,75.5]},'spawn':[13.4,144,0]}
(ROOT/'docs/review/wayfarer-capital-v75/plan.json').write_text(json.dumps(plan,separators=(',',':'))+'\n')
# Draw complete building silhouettes and original civic relationships for review.
im=Image.new('RGB',(1160,1320),'#203444');d=ImageDraw.Draw(im);scale=3.85;ox=85;oy=115;xy=lambda p:(ox+p[0]*scale,oy+p[1]*scale)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
d.text((52,25),'WAYFARER • ROYAL REGIONAL CAPITAL',fill='#ead4a5',font=font);d.text((52,57),'One city • Ceremonial axis • Formal districts • Original layout • Hard RO3 quality target',fill='#bdc9ce',font=small)
d.polygon([xy(p) for p in plan['land']],fill='#b5b292',outline='#ede0be',width=5)
for p in parks:d.polygon([xy(v) for v in p[1].exterior.coords],fill='#6b8558')
for r in plan['roads']:d.line([xy(v) for v in r['centerline']],fill='#ece0c0',width=int(r['width']*scale),joint='curve')
# Public center and retained raised courts connect directly into the streets.
for reg in [plaza,civiczone,marketzone]:d.polygon([xy(v) for v in reg.exterior.coords],fill='#d8caa7')
for l in lots:
 d.polygon([xy(v) for v in l['lot']],fill='#9f997c',outline='#c9bfa0')
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
labels=[('CONSORTIUM HALL',(106,52)),('COUNCIL CHAMBERS',(45,73)),('GRAND ARCHIVE',(168,73)),('TRADE EXCHANGE',(171,137)),('LUNA SHRINE',(178,101)),("SEAFARER’S REST",(48,108)),('WAYFARER SQUARE',(106,157)),('LANTERN MARKET',(166,164)),('BRONZE ANVIL',(50,179)),('SOUTH COMMONS',(65,224)),('WILLOW BOROUGH',(166,224)),('WEST GATE',(1,141)),('NORTH GATE',(113,12)),('SOUTH GATE',(110,276)),('EAST GATE',(218,141))]
for label,p in labels:
 q=xy(p);b=d.textbbox(q,label,font=small);d.rectangle((b[0]-4,b[1]-3,b[2]+4,b[3]+3),fill='#263c4a');d.text(q,label,font=small,fill='#f4dfb4')
d.text((52,1240),f'{len(lots)} houses: {len(houses)} reorganized + {plan["newHouses"]} new • Three major civic buildings • One integrated city',font=small,fill='#ead4a5');d.text((52,1270),'The fountain, civic precinct and service buildings retain their actual model scale.',font=small,fill='#bdc9ce')
im.save(ROOT/'docs/review/wayfarer-capital-v75/blueprint.png');print('ROYAL PLAN',len(lots),'houses',len(houses),'existing',plan['newHouses'],'new; land',plan['landArea'])
