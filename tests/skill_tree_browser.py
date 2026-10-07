"""Disposable real-browser skill learning/loadout/save acceptance; no visual claims."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--browser', default=os.environ.get('ASTRAEON_BROWSER',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name == 'nt' else '/usr/bin/chromium'))
parser.add_argument('--output', type=Path, default=Path(tempfile.gettempdir()) / 'astraeon-skill-browser')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
checks, errors, http_errors = [], [], []
report = {}

def passed(name, evidence=None):
    checks.append({'name': name, 'evidence': evidence})
    print('PASS', name, flush=True)

def dev(page, expression):
    return page.evaluate('()=>{const d=AstraeonProgressionDev;' + expression + '}')

def snap(page):
    return dev(page, 'return d.snapshot()')

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True,
            args=['--no-sandbox', '--enable-gpu'] + (['--use-angle=d3d11'] if os.name == 'nt'
                else ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']))

        def open_page(path, fixture=None):
            context = browser.new_context(viewport={'width':1280, 'height':800})
            if fixture:
                context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'
                                        + json.dumps(json.dumps(fixture)) + ')')
            page = context.new_page()
            page.set_default_timeout(180000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.on('response', lambda r: http_errors.append(f'{r.status} {r.url}') if r.status >= 400 else None)
            page.goto(args.url.rstrip('/') + path, wait_until='load')
            return context, page

        for cls, first, ultimate, passive, second_passive, node, stat in [
            ('0','rising-edge','jade-tempest','sword-mastery','swordsman-vitality','qi','physicalATK'),
            ('12','ember-bloom','tempest','arcane-mastery','focused-casting','fire','magicATK')]:
            context, page = open_page('/?qa=1&dev=1')
            page.wait_for_selector('#create')
            page.locator('#newname').fill('Skill smoke ' + cls)
            page.locator('#newclass').select_option(cls)
            page.locator('#create').click()
            page.wait_for_selector('#world')
            page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>.5')
            initial = snap(page)
            assert initial['learnedSkills'] == {} and initial['skillPoints'] == 0
            assert initial['actionLoadout'] == [None]*8 and initial['legacySkillControls'] is False
            page.wait_for_function('document.querySelector("[data-action=skill1]").disabled')
            passed('new character boots with empty ranks and eight unassigned slots', {'cls':cls})
            assert dev(page, f'return d.learnSkill("{first}")')['code'] == 'SKILL_POINTS'
            dev(page, 'd.grantBaseExp(45);d.grantJobExp(30)')
            assert snap(page)['baseLevel'] == snap(page)['baseJobLevel'] == 2
            assert snap(page)['skillPoints'] == 1
            assert dev(page, f'return d.learnSkill("{first}")')['ok']
            assert snap(page)['skillPoints'] == 0
            assert dev(page, f'return d.canUseSkill("{first}")')
            assert not dev(page, f'return d.isSkillAssigned("{first}")')
            assert dev(page, f'return d.rankUpSkill("{first}")')['code'] == 'JOB_LEVEL'
            dev(page, 'd.setBaseJobLevel(12);d.addSkillPoints(20)')
            before = snap(page)
            assert dev(page, f'return d.learnSkill("{ultimate}")')['code'] == 'PREREQUISITE'
            assert snap(page)['skillPoints'] == before['skillPoints']
            assert dev(page, f'return d.rankUpSkill("{first}")')['ok']
            assert dev(page, f'return d.learnSkill("{ultimate}")')['code'] == 'PREREQUISITE'
            assert dev(page, f'return d.rankUpSkill("{first}")')['ok']
            assert dev(page, f'return d.learnSkill("{ultimate}")')['ok']
            passed('shared pool spending, higher-rank Job and exact prerequisite rank gates', {'cls':cls})

            baseline = dev(page, 'return d.getDerivedStats()')
            assert dev(page, f'return d.learnSkill("{passive}")')['ok']
            assert dev(page, f'return d.rankUpSkill("{passive}")')['ok']
            assert dev(page, f'return d.learnSkill("{second_passive}")')['ok']
            assert dev(page, 'return d.getDerivedStats()')[stat] == baseline[stat]+4
            assert snap(page)['actionLoadout'] == [None]*8
            assert dev(page, f'return d.assignSkill(0,"{passive}")')['code'] == 'NOT_USABLE'
            assert dev(page, f'return d.assignSkill(0,"{first}")')['ok']
            assert dev(page, f'return d.setSkillNode("{first}","{node}")')['ok']
            compiled = dev(page, 'return d.compileAction(0)')
            assert compiled['node'] == node and compiled['learnedRank'] == 3
            assert compiled['id'] == first
            page.wait_for_function('(id)=>document.querySelector("[data-action=skill1] small").textContent.includes(id)', arg=compiled['name'])
            # Ordinary input executes the learned, assigned skill through the existing Timeline.
            page.keyboard.press('1')
            page.wait_for_function('AstraeonQA.snapshot().action!==null')
            during = dev(page, 'return d.assignSkill(1,null)')
            assert during['code'] == 'UNSAFE_CONFIGURATION'
            page.wait_for_function('AstraeonQA.snapshot().action===null')
            passed('automatic passives, explicit assignment and ranked Node action execute', {'cls':cls,'runtime':compiled['name']})

            page.locator('[data-open="journal"]').click()
            page.locator('[data-quest="2"]').click()
            page.locator('[data-open="character"]').click()  # Freeze resource regeneration for comparison.
            dev(page, 'const s=d.snapshot();d.setCurrentHP(s.maxHP);d.setCurrentSP(s.maxSP);d.save()')
            expected = snap(page)
            derived = dev(page, 'return d.getDerivedStats()')
            page.screenshot(path=str(args.output / ('class-'+cls+'-learned.png')))
            page.reload(wait_until='load')
            page.wait_for_selector('#world')
            page.locator('[data-open="character"]').click()
            restored = snap(page)
            for key in ['learnedSkills','skillPointSpending','skillPoints','actionLoadout','skillNodes',
                        'baseLevel','baseExp','baseJobLevel','baseJobExp','statPoints','STR','AGI','VIT','INT','DEX','LUK',
                        'maxHP','maxSP','resourceBase','inventory','equipment','quest','worldClaims','discovered','gold','zone','x','y']:
                assert restored[key] == expected[key], (key, restored[key], expected[key])
            assert dev(page, 'return d.getDerivedStats()') == derived
            assert dev(page, 'return d.compileAction(0)')['node'] == node
            paid = sum(restored['skillPointSpending'].values())
            result = dev(page, 'return d.resetSkills()')
            assert result['refund'] == paid
            assert snap(page)['skillPoints'] == restored['skillPoints']+paid
            assert dev(page, 'return d.resetSkills()')['refund'] == 0
            dev(page, 'd.save()')
            page.reload(wait_until='load')
            page.wait_for_selector('#world')
            assert snap(page)['learnedSkills'] == {}
            assert snap(page)['skillPoints'] == restored['skillPoints']+paid
            passed('reload retains ranks, balance, loadout, Nodes and gameplay state; reset refunds once', {'cls':cls,'refund':paid})
            context.close()

        legacy = {'name':'Legacy skill smoke','saveVersion':4,'cls':12,'lv':5,'xp':18,'gold':240,
                  'inventory':{'ore':9,'token':4},'equipment':{'weapon':'Astral Blade','armor':'Warden Plate','relic':'Sigil'},
                  'quest':{'id':2,'progress':4},'worldClaims':{'supply':True},'skillNodes':{'tempest':'ice'},
                  'loadout':{'historical':['scroll']},'futureField':{'kept':True}}
        context, page = open_page('/?qa=1&dev=1', legacy)
        page.wait_for_selector('#world')
        page.locator('[data-open="character"]').click()
        migrated = snap(page)
        assert migrated['learnedSkills'] == {} and migrated['legacySkillControls'] is True
        for key in ['equipment','quest','worldClaims','skillNodes','loadout','futureField','gold']:
            assert migrated[key] == legacy[key], key
        dev(page, 'd.save()')
        page.reload(wait_until='load')
        page.wait_for_selector('#world')
        assert snap(page)['learnedSkills'] == {} and snap(page)['skillPoints'] == 0
        # Fixed-button compatibility is not represented as learned or assigned progression.
        page.keyboard.press('4')
        page.wait_for_function('AstraeonQA.snapshot().action!==null')
        page.wait_for_function('AstraeonQA.snapshot().skillFields.some(f=>f.node==="ice")')
        passed('version 4 migration preserves historical data and legacy Node execution without free learning')
        context.close()

        context, page = open_page('/tools/progression.html')
        page.wait_for_function('window.AstraeonProgressionHarness?.snapshot()')
        page.locator('#points').fill('20');page.locator('#skill-points').click()
        page.locator('#job-level').fill('12');page.locator('#set-job').click()
        page.locator('#skill-id').select_option('rising-edge');page.locator('#learn-skill').click();page.locator('#rank-skill').click()
        page.locator('#assign-skill').click()
        page.locator('#skill-node').select_option('qi');page.locator('#set-node').click()
        assert page.locator('#status').inner_text() == 'OK'
        expected = page.evaluate('AstraeonProgressionHarness.snapshot()')
        assert expected['learnedSkills']['rising-edge'] == 2 and expected['actionLoadout'][0] == 'rising-edge'
        page.locator('#save').click();page.locator('#reload').click()
        assert page.evaluate('AstraeonProgressionHarness.snapshot()') == expected
        assert 'prerequisites' in page.locator('#skill-tree').inner_text()
        assert 'qi' in page.locator('#skill-loadout').inner_text()
        page.locator('#skill-id').select_option('sword-mastery');page.locator('#learn-skill').click()
        assert 'learned:sword-mastery' in page.locator('#skill-passives').inner_text()
        page.locator('#assign-skill').click();assert 'NOT_USABLE' in page.locator('#status').inner_text()
        page.locator('#reset-skills').click()
        balance = page.evaluate('AstraeonProgressionHarness.snapshot().skillPoints')
        page.locator('#reset-skills').click()
        assert page.evaluate('AstraeonProgressionHarness.snapshot().skillPoints') == balance
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        page.screenshot(path=str(args.output/'developer-skill-harness.png'))
        passed('developer harness inspect, learn, rank, assign, Node, passive, save and reset use shared APIs')
        context.close()

        context, page = open_page('/')
        page.wait_for_selector('#create')
        assert page.evaluate('typeof AstraeonProgressionDev') == 'undefined'
        passed('ordinary game URL exposes no developer mutation API')
        context.close()
        browser.close()
    assert not errors and not http_errors, (errors, http_errors)
    report['result'] = 'passed'
except Exception as error:
    report.update(result='failed', failure=str(error))
    raise
finally:
    report.update(checks=checks, runtimeErrors=errors, httpErrors=http_errors)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
