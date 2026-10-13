import base64,json
from pathlib import Path
P=Path(__file__).resolve().parent;data=json.loads((P/'parts.json').read_text());source=json.loads(Path('research/sprite-animation/pickup-pilot-v31/source/source.json').read_text())
payload={'parts':data['parts'],'source':source,'images':{p['name']:'data:image/png;base64,'+base64.b64encode(Path(p['file']).read_bytes()).decode() for p in data['parts']}}
payload['source_images']=['data:image/png;base64,'+base64.b64encode(Path(f['path']).read_bytes()).decode() for f in source['frames']]
html='''<!doctype html><meta charset="utf-8"><title>Modular pickup rig</title><style>body{background:#182332;color:#edf0fa;font:16px system-ui;margin:24px}canvas{background:#283747;width:384px;height:512px;image-rendering:auto}button,input{font:inherit}pre{white-space:pre-wrap}</style><h1>Modular pickup / source-driven8keys</h1><canvas id="view" width="384" height="512"></canvas><p><input id="frame" type="range" min="0" max="7" value="0"><button id="play">Play once</button><label><input id="bones" type="checkbox">Authored rig guide</label></p><p id="status"></p><script>__RUNTIME__</script><script>const DATA=__DATA__,images={},canvas=document.getElementById('view'),ctx=canvas.getContext('2d');let index=0,ready=false,running=false,start=0;const poses=DATA.source.frames.map((_,i)=>ModularPickup.pose(DATA.source,i));
Promise.all(Object.entries(DATA.images).map(([n,src])=>new Promise(resolve=>{const im=new Image;im.onload=()=>{images[n]=im;resolve()};im.src=src}))).then(()=>{ready=true;draw()});
function draw(){if(!ready)return;const rows=ModularPickup.recipe(DATA.parts,poses[index]);ModularPickup.render(ctx,rows,images,document.getElementById('bones').checked);document.getElementById('status').textContent='frame'+(index+1)+' / '+poses[index].source_time_seconds.toFixed(3)+'s';document.getElementById('frame').value=index}
document.getElementById('frame').oninput=e=>{running=false;index=+e.target.value;draw()};document.getElementById('bones').onchange=draw;
function tick(t){if(!running)return;const elapsed=t-start;while(index<7&&poses[index+1].source_time_seconds*1000<=elapsed)index++;draw();if(elapsed>=1900){running=false;return}requestAnimationFrame(tick)}
document.getElementById('play').onclick=()=>{index=0;running=true;start=performance.now();requestAnimationFrame(tick)};
window.pickup={get ready(){return ready},poses,set(i){index=i;draw()},frame(i,bones=false){const rows=ModularPickup.recipe(DATA.parts,poses[i]);ModularPickup.render(ctx,rows,images,bones);return canvas.toDataURL('image/png')},data:DATA,get rows(){return ModularPickup.recipe(DATA.parts,poses[index])}};</script>'''
html=html.replace('<canvas id="view"', '<img id="source-view" width="384" height="512" alt="Actual CC0 source frame"><canvas id="view"')
html=html.replace('<button id="play">', '<select id="clock"><option value="source">Source clock / 1300ms</option><option value="game">Game timing / 700ms</option></select><button id="play">')
html=html.replace("document.getElementById('status').textContent=", "document.getElementById('source-view').src=DATA.source_images[index];document.getElementById('status').textContent=")
html=html.replace('const elapsed=t-start;', "const elapsed=t-start,game=document.getElementById('clock').value==='game',active=game?700:1300;")
html=html.replace('poses[index+1].source_time_seconds*1000<=elapsed', '(game?(index+1)*100:poses[index+1].source_time_seconds*1000)<=elapsed')
html=html.replace('elapsed>=1900', 'elapsed>=active+600')
html=html.replace("document.getElementById('play').onclick", "document.getElementById('clock').onchange=()=>{running=false;index=0;draw()};document.getElementById('play').onclick")
html=html.replace('get ready(){return ready}', 'get ready(){return ready},get running(){return running},get index(){return index}')
(P/'rig-preview.html').write_text(html.replace('__RUNTIME__',(P/'rig-runtime.js').read_text()).replace('__DATA__',json.dumps(payload,separators=(',',':')).replace('<','\\u003c')))
