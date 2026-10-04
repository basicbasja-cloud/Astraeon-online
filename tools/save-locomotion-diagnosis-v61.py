"""Save scoped observed evidence without changing production character assets."""
import json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TEMP=Path('C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation');OUT=ROOT/'docs/review/locomotion-v61';OUT.mkdir(parents=True,exist_ok=True)
records=[]
for character in ['warrior','mage','ranger']:
    report=json.loads((TEMP/f'locomotion60-{character}/locomotion-audit.json').read_text())
    for case in report['cases']:
        r={k:v for k,v in case.items() if k not in ['changes']};r['character']=character;records.append(r)
    for mode in ['walk','run','sprint']:shutil.copy2(TEMP/'locomotion-qa-sheets'/f'locomotion60-{character}-{mode}-all-directions.png',OUT/f'{character}-{mode}-all-directions.png')
transition=json.loads((TEMP/'locomotion61-transitions/locomotion-audit.json').read_text())['transitions']
transition.pop('changes',None)
for character,case in [('warrior','walk-d'),('warrior','sprint-sa'),('mage','walk-d'),('ranger','walk-s')]:
    source=TEMP/f'locomotion60-{character}/motion-series'/case
    for name in ['recorded.gif','quarter-speed.gif','first-nine-transitions.png']:shutil.copy2(source/name,OUT/f'{character}-{case}-{name}')
atlas=json.loads((TEMP/'locomotion59-atlases/atlas-audit.json').read_text())
files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['world/v3/locomotion.js','character-motion.js','directional-art.js','world/v3/warrior-painted-locomotion.json']}
summary={'candidate':True,'locomotionAccepted':False,'assetsReplaced':False,'runtimeFix':'Requests queue until the exact declared half-cycle contact; displacement is split between old and new stride distances. Start/stationary changes are explicit exceptions.','cases':records,'postFixTransitions':transition,'atlasRegistration':atlas,'sourceHashes':files,'limits':['No painted anatomical approval: joint/contact coordinates cannot be inferred from alpha bounds or simulated solver feet.','Instrumented capture overhead differs from isolated runtime performance.','Root distance per display cycle verifies timing calibration, not a valid painted stride.','Source atlas crops can contain row fragments; some were not visible in the gameplay captures.','All nine gameplay sheets inspected including closing 7→0 poses. Foreign NPCs in a few crops are actual scene actors.']}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'README.md').write_text('''# Critical locomotion diagnosis — not accepted

Actual ordinary-input capture covers 72 character/mode/direction cases. Every selected pose and every render-frame root sample is recorded. All nine sheets include each 0→1→…→7→0 transition. GIFs show unchanged gameplay crops at recorded and quarter speed; magnification is for inspection only.

## Findings

- Frame selection is sequential: zero observed dropped selections, phase mismatches or held rendered roots in the 72 pre-fix captures.
- Warrior uses eight fixed 320-square slots, one (160,264) root and one scale. Nevertheless its drawn walk repeatedly advances the same leg; run/sprint contain abrupt weapon/body changes. A correct metadata anchor cannot repair those drawings.
- Mage and Ranger have variable tight crops without shared root registration. Their visible height is much smaller than Warrior and their leg/contact sequence is incomplete. Walk, run and sprint reuse the same eight poses with different cadence. Ranger's north strip also lacks a consistent rear silhouette. Source crop previews contain adjacent-row fragments; these were not consistently visible in actual runtime captures.
- The runtime immediately replaced the active gait on a modifier change, bypassing its own contact queue. The fix queues requests and splits traveled distance at the exact declared contact boundary. 19 targeted tests cover all six changes at 30/60/120Hz, plus cancellation and stationary behavior; the focused suite passes 85 tests. A fresh normal-input transition capture confirms three moving switches at integer/half-integer gait boundaries, with the remaining fraction of the tick spent in the new cycle.
- Start/stop labels change on simulation ticks, while the art uses the ordinary movement/idle frames; no authored startup or settling full-body sequence exists. Immediate eight-direction view selection follows actual movement rather than interpolating/faking body motion. Different view drawings still need consistent registration/anatomy.
- Ground travel per displayed cycle is deterministic; it does not certify stride length. The current painted support/contact sequence is mechanically invalid, so matching actual painted stance travel remains blocked until coherent full-body strips exist. Pelvis and actual anatomical contact trajectories are not guessed from opaque clothing or alpha extrema.

## Required next asset gate

Finish the town presentation work, then create coherent full-body walk/run/sprint strips from the approved in-game character. Preserve shared costume, weapon, proportions, scale and root. Validate actual painted feet, pelvis and full loop at slow speed before integration. No independent procedural legs, per-frame art generation, boot freezing, body interpolation, blur or faster playback as concealment. The previous rejected v50/v52 studies remain uninstalled.
''',encoding='utf-8')
html='''<!doctype html><meta charset="utf-8"><title>ASTRAEON locomotion diagnosis</title><style>body{background:#172631;color:#eee;font:16px system-ui;margin:24px}select{font:inherit;margin:8px;padding:8px}section{display:flex;gap:20px;flex-wrap:wrap}img{max-width:100%}h1{font-size:24px}.panel{width:432px}</style><h1>Actual gameplay locomotion — diagnostic, not approved</h1><p>Recorded frames, normal speed and quarter speed. Body crops follow the root for inspection; raw videos retain world travel.</p><label>Character <select id="character"><option>warrior</option><option>mage</option><option>ranger</option></select></label><label>Gait <select id="mode"><option>walk</option><option>run</option><option>sprint</option></select></label><label>Direction <select id="direction"><option value="d">E</option><option value="s">S</option><option value="sd">SE</option><option value="wd">NE</option><option value="w">N</option><option value="wa">NW</option><option value="a">W</option><option value="sa">SW</option></select></label><section><div class="panel"><h2>Recorded speed</h2><img id="normal"></div><div class="panel"><h2>Quarter speed</h2><img id="slow"></div></section><p>Frame timing is observed, not anatomical approval. All current characters remain rejected for Golden locomotion.</p><script>function update(){const p=`locomotion60-${character.value}/motion-series/${mode.value}-${direction.value}/`;normal.src=p+'recorded.gif';slow.src=p+'quarter-speed.gif'}document.querySelectorAll('select').forEach(s=>s.onchange=update);update()</script>'''
(TEMP/'locomotion-dashboard.html').write_text(html,encoding='utf-8')
print('Saved 72 scoped cases, nine gameplay sheets, selected slow previews and unapproved diagnosis')
