const test=require('node:test'),assert=require('node:assert/strict');
global.window={};require('../world-content.js');require('../world-view.js');require('../town-structure.js');require('../directional-metadata.js');require('../hero-registration.js');require('../warrior-gait.js');require('../sprite-motion.js');
test('all eight directions retain an opposite leg contact half a cycle later',()=>{
 const data=window.AstraeonHeroRegistration['warrior-walk'];
 for(let row=0;row<8;row++)for(let frame=0;frame<4;frame++){
  const left=data.frames[row*8+frame],right=data.frames[row*8+frame+4];
  assert.equal(left.contacts[0].stance,right.contacts[1].stance);
  assert.equal(left.contacts[1].stance,right.contacts[0].stance);
  assert.equal(left.visibleBodyHeight,right.visibleBodyHeight);
  assert.deepEqual([left.footAnchorX,left.footAnchorY],[96,174]);
  assert.notDeepEqual(left.contacts,right.contacts);
 }
});
test('opaque architecture layers cover the source exactly once and carry independent depths',()=>{
 const S=window.AstraeonTownStructure,m=S.metadata['guild-hall'];
 const inside=(polygon,x,y)=>{let hit=false;for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){const a=polygon[i],b=polygon[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit}return hit};
 for(const object of Object.values(S.metadata))for(let x=.025;x<1;x+=.05)for(let y=.025;y<1;y+=.05){assert.equal(object.layers.filter(l=>{const [a,b,c,d]=l.region;return x>=a&&x<c&&y>=b&&y<d&&(!l.polygon||inside(l.polygon,x,y))&&(!l.exclude||!inside(l.exclude,x,y))}).length,1)}
 assert.notDeepEqual(m.layers[0].depth,m.layers[1].depth);
 const actors=S.layers(window.AstraeonContent.townObjects);assert.ok(actors.length>window.AstraeonContent.townObjects.length);
});
test('raw walk playback adds no root bob, lean or stretch',()=>{
 for(let p=0;p<1;p+=.025)assert.deepEqual(window.AstraeonSpriteMotion.sample('walk',0,.45,p,4),{x:0,lift:0,lean:0,stretch:1});
});
