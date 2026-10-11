// Native-resolution diagnostic sprite exporter, not a production game adapter.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import assert from 'node:assert/strict';
import {bodyFaces} from './geometry.mjs';
import {DIRECTIONS,pose,poseTimeline,clipDuration,project,add,sub,length,STRIDE,PERIOD} from './motion.mjs';
const output=path.resolve(process.argv[2]||'/workspace/scratch/sprite-export-study');
fs.mkdirSync(output,{recursive:true});
const W=128,H=128,SCALE=64,ROOT=[64,104],PARTS=['body','hat','weapon','shield'];
const UNSET=-2147483648,DEPTH_SCALE=1000000;

// Minimal PNG writer for newly rasterized RGBA arrays. No existing image edits.
function crc32(bytes){let c=0xffffffff;for(const byte of bytes){c^=byte;for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xedb88320:0);}return (c^0xffffffff)>>>0;}
function chunk(kind,data){const name=Buffer.from(kind),len=Buffer.alloc(4),crc=Buffer.alloc(4);len.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(Buffer.concat([name,data])));return Buffer.concat([len,name,data,crc]);}
function png(rgba,width=W,height=H){
  const header=Buffer.alloc(13);header.writeUInt32BE(width,0);header.writeUInt32BE(height,4);header[8]=8;header[9]=6;
  const rows=Buffer.alloc(height*(width*4+1));for(let y=0;y<height;y++)Buffer.from(rgba.buffer,rgba.byteOffset+y*width*4,width*4).copy(rows,y*(width*4+1)+1);
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',header),chunk('IDAT',zlib.deflateSync(rows)),chunk('IEND',Buffer.alloc(0))]);
}
function projected(point,dir){const q=project(point,dir,46,0);return [ROOT[0]+q[0]*SCALE,ROOT[1]+q[1]*SCALE,q[2]];}
function triangle(a,b,c,color,result){
  const det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(det)<1e-10)return;
  const minX=Math.max(0,Math.floor(Math.min(a[0],b[0],c[0]))),maxX=Math.min(W-1,Math.ceil(Math.max(a[0],b[0],c[0])));
  const minY=Math.max(0,Math.floor(Math.min(a[1],b[1],c[1]))),maxY=Math.min(H-1,Math.ceil(Math.max(a[1],b[1],c[1])));
  for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){
    const px=x+.5,py=y+.5;
    const u=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/det;
    const v=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/det,w=1-u-v;
    if(u<-1e-8||v<-1e-8||w<-1e-8)continue;
    const depth=Math.round((u*a[2]+v*b[2]+w*c[2])*DEPTH_SCALE),i=y*W+x;
    if(depth>=result.depth[i]){result.depth[i]=depth;result.rgba.set(color,i*4);}
  }
}
function empty(){const depth=new Int32Array(W*H);depth.fill(UNSET);return {rgba:new Uint8Array(W*H*4),depth};}
function raster(faces,dir){
  const result=empty();
  for(const face of faces){const points=face.points.map(p=>projected(p,dir));const hex=face.color.slice(1),color=[parseInt(hex.slice(0,2),16),parseInt(hex.slice(2,4),16),parseInt(hex.slice(4,6),16),255];
    for(let i=1;i<points.length-1;i++)triangle(points[0],points[i],points[i+1],color,result);
  }
  return result;
}
function compose(layers){
  const result=empty();
  for(const layer of layers)for(let i=0;i<W*H;i++)if(layer.rgba[i*4+3]&&layer.depth[i]>=result.depth[i]){
    result.depth[i]=layer.depth[i];result.rgba.set(layer.rgba.subarray(i*4,i*4+4),i*4);
  }
  return result;
}
function decodedDepth(filename){const bytes=zlib.inflateSync(fs.readFileSync(filename));assert.equal(bytes.length,W*H*4);const depth=new Int32Array(W*H);for(let i=0;i<depth.length;i++)depth[i]=bytes.readInt32LE(i*4);return depth;}
function decodedPng(filename){
  const bytes=fs.readFileSync(filename),parts=[];let p=8;
  while(p<bytes.length){const n=bytes.readUInt32BE(p),kind=bytes.toString('ascii',p+4,p+8),data=bytes.subarray(p+8,p+8+n);assert.equal(crc32(bytes.subarray(p+4,p+8+n)),bytes.readUInt32BE(p+8+n));if(kind==='IDAT')parts.push(data);p+=n+12;}
  const rows=zlib.inflateSync(Buffer.concat(parts));assert.equal(rows.length,H*(W*4+1));const rgba=new Uint8Array(W*H*4);
  for(let y=0;y<H;y++){assert.equal(rows[y*(W*4+1)],0);rgba.set(rows.subarray(y*(W*4+1)+1,(y+1)*(W*4+1)),y*W*4);}return rgba;
}
function saveLayer(directory,name,layer){
  const image=path.join(directory,name+'.png'),depthFile=path.join(directory,name+'.depth-i32.deflate');fs.writeFileSync(image,png(layer.rgba));
  const bytes=Buffer.alloc(layer.depth.length*4);for(let i=0;i<layer.depth.length;i++)bytes.writeInt32LE(layer.depth[i],i*4);
  fs.writeFileSync(depthFile,zlib.deflateSync(bytes));return {image,depthFile};
}
const canonical={hat:'cap',coat:'blue',weapon:'sword',shield:'round'};
const stress={hat:'crest',coat:'red',weapon:'wand',shield:'large'};
const absent={hat:'none',coat:'blue',weapon:'none',shield:'none'};
const walk=poseTimeline('walk','60'),attack=poseTimeline('attack','60');
const specs=[{id:'canonical',appearance:canonical,clips:{idle:[0,.4],walk,attack}},
  {id:'stress',appearance:stress,clips:{walk:[0,.12,.24,.4],attack:[0,.2016,.2592,.3024]}},
  {id:'absent',appearance:absent,clips:{idle:[0]}}];
