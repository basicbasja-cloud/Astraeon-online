"""One-time Golden layout edit of the saved court, not a parity/proof generator.

Run against authoring/wayfarer-court.blend. The saved .blend remains the authority;
subsequent edits use export-world-v3.py without rerunning this initial redesign.
Physical foundation outlines are artist-registered ground planes, not image boxes.
"""
import bpy, json, math, runpy, subprocess
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'))
mesh,empty=kit['mesh'],kit['empty']
scene=bpy.context.scene
old=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./world-view.js');eval(require('fs').readFileSync(0,'utf8'));require('./town-structure.js');console.log(JSON.stringify({content:window.AstraeonContent,metadata:window.AstraeonTownStructure.metadata}))"],cwd=ROOT,input=subprocess.check_output(['git','show','f610aef:world-content.js'],cwd=ROOT)))
terrain=bpy.data.collections['court-terrain']
for o in list(terrain.objects):
 if o.get('surface_role'):bpy.data.objects.remove(o,do_unlink=True)

def surface(id,role,points,parent=None):
 o=mesh(terrain,id,[(x,y,.005) for x,y in points],[list(range(len(points)))],'paving','decorative',False)
 o['surface_role']=role
 if parent:o['object_id']=parent.name.removesuffix('-placement');o.parent=parent
 return o

