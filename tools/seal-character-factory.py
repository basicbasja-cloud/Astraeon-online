"""Seal completed factory evidence and create a local delivery archive."""
import hashlib,json,platform,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
recipe=read(OUT/'factory/recipe.json');package=read(OUT/'package.json');audit=read(OUT/'factory/source-audit.json');raster=read(OUT/'validation.json')
assert audit['technicalVerdict']==raster['technicalVerdict']=='PASS'
assert not package['missingActions'] and package['requiredFramePositionsRendered']==1392
native=ROOT/recipe['productionNative'];assert sha(native)==package['nativeSHA256']==audit['nativeSHA256']
integration=read(OUT/'factory/integration-evidence.json');assert integration['nativeSHA256']==package['nativeSHA256']
test_result=read(OUT/'factory/test-result.json');assert test_result['technicalVerdict']=='PASS' and test_result['testsRun']==5 and test_result['nativeSHA256']==package['nativeSHA256']
runtime_result=read(OUT/'factory/runtime-test-result.json');assert runtime_result['technicalVerdict']=='PASS' and runtime_result['nativeSHA256']==package['nativeSHA256']
assert len(integration['gripSamples'])==408
assert integration['trueHandHoldout']['samples']==408 and integration['trueHandHoldout']['opaqueCoveredPixels']>1000
assert integration['trueHandHoldout']['residualFraction']<.05
assert all(s['transparentHoles']==0 and s['revealedDifferentPixels']>100 for s in integration['capeRemoval'])
scripts=recipe['buildScripts']+[recipe['auditScript'],recipe['bakeScript'],recipe['packScript'],'inspect-fantasy-base.py','run-character-factory.py','check-fantasy-grip.py','render-fantasy-proof.py','verify-fantasy-delivery.py','seal-character-factory.py']
scripts+=['build-fantasy-swap-bank.py','bake-fantasy-swap-bank.py','compile-fantasy-runtime.py','verify-fantasy-runtime.py']
scripts+=['fetch-free-quaternius-motions.py','inspect-free-motion-rigs.py','extract-free-motion-samples.py','make-fantasy-review-media.py']
files=[ROOT/'tools'/name for name in scripts]+[ROOT/'tests/test_fantasy_sprite_package.py']
support=[ROOT/recipe['approvedConcept'],ROOT/'authoring/characters/swordsman-production/fresh-2d/candidate-01/CONCEPT_APPROVAL.md',
         ROOT/'authoring/characters/swordsman-production/reference-fit-01/fit-spec.json',ROOT/'authoring/characters/true-modular/swordsman/male/blueprint.json',
         ROOT/'docs/character-factory/new-production-matrix.json',ROOT/'docs/character-factory/RESEARCH_COHERENT_SPRITE_AUTHORING_V2.md']
support+=[ROOT/'modular-sprites.js',ROOT/'world-view.js',ROOT/'character-renderer.js',ROOT/'animation.js',ROOT/'tools/pack-modular-sprites.py',ROOT/'tools/validate-sprites.py',ROOT/'tools/validate-modular-metadata.cjs',ROOT/'assets/characters/schemas/sprite-definition.schema.json']
support+=[ROOT/'boot.js',ROOT/'proof/swordsman-development.js',ROOT/'proof/fantasy-game.html',ROOT/'docs/character-factory/RESEARCH_FREE_MOTIONS_20261011.md']
receipt={'sealedAtUTC':datetime.now(timezone.utc).isoformat(),'nativeSHA256':sha(native),'archiveSHA256':recipe['sourceArchiveSHA256'],
         'approvedConceptSHA256':recipe['approvedConceptSHA256'],'python':platform.python_version(),'blender':'5.2.2 LTS',
         'scripts':{p.relative_to(ROOT).as_posix():sha(p) for p in files},'requiredFramePositions':1392,'totalFramePositions':1456,
         'technicalVerdict':'PASS','visualVerdict':'REQUIRES_OWNER_ART_REVIEW','ownerApproved':False,'runtimeAdmitted':False,
         'sourceScope':'Owner-supplied local input; archive has no license document. Raw source excluded from public package.',
         'originalConceptPixelsUnchanged':sha(ROOT/recipe['approvedConcept'])==recipe['approvedConceptSHA256']}
write(OUT/'factory/build-receipt.json',receipt)
write(OUT/'artifact-manifest.json',{p.relative_to(OUT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json'})
dest=ROOT/'.character-tools/deliveries/ASTRAEON_first_sprite_production.zip';dest.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as archive:
    for path in sorted(OUT.rglob('*')):
        if path.is_file():archive.write(path,path.relative_to(ROOT).as_posix())
    for path in files:archive.write(path,path.relative_to(ROOT).as_posix())
    for path in support:archive.write(path,path.relative_to(ROOT).as_posix())
    archive.write(native,recipe['productionNative'])
    archive.write(ROOT/'.character-tools/checkpoints/fantasy-swap-bank.blend','.character-tools/checkpoints/fantasy-swap-bank.blend')
print(json.dumps({'delivery':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'receipt':receipt},indent=2))
