/* Small bounded A* for click-to-move. Collision coordinates never become visual tiles. */
(() => {
'use strict';
const length=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
function clear(a,b,blocked){const distance=length(a,b),steps=Math.ceil(distance/.18);for(let i=1;i<=steps;i++){const t=i/steps;if(blocked(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t))return false}return true}
class Heap{
 constructor(){this.items=[]}
 push(node){const a=this.items;a.push(node);let i=a.length-1;while(i){const p=(i-1)>>1;if(a[p].score<=node.score)break;a[i]=a[p];i=p}a[i]=node}
 pop(){const a=this.items,first=a[0],last=a.pop();if(a.length){let i=0;while(i*2+1<a.length){let c=i*2+1;if(c+1<a.length&&a[c+1].score<a[c].score)c++;if(a[c].score>=last.score)break;a[i]=a[c];i=c}a[i]=last}return first}
}
function route(start,goal,blocked,{reach=.3,bounds={minX:1,maxX:28,minY:1,maxY:25}}={}){
 if(clear(start,goal,blocked))return [{x:goal.x,y:goal.y}];
 const step=.5,key=(x,y)=>x+','+y,heap=new Heap(),cost=new Map(),closed=new Set(),nodes=new Map();let seed=null;
 for(let ox=-1;ox<=1;ox++)for(let oy=-1;oy<=1;oy++){const x=Math.round(start.x/step)+ox,y=Math.round(start.y/step)+oy,p={x:x*step,y:y*step};if(blocked(p.x,p.y)||!clear(start,p,blocked))continue;if(!seed||length(start,p)<length(start,seed.point))seed={x,y,point:p,cost:length(start,p),parent:null}}
 if(!seed)return null;seed.score=seed.cost+Math.max(0,length(seed.point,goal)-reach);heap.push(seed);cost.set(key(seed.x,seed.y),seed.cost);nodes.set(key(seed.x,seed.y),seed);
 const dirs=[[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]];
 for(let visits=0;heap.items.length&&visits<6000;visits++){
  const node=heap.pop(),id=key(node.x,node.y);if(closed.has(id))continue;closed.add(id);
  // A clear off-grid destination must not become unreachable merely because
  // every half-unit node is farther away than the requested stopping radius.
  const distance=length(node.point,goal),finish=distance<=step*Math.SQRT2&&!blocked(goal.x,goal.y)&&clear(node.point,goal,blocked);
  if(distance<=reach+.025||finish){const path=[];let current=node;while(current){path.push(current.point);current=current.parent}path.reverse();if(finish)path.push({x:goal.x,y:goal.y});const simplified=[];let anchor=start,index=0;while(index<path.length){let far=index;while(far+1<path.length&&clear(anchor,path[far+1],blocked))far++;simplified.push(path[far]);anchor=path[far];index=far+1}return simplified}
  for(const [dx,dy] of dirs){const x=node.x+dx,y=node.y+dy,p={x:x*step,y:y*step},neighbor=key(x,y);if(p.x<bounds.minX||p.x>bounds.maxX||p.y<bounds.minY||p.y>bounds.maxY||closed.has(neighbor)||blocked(p.x,p.y)||!clear(node.point,p,blocked))continue;const candidate=node.cost+Math.hypot(dx,dy)*step;if(candidate>=(cost.get(neighbor)??Infinity))continue;cost.set(neighbor,candidate);const next={x,y,point:p,cost:candidate,parent:node,score:candidate+Math.max(0,length(p,goal)-reach)};nodes.set(neighbor,next);heap.push(next)}
 }
 return null;
}
window.AstraeonNavigation={route,clear};
})();