def road(id,role,points,width):
 for j,(a,b) in enumerate(zip(points,points[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*width/2,dx/n*width/2
  o=surface(id+'-'+str(j),{'avenue':'primary','street':'residential'}.get(role,role),[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]])
  o['road_segment']=True;o['legacy_role']=role

# West arrival bends through the existing painted gate's real opening, then
# opens onto a broad avenue. Facades keep their original camera orientation.
road('west-field','field',[[6.95,40],[6.95,27],[6.95,25]],2.1)
road('arrival-passage','street',[[6.95,25],[6.95,19.1]],1.1)
road('main-avenue','avenue',[[6.95,18.5],[13.8,18.5],[18,19.6]],3.4)
road('civic-axis','avenue',[[21.8,16.8],[21.8,14.5]],3.4)
road('market-street','street',[[25.8,21.5],[30,22.5],[36.8,22.5]],2.5)
road('inn-street','street',[[18.4,22.5],[14,24.8],[14,28.4]],2.2)
road('artisan-street','street',[[25.8,23.5],[27.5,28.9],[33.8,28.9]],2.0)
road('domestic-lane','street',[[14,28.4],[14,32.5],[29.8,32.5]],1.8)
road('south-connection','street',[[20.95,32.5],[20.95,34.0]],1.8)
road('south-passage','street',[[20.95,34],[20.95,40]],1.0)
road('shrine-lane','street',[[26.0,17],[28.0,14.2],[32.8,14.2]],1.7)
road('north-street','street',[[16.2,15.5],[14.8,11.5],[14.8,5.8],[20.55,5.8]],1.8)
road('north-passage','street',[[20.55,5.8],[20.55,-3]],1.0)
road('service-lane','service',[[34.8,22.5],[36.8,25.0],[36.8,30.3],[29.8,32.5]],1.0)
road('residential-access','service',[[23,26.5],[23,32.5]],1.0)
plaza=[[17.4,16.2],[24.7,16.2],[27.2,19.4],[26.0,24.4],[17.5,24.4],[16.4,20.5]]
surface('orientation-plaza','plaza',plaza)

placements={
 'guild-hall':(21,12.7),'astral-fountain':(21.8,19.2),
 'caravan-gate':(8,23),'north-gate':(21.6,4.7),'south-gate':(22,36.8),
 'market-shop':(30,19.5),'east-house':(35,19.5),'west-house':(10.8,14.8),
 'food-market':(32.4,22.2),'market-crates':(34.7,23.8),'caravan-cart':(35.7,25.9),
 'east-cart':(10,25.0),'artisan-workshop':(31,27.5),'east-inn':(13.5,26.3),
 'moon-shrine':(30.8,11.3),'residence':(17,30.7),'willow-house':(23.4,30.7),
 'north-house':(29.8,30.7),'guild-board':(23.8,15.0),
 'planter-a':(18.0,16.0),'planter-b':(25.1,16.0),
 'bench-a':(17.7,23.7),'bench-b':(25.7,24.0),
}
trees=[(3.4,26),(10.6,28.9),(10.5,9),(26.8,7),(35.6,10.6),(35.5,14.0),
       (27.2,9.0),(8.8,29.7),(12,33.5),(33,32.8),(37.5,27.8),(34.5,34.6),
       (16.5,8),(14,7.5),(25.6,7.5),(26.5,12.6),(36.9,18.9),(38.0,22.5),
       (17,35),(28.2,35.1),(4.2,18.1),(9.1,11.1)]
tree_ids=[o['id'] for o in old['content']['townObjects'] if o.get('tree')]
placements.update(dict(zip(tree_ids,trees)))
ground={
 'civic':[[.06,.82],[.58,.69],[.96,.83],[.45,.98]],
 'shop':[[.09,.86],[.50,.73],[.94,.86],[.56,.99]],
 'forge':[[.03,.83],[.54,.65],[.97,.78],[.58,.99]],
 'inn':[[.12,.80],[.62,.65],[.96,.78],[.58,.99]],
 'shrine':[[.09,.88],[.60,.70],[.93,.84],[.44,.98]],
 'cottage':[[.12,.83],[.65,.70],[.93,.83],[.55,.97]],
}
def inverse(sx,sy):return [(22*sx+32*sy)/1504,(48*sy-14*sx)/1504]
def extrude(c,id,polygon,bottom,top,role):
 n=len(polygon);vs=[(x,y,z) for z in [bottom,top] for x,y in polygon]
 return mesh(c,id,vs,[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],'stone',role,True)
def child_anchor(c,root,id,xy,kind,data=None,z=0):
 o=empty(c,id,(xy[0]-root.location.x,xy[1]-root.location.y,z),kind);o.parent=root
 if data:o['data_json']=json.dumps(data)
 return o

for record in old['content']['townObjects']:
 id=record['id'];c=bpy.data.collections[id];root=bpy.data.objects[id+'-placement']
 root.location=(*placements.get(id,(record['x'],record['y'])),0)
 sprite=json.loads(root['data_json'])
 if id in ['north-gate','south-gate']:sprite.update(w=250,h=311)
 if id=='north-house':sprite.update(w=245,h=242)
 if id=='east-house':sprite.update(w=250,h=375)
 if id=='west-house':sprite.update(w=220,h=301)
 root['data_json']=json.dumps(sprite)
 for o in list(c.objects):
  if o!=root:bpy.data.objects.remove(o,do_unlink=True)
 m=old['metadata'].get(id)
 if m:
  m=json.loads(json.dumps(m));m.pop('collision',None);m.pop('footprint',None)
  m['entrance']=[0,1.4];m['layers']=[{**l,'depth':[l['depth'][0]-record['x'],l['depth'][1]-record['y']]} for l in m['layers']]
  m['renderAnchor']=[.4,.91] if id=='guild-hall' else [(.42 if sprite['art']=='shrine' else .43 if sprite['art']=='inn' else .5),.94] if sprite.get('pack')=='district' else old['content']['atlas'][sprite['art']]['anchor']
 if sprite.get('building') and sprite['art']!='gate':
  key='civic' if id=='guild-hall' else sprite['art'];outline=ground[key];ax,ay=m['renderAnchor']
  polygon=[inverse((x-ax)*sprite['w'],(y-ay)*sprite['h']) for x,y in outline]
  # Explicit registered foundation plane. Neither transparent extent nor roof size is a blocker.
  height=sprite['h']*.73/35
  body=extrude(c,id+'-body',polygon,0,height*.62,'solid');body.parent=root
  roof=extrude(c,id+'-overhead',polygon,height*.62,height,'overhead');roof.parent=root
  m['groundPolygon']=outline
  depths=[14*x+22*y for x,y in polygon];rear=min(range(len(depths)),key=depths.__getitem__);front=max(range(len(depths)),key=depths.__getitem__)
  m['layers'][0]['depth']=polygon[rear];m['layers'][1]['depth']=polygon[front];m['layers'][2]['depth']=polygon[front]
  m['layers'][2]['visibility']='selective-overhead'
  root['footprint_review']='registered physical foundation; reviewed in Golden gameplay camera'
  surface(id+'-forecourt','forecourt',[[-2.3,.9],[2.9,.9],[3.1,2.9],[-2.3,2.9]],root)
  # Door services use the clear frontage, not a point buried inside the foundation.
  approach=child_anchor(c,root,id+'-approach',(root.location.x,root.location.y+2.0),'approach')
  portal=child_anchor(c,root,id+'-entrance',(root.location.x,root.location.y+1.3),'portal');portal['approach_id']=approach.name;portal['range']=1.5
 elif sprite['art']=='gate':
  m['layers']=[];m['groundPolygon']=None
  pillar_regions=[[.015,.87,.17,.91,.365,.83,.27,.79],[.51,.9,.70,.94,.935,.88,.80,.84]]
  for index,coords in enumerate(pillar_regions):
   polygon=[inverse((coords[i]-.5)*sprite['w'],(coords[i+1]-.93)*sprite['h']) for i in range(0,8,2)]
   o=extrude(c,id+'-pillar-'+str(index),polygon,0,5.5,'solid');o.parent=root
  # Semantic source partitions cover the painting exactly once. Towers remain opaque.
  m['layers']=[{'name':'left-pillar','region':[0,0,.39,1],'depth':[-1.5,.6]},
               {'name':'right-pillar','region':[.59,0,1,1],'depth':[1,.1]},
               {'name':'span','region':[.39,0,.59,1],'depth':[0,.5],'visibility':'selective-overhead'}]
  bridge=extrude(c,id+'-span',[[-1.8,-1.4],[.6,-1.4],[.6,.1],[-1.8,.1]],3.7,4.5,'overhead');bridge.parent=root
  root['footprint_review']='two registered stone pillars; opening has no ground blocker'
 elif sprite.get('tree'):
  # Small physical root, independent of canopy extent.
  polygon=[[math.cos(i*math.tau/8)*.20,math.sin(i*math.tau/8)*.20] for i in range(8)]
  trunk=extrude(c,id+'-trunk',polygon,0,1.8,'solid');trunk.parent=root
  canopy=extrude(c,id+'-canopy',[[x*3.2,y*3.2] for x,y in polygon],1.8,4,'overhead');canopy.parent=root
  m['layers']=[{'name':'trunk','region':[0,.66,1,1],'depth':[0,0]},
               {'name':'rear-canopy','region':[0,0,.55,.66],'depth':[.15,.25],'visibility':'selective-overhead'},
               {'name':'front-canopy','region':[.55,0,1,.66],'depth':[.35,.45],'visibility':'selective-overhead'}]
  root['footprint_review']='physical root only; overhead canopy is walkable'
 else:
  # Existing decorations stay decorative except the physical fountain basin.
  if id=='astral-fountain':
   poly=[[math.cos(i*math.tau/12)*.94,math.sin(i*math.tau/12)*.78] for i in range(12)]
   o=extrude(c,id+'-basin',poly,0,.7,'solid');o.parent=root
  else:
   o=kit['box'](c,id+'-marker',(0,0,.01),(.04,.04,.02),'stone','decorative',False);o.parent=root
  root['footprint_review']='fountain basin' if id=='astral-fountain' else 'decorative furnishing'
 if m:root['structure_json']=json.dumps(m)

# Authored spaces fill the old unassigned lawn gaps. Keep vegetation bounded to
# gardens and outer framing; leave the civic sightline and street mouths clear.
for id,role,points in [
 ('civic-terrace','forecourt',[[16,13.4],[26.2,13.4],[26.2,16.8],[16.7,16.8]]),
 ('market-browsing','market',[[27.7,20.2],[37.2,20.2],[37.2,24.3],[27,24.3]]),
 ('forge-workyard','yard',[[27.2,28.1],[35.9,28.1],[36.6,30.8],[27.7,30.8]]),
 ('inn-courtyard','forecourt',[[10.5,27.3],[16.7,27.3],[17,29.5],[10.5,29.5]]),
 ('shrine-garden','garden',[[26.4,7],[37.4,7],[37.4,15.5],[26.4,15.5]]),
 ('domestic-garden','garden',[[11.2,33.7],[34.6,33.7],[34.6,36.3],[11.2,36.3]]),
 ('west-public-green','green',[[3,12],[9,9],[13.5,10],[13.5,17],[9,18],[3,17]]),
 ('arrival-forecourt','forecourt',[[5.4,24],[10.5,24],[11.5,27.3],[5.4,27.3]]),
 ('south-public-green','green',[[16.1,25.3],[26,25.3],[26,28.9],[16.1,28.9]]),
]:surface(id,role,points)

services=[
 ('guild-hall','guild-registrar','Guild Registrar','guild','✦',(19.7,14.8)),
 ('guild-hall','quest-board','Quest Board','journal','📜',(23.8,15.0)),
 ('market-shop','merchant','Merchant','market','✧',(31.3,23.7)),
 ('artisan-workshop','artisan','Artisan','craft','⚒',(30.8,29.4)),
 ('residence','housing-keeper','Housing Keeper','housing','⌂',(17.9,32.0)),
 ('caravan-gate','gatekeeper','Gatekeeper','travel','◇',(9.5,26.7)),
]
for parent,id,name,kind,symbol,xy in services:
 root=bpy.data.objects[parent+'-placement'];child_anchor(bpy.data.collections[parent],root,id,xy,'service',{'name':name,'kind':kind,'symbol':symbol})
walkers=[('caravan-gate','guard-1',[[6.9,24.6],[6.9,20],[9.7,19.1],[10.5,21]],.58,0),
         ('caravan-gate','guard-2',[[5.4,25.3],[10.2,27.5],[11.0,25.0]],.54,0),
         ('market-shop','customer-1',[[28.7,23],[30.5,24.5],[33.4,24.3],[29.7,25]],.46,45)]
for parent,id,points,pace,tint in walkers:
 root=bpy.data.objects[parent+'-placement'];o=child_anchor(bpy.data.collections[parent],root,id,tuple(root.location[:2]),'walker',{'pace':pace,'tint':tint})
 o['route_json']=json.dumps([[x-root.location.x,y-root.location.y,0] for x,y in points])
for parent,id,anchor,approach,to,label,glyph,arrival in [
 ('caravan-gate','west-field-transition',(6.95,27),(6.95,24.6),2,'Goldenfield Road','↙',[2.5,14]),
 ('north-gate','forest-transition',(20.55,2.0),(20.55,5.8),1,'Moonbamboo Trail','↑',[14.5,24]),
]:
 root=bpy.data.objects[parent+'-placement'];c=bpy.data.collections[parent]
 a=child_anchor(c,root,id+'-approach',approach,'approach')
 p=child_anchor(c,root,id,anchor,'portal');p['approach_id']=a.name;p['range']=.9;p['transition_json']=json.dumps({'to':to,'label':label,'glyph':glyph,'arrival':arrival})

# Fixture coordinates are registered to visible painted lamps/forge fire. Z is
# explicit; ground pools follow the source, never a generic building centre.
for id,fixtures in {'guild-hall':[(.30,.58,3.0,'#ffd993'),(.65,.50,3.7,'#ffd993')],
                    'artisan-workshop':[(.40,.70,1.8,'#ffb45c')],
                    'east-inn':[(.46,.76,1.6,'#ffdb9b')],
                    'moon-shrine':[(.34,.77,2.0,'#d9e8dc')]}.items():
 root=bpy.data.objects[id+'-placement'];sprite=json.loads(root['data_json']);m=json.loads(root['structure_json']);ax,ay=m['renderAnchor']
 for j,(u,v,z,color) in enumerate(fixtures):
  xy=inverse((u-ax)*sprite['w'],(v-ay)*sprite['h']+35*z)
  o=empty(bpy.data.collections[id],id+'-emitter-'+str(j),(*xy,z),'light');o.parent=root;o['color']=color;o['radius']=.65

scene['layout_id']='wayfarer-golden-v1';scene['purpose']='Golden Wayfarer playable redesign: west arrival, civic plaza, functional districts'
scene['spawn_json']=json.dumps([6.95,24.6,0])
scene['safe_spawn_json']=json.dumps([21.8,22.6,0])
scene['districts_json']=json.dumps([{'name':name,'x':x,'y':y} for name,x,y in [('Consortium Hall',21,12.7),('Wayfarer Plaza',21.8,20),('Lantern Market',32,22.5),('Bronze Anvil',31,28.7),('Seafarer Rest',13.5,27.8),('Moon Shrine',31,13.7),('Willow Quarter',23,32.5),('West Arrival',7,24.5)]])
scene['route_json']=json.dumps([{'name':name,'position':xy} for name,xy in [('Arrival',[6.95,24.6]),('Main avenue',[11.5,18.5]),('Plaza',[21.8,22.6]),('Hall',[21,15]),('Market',[29,23]),('Blacksmith',[30.8,29.4]),('Inn',[13.5,28.4]),('Residential',[23.4,32.5]),('Shrine',[31,14.1])]])
camera=bpy.data.objects['CourtReviewCamera'];direction=Vector((48,-32,0)).cross(Vector((14,22,-35))).normalized();camera.location=Vector((21,20,0))+direction*70;camera.data.ortho_scale=38
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-court.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
