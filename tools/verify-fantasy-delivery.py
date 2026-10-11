"""Run the delivered package's integration checks and retain their verdict."""
import json,sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'authoring/characters/swordsman-production/fantasy-base-01'
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_fantasy_sprite_package.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'technicalVerdict':'PASS' if result.wasSuccessful() else 'FAIL','testsRun':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),
        'nativeSHA256':json.loads((out/'package.json').read_text())['nativeSHA256'],
        'visualVerdict':'REQUIRES_OWNER_ART_REVIEW'}
(out/'factory/test-result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
sys.exit(0 if result.wasSuccessful() else 1)
