"""Inspect render bytes, record provenance, and build a source-model review page."""
from pathlib import Path
import json
import hashlib
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/free-master-01'
DIRS=['S','SW','W','NW','N','NE','E','SE']
if json.loads((OUT/'source-validation.json').read_text())['status']!='TECHNICAL_PILOT_PASS':
    raise RuntimeError('Saved-source geometry/binding checks must pass before review capture')
checks=[]
def check(name,result,detail=None):checks.append({'name':name,'pass':bool(result),'detail':detail})
images={}
for name in DIRS:
    file=OUT/'grip-review'/(name+'.png')
    with Image.open(file) as img:
        alpha=img.getchannel('A');bounds=alpha.getbbox()
        check(name+' registered RGBA canvas',img.mode=='RGBA' and img.size==(320,320),{'mode':img.mode,'size':img.size})
        check(name+' unclipped alpha',bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<320 and bounds[3]<320,{'alphaBounds':bounds})
        images[name]={'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'pixelHash':hashlib.sha256(img.tobytes()).hexdigest(),'alphaBounds':bounds}
with Image.open(OUT/'grip-review/NW.png') as a,Image.open(OUT/'grip-review/NW-repeat.png') as b:
    check('Repeated NW pixels identical',a.mode==b.mode and a.size==b.size and a.tobytes()==b.tobytes())
check('Eight independently rotated renders differ',len({i['pixelHash'] for i in images.values()})==8)
report={'status':'RENDER_CHECKS_PASS' if all(c['pass'] for c in checks) else 'RENDER_CHECKS_FAIL','checks':checks,'images':images,'visualApproval':False}
(OUT/'render-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if not all(c['pass'] for c in checks):raise RuntimeError('Render verification failed')

licenses=OUT/'licenses';licenses.mkdir(exist_ok=True)
upstream=ROOT/'.character-tools/mpfb-2.0.17/mpfb2-2.0.17'
for source,name in [('LICENSE.ASSETS.md','MPFB-core-assets-CC0.md'),('LICENSE.md','MPFB-license-boundary.md')]:
    shutil.copyfile(upstream/source,licenses/name)
receipt=json.loads((ROOT/'.character-tools/mpfb-2.0.17/download-receipt.json').read_text())
approved=ROOT/'authoring/characters/swordsman-production/fresh-2d/candidate-01/candidate.png'
provenance={'status':'UNAPPROVED_SOURCE_PILOT','upstream':receipt,'approvedConcept':{'path':approved.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(approved.read_bytes()).hexdigest(),'scope':'Parent painted concept only'},'authoring':'Local Blender geometry and weighted skeleton; no AI image cards or paid generation','excludedSources':['neutral mannequin','rejected turnaround','rejected painted-cutout rig'],'runtime3D':False,'paidCalls':0,'humanApproval':False}
provenance['scripts']={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'tools'/n for n in ['setup-free-character-source.py','probe-free-character-source.py','build-free-character-master.py','pose-free-character-grip.py','verify-free-character-source.py','inspect-free-character-master.py','review-free-character-source.py']]}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
proof=json.loads((OUT/'grip-proof.json').read_text())
cards=''.join(f'<article class="direction"><h3>{d} · yaw {proof["views"][i]["yawDegrees"]}°</h3><img class="source-image" src="grip-review/{d}.png" alt="{d} source model"><small>320 × 320 · root 160,264</small></article>' for i,d in enumerate(DIRS))
grips=''.join(f'<article><h3>{d} hand inspection</h3><img src="grip-review/hand-{d}.png" alt="{d} right glove and sword isolated"></article>' for d in ['W','NW','N','SE'])
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ASTRAEON — Free source-model checkpoint</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#101923;color:#eef3f7;font:16px/1.5 system-ui,sans-serif}main{max-width:1376px;margin:auto;padding:28px}h1{margin:0 0 6px;font-size:28px}h2{font-size:21px;margin:24px 0 12px}h3{font-size:16px;margin:0 0 8px}p{max-width:950px;color:#b9c8d7}a{color:#8ed5ff}.status{color:#ffd48d;border:1px solid #785f33;background:#30281b;padding:12px 16px;border-radius:9px}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}button{font:inherit;color:inherit;background:#263849;border:1px solid #4b647c;padding:7px 13px;border-radius:6px;cursor:pointer}button[aria-pressed=true]{border-color:#f7c765;color:#f7c765}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.direction{background:var(--surface,#192735);padding:14px 8px;text-align:center;border-radius:8px;border:1px solid #314557}.direction img{display:block;width:320px;height:320px;max-width:100%;object-fit:contain;margin:auto}.direction small{display:block;color:#a8bbcb}.light{--surface:#f3efe6}.light .direction{color:#182432}.light .direction small{color:#465b6d}.grips article{border:1px solid #3e5266;border-radius:8px;padding:10px;background:var(--surface,#192735)}.grips img{width:100%;display:block}.comparison{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.comparison article{background:var(--surface,#192735);border:1px solid #314557;border-radius:8px;padding:14px;text-align:center}.comparison img{height:320px;width:100%;object-fit:contain}.comparison .concept{height:430px}.facts{display:flex;gap:12px;flex-wrap:wrap}.facts span{background:#213142;border-radius:7px;padding:8px 12px;font-size:14px}.caption{margin:4px 0 16px;font-size:14px}#directions,#grips{padding:14px;background:#101923}#directions>p,#grips>p{margin-top:0}body.game-scale .direction img{width:160px;height:160px}body.large-scale .direction img{width:640px;height:640px}.light #directions,.light #grips{background:#e8e2d8}.light #directions>p,.light #grips>p{color:#324558}@media(max-width:850px){.grid,.comparison{grid-template-columns:repeat(2,1fr)}main{padding:16px}}
</style><main><h1>ASTRAEON · Free Blender source checkpoint</h1><div class="status">SOURCE MODEL PILOT — unapproved geometry, unfinished face/hair/materials. No finished sprite or factory completion claimed.</div>
<p>This fresh model uses a connected MPFB body and finger skeleton, with modeled clothing, hair and equipment. The painted concept remains the design authority. Review body proportions, the difficult sword views and source separation before expanding animation.</p>
<div class="facts"><span>No paid generation</span><span>Eight exact rotations</span><span>One fixed orthographic camera</span><span>320 × 320 · root 160,264</span><span>One uniform scale · height reference 176</span></div>
<div class="controls"><button id="dark" aria-pressed="true">Dark background</button><button id="light" aria-pressed="false">Light background</button><button id="authoring" aria-pressed="true">Authoring · 176 px height</button><button id="game" aria-pressed="false">Gameplay · 88 px height</button><button id="large" aria-pressed="false">Enlarge source</button></div>
<section id="directions"><h2>One pose · eight real character headings</h2><p class="caption">Geometry preview only. The camera stays fixed; the character rotates. No east/west image mirroring.</p><div class="grid">CARDS</div></section>
<section id="grips"><h2>Grip inspection · W / NW / N / SE</h2><p class="caption">Cape hidden in these close-ups to expose the hand. The full-character views above retain actual cape occlusion. Endpoint fit and binding tests do not approve anatomy or artwork.</p><div class="grid grips">GRIPS</div></section>
<h2>Source separation and reference</h2><div class="comparison"><article><h3>Approved painted concept</h3><img class="concept" src="../fresh-2d/candidate-01/candidate.png" alt="Approved painted concept"><p>Concept approval only.</p></article><article><h3>Current modeled source · SE</h3><img src="grip-review/SE.png" alt="Dressed source"><p>Pose and surface source, not finished painted art.</p></article><article><h3>Underlying body · SE</h3><img src="grip-review/body-without-outfit.png" alt="Body with outfit removed"><p>Hair remains. Source body and fingers are preserved under removable clothes.</p></article><article><h3>Alternate blade · SE</h3><img src="grip-review/alternate-sword-SE.png" alt="Alternate sword"><p>Same body, skeleton, grip and camera; blade geometry swapped.</p></article></div>
<p>Known remaining work: face and hair sculpt refinement toward the approved identity; garment construction details, cape emblem and painted material finish; motion library; depth-aware modular sprite exports; runtime validation and owner acceptance. This checkpoint provides no accepted animation coverage.</p>
<p><a href="grip-master.blend">Editable grip source</a> · <a href="source-master.blend">Editable modeling source</a> · <a href="source-validation.json">Geometry and binding checks</a> · <a href="render-validation.json">Render checks</a> · <a href="grip-proof.json">Camera and sockets</a> · <a href="provenance.json">Provenance</a></p>
<script>
function pressed(ids,active){ids.forEach(id=>document.getElementById(id).setAttribute('aria-pressed',id===active))}
document.getElementById('light').onclick=()=>{document.body.classList.add('light');pressed(['light','dark'],'light')};document.getElementById('dark').onclick=()=>{document.body.classList.remove('light');pressed(['light','dark'],'dark')};
for(const id of ['authoring','game','large'])document.getElementById(id).onclick=()=>{document.body.classList.toggle('game-scale',id==='game');document.body.classList.toggle('large-scale',id==='large');pressed(['authoring','game','large'],id)};
</script></main></html>'''.replace('CARDS',cards).replace('GRIPS',grips)
html=html.replace('Cape hidden in these close-ups to expose the hand. The full-character views above retain actual cape occlusion.','Right glove, bracer and sword isolated in these close-ups. Other anatomy, outfit and cape are hidden for diagnosis. The full-character views above retain actual occlusion.')
html=html.replace('max-width:1376px','max-width:1500px').replace('grid-template-columns:repeat(4,1fr)','grid-template-columns:repeat(auto-fit,minmax(338px,1fr))')
html=html.replace('</style>','.large-scale #directions .grid{grid-template-columns:repeat(auto-fit,minmax(658px,1fr))}.light .grips article,.light .comparison article{color:#182432}.light .comparison p{color:#465b6d}</style>')
(OUT/'review.html').write_text(html,encoding='utf-8')
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    page=browser.new_page(viewport={'width':1540,'height':1000},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto((OUT/'review.html').as_uri());page.wait_for_load_state('networkidle')
    page.locator('#directions').screenshot(path=str(OUT/'eight-direction-contact-sheet.png'))
    page.locator('#grips').screenshot(path=str(OUT/'grip-contact-sheet.png'))
    images_loaded=page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)')
    page.locator('#light').click();light=page.locator('body').evaluate('(e)=>e.classList.contains("light")')
    page.locator('#game').click();game=page.locator('.direction img').first.evaluate('(e)=>Math.round(e.getBoundingClientRect().height)')
    page.locator('#authoring').click();page.locator('#dark').click()
    page.screenshot(path=str(OUT/'review-page.png'),full_page=True)
    browser.close()
ui={'imagesLoaded':images_loaded,'lightControlWorks':light,'gameplayCanvasHeight':game,'pageErrors':errors,'pass':images_loaded and light and game==160 and not errors}
(OUT/'review-ui-validation.json').write_text(json.dumps(ui,indent=2),encoding='utf-8')
if not ui['pass']:raise RuntimeError('Review page verification failed')
manifest={str(p.relative_to(OUT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(OUT.rglob('*')) if p.is_file() and p.suffix!='.blend1' and p.name!='artifact-manifest.json'}
(OUT/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'renderChecks':len(checks),'ui':ui,'files':len(manifest)},indent=2))