const manifest={schema:'diagnostic-depth-parts-v1',native:[W,H],root:ROOT,scale:SCALE,directions:DIRECTIONS,projection:{kind:'orthographic',pitch:46,cameraYaw:0},
  depth:{format:'little-endian signed int32, deflate',scale:DEPTH_SCALE,empty:UNSET,near:'larger',tiePriority:PARTS},alpha:'straight; binary opaque/transparent',
  fpsTarget:{walk:60,attack:60,idle:'two diagnostic holds'},scope:'Original geometric motion diagnostic; not production art',variants:[]};
let checks=0,pngCount=0,blankFrames=0;const contactSheet=new Uint8Array(W*8*H*4*4);const swapSheet=new Uint8Array(W*8*H*4*3);
function tile(sheet,columns,row,col,rgba){const width=columns*W;for(let y=0;y<H;y++)sheet.set(rgba.subarray(y*W*4,(y+1)*W*4),((row*H+y)*width+col*W)*4);}
const retained=new Map();
for(const spec of specs){
  const variant={id:spec.id,appearance:spec.appearance,clips:{}};manifest.variants.push(variant);
  for(const [action,times] of Object.entries(spec.clips)){
    variant.clips[action]={duration:clipDuration(action),complete:spec.id==='canonical'||action==='idle',frames:[]};
    for(let f=0;f<times.length;f++){
      const time=times[f],p=pose(action,time),faces=bodyFaces(p,spec.appearance),frame={time,duration:(times[f+1]??clipDuration(action))-time,directions:[]};variant.clips[action].frames.push(frame);
      for(let dir=0;dir<8;dir++){
        for(const face of faces)for(const point of face.points){const q=projected(point,dir);assert.ok(q[0]>=0&&q[0]<W&&q[1]>=0&&q[1]<H,`Clipped geometry ${spec.id} ${action} ${dir} ${f}`);}
        const directory=path.join(output,spec.id,action,DIRECTIONS[dir],String(f).padStart(3,'0'));fs.mkdirSync(directory,{recursive:true});
        const reference=raster(faces,dir),layers=[];const bindings={};
        for(const part of PARTS){const layer=raster(faces.filter(face=>face.part===part),dir),saved=saveLayer(directory,part,layer);pngCount++;
          const blank=!layer.rgba.some((v,i)=>i%4===3&&v>0);if(blank)blankFrames++;
          bindings[part]={image:path.relative(output,saved.image),depth:path.relative(output,saved.depthFile),blank};
          // Reconstruction is checked after encoding AND decoding the independent exports.
          layers.push({rgba:decodedPng(saved.image),depth:decodedDepth(saved.depthFile)});
        }
        const assembled=compose(layers);assert.deepEqual(assembled.rgba,reference.rgba,`${spec.id} ${action} ${dir} ${f}`);checks++;
        fs.writeFileSync(path.join(directory,'reference.png'),png(reference.rgba));pngCount++;
        frame.directions.push({direction:DIRECTIONS[dir],parts:bindings,footContacts:p.feet});
        if(spec.id==='canonical'&&action==='walk'&&[0,12,24,36].includes(f))tile(contactSheet,8,[0,12,24,36].indexOf(f),dir,reference.rgba);
        if(spec.id==='canonical'&&action==='walk'&&f===0)retained.set(dir,{p,layers});
        if(spec.id==='stress'&&action==='walk'&&f===0){
          // Independently generated substitute layers combine with the canonical body.
          const mixed=compose([retained.get(dir).layers[0],layers[1],layers[2],layers[3]]);
          const expected=raster(bodyFaces(p,{...stress,coat:'blue'}),dir);assert.deepEqual(mixed.rgba,expected.rgba,`mixed swap ${dir}`);
          tile(swapSheet,8,0,dir,raster(bodyFaces(p,canonical),dir).rgba);
          tile(swapSheet,8,1,dir,reference.rgba);tile(swapSheet,8,2,dir,mixed.rgba);checks++;
        }
      }
    }
  }
}
// Reuse independently rendered equipment across combinations and sampled actions.
let combinationChecks=0;
for(const action of ['walk','attack'])for(const time of action==='walk'?[0,.2,.4,.6]:[.2016,.2592,.3024])for(let dir=0;dir<8;dir++){
  const p=pose(action,time),body=raster(bodyFaces(p,canonical).filter(f=>f.part==='body'),dir),variants={};
  for(const [part,items] of Object.entries({hat:['cap','crest'],weapon:['sword','wand'],shield:['round','large']})){
    variants[part]=items.map(item=>raster(bodyFaces(p,{...canonical,[part]:item}).filter(f=>f.part===part),dir));
  }
  for(let h=0;h<2;h++)for(let w=0;w<2;w++)for(let s=0;s<2;s++){
    const mixed=compose([body,variants.hat[h],variants.weapon[w],variants.shield[s]]);
    const reference=raster(bodyFaces(p,{...canonical,hat:['cap','crest'][h],weapon:['sword','wand'][w],shield:['round','large'][s]}),dir);
    assert.deepEqual(mixed.rgba,reference.rgba,`Combination ${action} ${time} ${dir} ${h}${w}${s}`);combinationChecks++;
  }
}
fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(path.join(output,'walk-contact-sheet.png'),png(contactSheet,W*8,H*4));
fs.writeFileSync(path.join(output,'swap-reconstruction.png'),png(swapSheet,W*8,H*3));
const report={status:'passed',checks,combinationChecks,pngCount,blankFrames,walkPosesPerDirection:walk.length,attackPosesPerDirection:attack.length,
  nativeFrame:[W,H],root:ROOT,allEightDirections:true,decodedPartReconstruction:'byte-identical to same-rasterizer full reference',
  independentMixedSwapChecks:8,walkHoldDriftBoundPixels:STRIDE/walk.length*SCALE,
  limitations:['Original geometric diagnostic, not Ragnarok-like approved sprite art','Fixed elevation only','Binary-alpha depth composition; no antialiased or translucent surfaces',
    'Reference and parts share one rasterizer; comparison does not prove external renderer correctness','No trimmed atlas or target-game integration',
    'Stress action subsets are incomplete; not standalone shippable items','Contact bound excludes pixel rounding, starts/stops/turns and actual game movement'],
  output};
fs.writeFileSync(path.join(output,'export-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
