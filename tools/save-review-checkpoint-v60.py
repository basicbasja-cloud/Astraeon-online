"""Preserve current gameplay evidence and honest scopes, never art approval."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TEMP=Path('C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation');OUT=ROOT/'docs/review/wayfarer-v49';OUT.mkdir(parents=True,exist_ok=True)
for name in ['plaza','residential','hall-terrace','arrival','gate-spillways']:shutil.copy2(TEMP/'v60-town'/f'{name}.png',OUT/f'{name}-cache60.png')
for src,dst in [(TEMP/'v60-town/views.json','views-cache60.json'),(TEMP/'v59-spatial/report.json','spatial-cache59.json'),(TEMP/'v59-performance.json','performance-cache59.json')]:shutil.copy2(src,OUT/dst)
files={}
for key,path in [('blend','authoring/wayfarer-spatial.blend'),('world','world/v3/wayfarer-spatial.json'),('renderer','world/v3/renderer.js'),('actorAdapter','animation.js')]:
    p=ROOT/path;files[key]={'path':path,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
world=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());spatial=json.loads((TEMP/'v59-spatial/report.json').read_text())
summary={'candidate':True,'runtimeCache':60,'townLayout':world['layoutId'],'visualAcceptance':False,'locomotionAcceptance':False,'nodeTestsPassed':75,'publicSchemas':'PASS59','savedSourceParity':'PASS59; source60 lighting/bake parity pending','geometry':{'objects':len(world['objects']),'bakedCorners':329419,'bakedMeshes':7933},'files':files,'lighting':world['lighting'],'gameplay':{'cache':59,'spatialCases':len(spatial['evidence']),'errors':spatial['runtime_errors'],'resourceErrors':spatial['resource_errors'],'scope':'13 stairs/gates, field transfer and save reload. Cache60 changes light/fill/bake only, not navigation or geometry.'},'references':{'identityLayoutArchitecture':'Approved original Wayfarer concept','primaryPresentation':'Local RO3 Prontera screenshots','animationFeel':'Supplied RO3 video reviewed at quarter speed; robe limits exact contact measurements'},'limits':['Town architecture/composition/presentation remains below visual acceptance.','No new character art installed. Existing loops fail visible alternation/weapon/crop/root gates.','75 tests and continuous root motion never approve anatomical gait.','Desktop Radeon780M/Chrome D3D11 performance is not phone certification.','Atlas/GIF evidence and instrumented gameplay capture have different scopes.']}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'README.md').write_text('''# Wayfarer candidate checkpoint — runtime60

The cache60 images are actual gameplay views at zoom160/yaw25/pitch46. They show the source-owned upper-floor/roof extensions, repaired corner-post slabs, recessed side windows and stronger .72sun/.36fill balance. The concept controls original architecture/layout; RO3 screenshots remain the primary presentation comparison. **Town and locomotion are not Golden-approved.**

`spatial-cache59.json` and `performance-cache59.json` cover the current geometry/navigation; cache60 only changes sunlight/fill and its native floor bake. Earlier cache52/53 evidence is retained as history and does not represent the current screenshot checkpoint. Raw videos are in the local temporary preparation folder, rather than added to Git.

Locomotion is a critical blocker. Read-only whole-cycle previews and actual pose-change/RAF captures reveal incomplete leg alternation, weapon changes, adjacent-row crop fragments and missing Mage/Ranger root registration. Runtime timing is being diagnosed before any further character asset generation or replacement. Root continuity is a separate check from visible foot/body continuity.
''')
print('Saved cache60 stills/current hashes and scoped59 behavior/performance; visual gates remain false')
