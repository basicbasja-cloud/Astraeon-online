/* Original diagnostic of current ASTRAEON authoring data, not game artwork. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const context = {window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root, 'world-content.js'), 'utf8'), context);
const c = context.window.AstraeonContent;
const game = fs.readFileSync(path.join(root, 'game.js'), 'utf8');
const npcDeclaration = game.match(/^const NPCS=(\[.*\]);$/m);
if (!npcDeclaration) throw new Error('NPCS authoring declaration changed; update reference extraction.');
const npcs = vm.runInNewContext(npcDeclaration[1]);
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const unit = 17, ox = 46, oy = 106;
const xy = (x,y) => `${ox+x*unit},${oy+y*unit}`;
const points = list => list.map(([x,y]) => xy(x,y)).join(' ');
const label = (x,y,s,cls='label') => `<text x="${x}" y="${y}" class="${cls}">${escape(s)}</text>`;
const colors = {avenue:'#d5bc83',street:'#b0b0a0',service:'#a88a64',field:'#a88a64'};
let out = `<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="880" viewBox="0 0 1160 880" role="img" aria-labelledby="title desc">
<title id="title">Wayfarer Court — current authored ground plan</title>
<desc id="desc">Original top-down diagnostic of ASTRAEON roads, plaza, collision blocks, sprite anchors and service NPC positions. It is not a perspective rendering or an art approval.</desc>
<style>text{font-family:system-ui,sans-serif;fill:#e6e5d8}.heading{font-size:24px;font-weight:700}.label{font-size:11px}.note{font-size:13px}.sub{font-size:14px;fill:#bac5bc}</style>
<defs><clipPath id="town"><rect x="46" y="106" width="748" height="680"/></clipPath><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#f4d681"/></marker></defs>
<rect width="1160" height="880" fill="#14252b"/>
${label(46,42,'WAYFARER COURT · authored ground plan','heading')}
${label(46,68,'Existing content only · world coordinates · +Y downward · not a finished scene illustration','sub')}
<rect x="46" y="106" width="748" height="680" fill="#3c5145" stroke="#92a69a"/>
<g clip-path="url(#town)">`;
for(let x=0;x<=44;x+=2) out+=`<path d="M${xy(x,0)}L${xy(x,40)}" stroke="#ffffff0a"/>`;
for(let y=0;y<=40;y+=2) out+=`<path d="M${xy(0,y)}L${xy(44,y)}" stroke="#ffffff0a"/>`;
for(const r of c.townRoads) out+=`<polyline points="${points(r.points)}" fill="none" stroke="${colors[r.role]}" stroke-width="${r.width*unit}" stroke-linejoin="round" stroke-linecap="round"/>`;
out+=`<polygon points="${points(c.goldenScene.plaza)}" fill="#c4b99b" stroke="#eee0b6"/>`;
// The present forecourt is authored in scene.js; extract its literal polygon.
const scene = fs.readFileSync(path.join(root, 'scene.js'), 'utf8');
const forecourt = scene.match(/polygon\(m,(\[\[6\.6,14\.8\].*?\]\]),p\);m\.fill\(\);/);
if (!forecourt) throw new Error('Forecourt authoring changed; update reference extraction.');
out+=`<polygon points="${points(JSON.parse(forecourt[1]))}" fill="#c4b99b" stroke="#eee0b6"/>`;
for(const b of c.townBlocks) out+=`<rect x="${ox+b.x*unit}" y="${oy+b.y*unit}" width="${b.w*unit}" height="${b.h*unit}" fill="${b.kind==='fountain'?'#447f8a':'#192d32'}" stroke="#ec9b8877"/>`;
out+=`<polyline points="${points(c.goldenScene.axis)}" fill="none" stroke="#f4d681" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#arrow)"/>`;
for(const o of c.townObjects){
 const x=ox+o.x*unit,y=oy+o.y*unit;
 out+=o.tree?`<circle cx="${x}" cy="${y}" r="7" fill="#7fa76b" stroke="#bdd69a"/>`:`<path d="M${x-3},${y}H${x+3}M${x},${y-3}V${y+3}" stroke="#e6d7b5" stroke-width="1.5"/>`;
 if(['guild-hall','north-house','market-shop','food-market','caravan-gate','artisan-workshop','moon-shrine','residence'].includes(o.id)) out+=label(o.id==='caravan-gate'?x-84:x+5,y-7,o.id);
}
for(const n of npcs){const x=ox+n.x*unit,y=oy+n.y*unit;out+=`<circle cx="${x}" cy="${y}" r="3.5" fill="#f6e1ad" stroke="#172c30"/>`;}
for(const w of c.walkers)out+=`<polyline points="${points([...w.route,w.route[0]])}" fill="none" stroke="${w.id.startsWith('guard')?'#98d1df':'#df9fc6'}" stroke-width="1.5" stroke-dasharray="3 3"/>`;
out+=`<circle cx="${ox+14.5*unit}" cy="${oy+18*unit}" r="5" fill="#fff" stroke="#172c30" stroke-width="2"/>`;
out+=`</g>`;
for(let x=0;x<=44;x+=4)out+=label(ox+x*unit-4,805,x);
for(let y=0;y<=40;y+=4)out+=label(22,oy+y*unit+4,y);
const notes=[
 ['READ THE PLAN',true],
 ['Tan wide route: 3.8-unit main avenue'],
 ['Grey: stone secondary streets'],
 ['Brown: soil service / field routes'],
 ['Outlined court: shared plaza paving'],
 ['Dark blocks: collision footprints'],
 ['Crosses: painted asset ground anchors'],
 ['Green circles: existing tree anchors'],
 ['Gold dots: functional services'],
 ['White dot: fresh Warrior spawn'],
 ['Dashed gold: intended primary axis'],
 ['Cyan loops: current court guards'],
 ['Pink loop: current market customer'],
 ['',false],
 ['SERVICE POSITIONS',true],
 ...npcs.map(n=>[`${n.name}: ${n.x}, ${n.y}`]),
 ['',false],
 ['GOLDEN REVIEW',true],
 ['Hall → court → market → eastern gate'],
 ['Keep fountain perimeter traversable.'],
 ['Pair facade, footprint and entrance edits.'],
 ['An art anchor is not a door or footprint.'],
 ['Guard loops currently serve the court.'],
 ['Inspect facade hierarchy in gameplay.'],
 ['Both Golden approvals remain pending.']
];
notes.forEach(([s,bold],i)=>{out+=label(823,119+i*23,s,bold?'sub':'note');});
out+=label(46,841,'Generated from world-content.js, scene.js and game.js · regenerate: node tools/reference-plan.cjs','sub');
out+=`</svg>\n`;
const target=path.join(root,'docs/reference/wayfarer-plan.svg');
fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,out);
console.log(`Wrote ${path.relative(root,target)}: ${c.townRoads.length} roads, ${c.townBlocks.length} collision blocks, ${c.townObjects.length} art anchors, ${npcs.length} services.`);
