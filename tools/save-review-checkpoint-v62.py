"""Preserve verified current gameplay stills, hashes and separate quality gates."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TEMP=Path('C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation');OUT=ROOT/'docs/review/wayfarer-v49'
for name in ['plaza','market','residential','inn','hall-terrace']:shutil.copy2(TEMP/'v62-town'/f'{name}.png',OUT/f'{name}-cache62.png')
shutil.copy2(TEMP/'v62-town/views.json',OUT/'views-cache62.json');shutil.copy2(TEMP/'v62-performance.json',OUT/'performance-cache62.json')
summary=json.loads((OUT/'summary.json').read_text());summary.update(runtimeCache=62,nodeTestsPassed=94,publicSchemas='PASS62',savedSourceParity='PASS62; shared Hall transform and stale-bake invalidation pass',geometry={'objects':118,'bakedCorners':337231,'bakedMeshes':8251},latestGeometry='12 recessed attic bays, structural gables and roof crowns; lower footprints/entry anchors retained',locomotionDiagnosis='../locomotion-v61/summary.json',cosmetics='Not implemented; original appearance/attachment/ownership contract recorded in research/character-locomotion-and-cosmetics.md')
for record in summary['files'].values():
    p=ROOT/record['path'];record.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
summary['lighting']=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())['lighting'];summary['gameplay']['scope']='59 stairs/gates/field/save coverage retained for unchanged ground lots/navigation.62 attic geometry is overhead only;94Node/schema/source parity pass. Actual62 still review and isolated62 performance recorded.'
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('''# Wayfarer candidate checkpoint — runtime62

Cache62 images are actual gameplay at zoom160/yaw25/pitch46. The current pass adds12 recessed attic bays and structural roof crowns, following the preceding deeper upper floors, repaired side façades and .72sun/.36coolfill. Both source light bakes are refreshed. Source/export parity,94Node tests and public schemas pass. `performance-cache62.json` measures the current geometry/runtime on the desktop; it does not certify other devices or anatomical animation.

The approved concept controls original architecture/layout; local RO3 Prontera screenshots remain the primary presentation comparison. **Town and locomotion remain below Golden acceptance.** Older cache52/53/60 images and59 behavior coverage are historical/scoped rather than replacements for the current screenshots. Ground lots, service entrances and navigation did not change in the attic pass.

`../locomotion-v61/` preserves all72 actual gait/direction captures as nine pose sheets, measured timing summaries and selected slow previews. The mode-switch queue defect is repaired and tested, but the painted contact/body/weapon sequence still fails. No replacement character assets are installed. The user requests simple grounded RO1-like movement after town work and interchangeable original costumes, hats and wings; the appearance contract is documented, with no cosmetic shop/payments implemented yet.
''',encoding='utf-8')
print('Saved verified62 stills/performance/current source hashes; visual and gait gates remain false')
