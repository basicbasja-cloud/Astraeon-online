"""Disposable live combat resolution/save acceptance. No visual acceptance claim."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--browser', default=os.environ.get('ASTRAEON_BROWSER', r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name == 'nt' else '/usr/bin/chromium'))
parser.add_argument('--output', type=Path, default=Path(tempfile.gettempdir())/'astraeon-combat-browser')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
checks, errors, http_errors = [], [], []
report = {}

def passed(name, evidence=None):
    checks.append({'name':name, 'evidence':evidence})
    print('PASS', name, flush=True)

def dev(page, expression):
    return page.evaluate('()=>{const d=AstraeonProgressionDev;'+expression+'}')

def snapshot(page):
    return dev(page, 'return d.snapshot()')

def world_point(page, x, y):
    s = page.evaluate('AstraeonQA.snapshot()')
    b = page.locator('#world').bounding_box()
    v, c = s['view'], s['camera']
    return (b['x']+b['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-c['x'])*v['zoom'],
            b['y']+b['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-c['y'])*v['zoom'])

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True,
            args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))

        def open_page(path='/?qa=1&dev=1', fixture=None):
            context = browser.new_context(viewport={'width':1280,'height':800})
            if fixture is not None:
                context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps(fixture))+')')
            page = context.new_page()
            page.set_default_timeout(180000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type=='error' else None)
            page.on('response', lambda r: http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
            page.goto(args.url.rstrip('/')+path, wait_until='load')
            return context, page

        for cls, first, passive, node, damage_type in [('0','rising-edge','sword-mastery','qi','physical'),('12','ember-bloom','arcane-mastery','fire','magical')]:
            context, page = open_page()
            page.wait_for_selector('#create')
            page.locator('#newname').fill('Combat smoke '+cls)
            page.locator('#newclass').select_option(cls)
            page.locator('#create').click()
            page.wait_for_selector('#world')
            page.wait_for_function('AstraeonQA.snapshot().time>.5')
            dev(page, 'd.setBaseJobLevel(12);d.addSkillPoints(20)')
            for expression in [f'd.learnSkill("{first}")',f'd.rankUpSkill("{first}")',f'd.rankUpSkill("{first}")',f'd.learnSkill("{passive}")',f'd.assignSkill(0,"{first}")',f'd.setSkillNode("{first}","{node}")']:
                assert dev(page, 'return '+expression)['ok'], expression
            compiled = dev(page, 'return d.compileAction(0)')
            assert compiled['learnedRank']==3 and compiled['node']==node
            passed('playable boot, learning, ranked active, passive and compatible Node', {'cls':cls})
            page.locator('[data-open="journal"]').click()
            page.locator('[data-quest="2"]').click()
            page.locator('[data-open="map"]').click()
            page.locator('[data-travel="2"]').click()
            page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
            page.mouse.click(*world_point(page,14.5,22))
            page.wait_for_function('Math.hypot(AstraeonQA.snapshot().save.x-14.5,AstraeonQA.snapshot().save.y-22)<.5',timeout=60000)

            def exercise(policy, predicate, key='f'):
                page.evaluate('(policy)=>AstraeonCombatDev.setPolicy(policy)', policy)
                dev(page, 'd.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP)')
                page.wait_for_function('!AstraeonQA.snapshot().action')
                button=page.locator('[data-action="'+('attack' if key=='f' else 'skill1')+'"]').bounding_box()
                page.mouse.move(button['x']+button['width']/2,button['y']+button['height']/2)
                page.mouse.down()
                try:
                    if key=='f':
                        page.wait_for_function('()=>AstraeonCombatDev.results().some(e=>'+predicate+')', timeout=60000)
                    else:
                        page.mouse.up()
                        for attempt in range(20):
                            try:
                                page.wait_for_function('()=>AstraeonCombatDev.results().some(e=>'+predicate+')',timeout=1500)
                                break
                            except PlaywrightTimeout:
                                page.keyboard.press(key)
                        else:
                            raise AssertionError('Learned active did not reach a field actor')
                except Exception:
                    (args.output/f'failure-{cls}.json').write_text(json.dumps({'state':page.evaluate('AstraeonQA.snapshot()'),'results':page.evaluate('AstraeonCombatDev.results()')},indent=2),encoding='utf-8')
                    raise
                finally:
                    page.mouse.up()
                records = page.evaluate('AstraeonCombatDev.results()')
                assert all(record['result']['ok'] for record in records), records
                assert all(record['hpAfter']==record['hpApplication']['hpAfter'] for record in records)
                return records

            for name, policy, predicate in [
                ('ordinary miss',{'defenderStats':{'FLEE':999},'rolls':[.9,.5,.5]},'e.result.outcome==="miss"'),
                ('perfect dodge',{'defenderStats':{'perfectDodge':100},'rolls':[.5,.5,.5]},'e.result.outcome==="perfectDodge"'),
                ('critical',{'attackerStats':{'CRIT':100},'action':{'coefficient':.1},'rolls':[.5,.5,.5]},'e.result.critical'),
                ('defense',{'defenderStats':{'DEF':999,'MDEF':999},'rolls':[.5,.5,.5]},'e.result.finalDamage===1&&e.result.effectiveDefense===999')]:
                records = exercise(policy,predicate)
                assert all(e['result']['input']['action']['damageType']==damage_type for e in records)
                if name in ['ordinary miss','perfect dodge']:
                    assert all(e['hpApplication']['hpAfter']==e['hpBefore'] for e in records)
                elif name=='defense':
                    assert all(e['hpApplication']['hpAfter']==max(0,e['hpBefore']-1) for e in records)
                passed('live '+name+' uses staged resolver', {'cls':cls,'sample':records[0]})

            # A learned active actually hits the ordinary field actor through existing input/Timeline.
            records = exercise({'rolls':[.5,.5,.5]},f'e.result.input.context.sourceSkillId==="{first}"','1')
            record = next(e for e in records if e['result']['input']['context']['sourceSkillId']==first)
            assert record['result']['input']['context']['sourceRank']==3
            assert record['result']['input']['context']['nodeId']==node
            assert record['result']['input']['action']['coefficient']==compiled['damage']
            assert record['result']['finalDamage']>0
            passed('learned rank and Node reach real combat HP application', {'cls':cls,'damage':record['result']['finalDamage']})
            before = snapshot(page)
            page.evaluate('AstraeonCombatDev.setPolicy(null)')
            button=page.locator('[data-action="attack"]').bounding_box()
            page.mouse.move(button['x']+button['width']/2,button['y']+button['height']/2);page.mouse.down()
            try:
                page.wait_for_function('(kills)=>AstraeonQA.snapshot().save.kills>kills',arg=before['kills'],timeout=60000)
            finally:
                page.mouse.up()
            after = snapshot(page)
            assert after['baseLevel']>before['baseLevel'] or after['baseExp']>before['baseExp']
            assert after['baseJobLevel']>before['baseJobLevel'] or after['baseJobExp']>before['baseJobExp']
            assert after['gold']>before['gold'] and after['quest']['progress']>before['quest']['progress']
            passed('ordinary combat death awards Base/Job EXP, loot and quest credit',{'cls':cls})
            # Existing enemy damage/death/respawn orchestration is retained.
            dev(page,'d.setCurrentHP(1)')
            page.wait_for_function('AstraeonQA.snapshot().animation.state==="death"',timeout=60000)
            assert snapshot(page)['currentHP']==0
            page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=60000)
            passed('existing incoming damage, player death and town respawn work',{'cls':cls})
            page.locator('[data-open="character"]').click()
            dev(page,'d.addStatPoints(5);d.allocateStat("STR",2);const s=d.snapshot();d.setCurrentHP(s.maxHP);d.setCurrentSP(s.maxSP);d.save()')
            before = snapshot(page)
            assert before['statPointSpending']==2
            page.reload(wait_until='load')
            page.wait_for_selector('#world')
            page.locator('[data-open="character"]').click()
            after = snapshot(page)
            for key in ['baseLevel','baseExp','baseJobLevel','baseJobExp','statPoints','statPointSpending','skillPoints','skillPointSpending','learnedSkills','actionLoadout','skillNodes','inventory','equipment','quest','worldClaims','discovered','zone','x','y','resourceBase','maxHP','maxSP','currentHP','currentSP']:
                assert after[key]==before[key],(key,before[key],after[key])
            dev(page,'d.resetStats();d.save()')
            balance=snapshot(page)['statPoints']
            dev(page,'d.resetStats()')
            assert snapshot(page)['statPoints']==balance==before['statPoints']+2
            passed('reload preserves core/skills/Node/world/gear and Stat ledger refunds once',{'cls':cls})
            context.close()

        future={'saveVersion':5,'name':'Future fixture','unknown':{'preserved':True},'inventory':{'token':7}}
        context,page=open_page('/',future)
        page.wait_for_selector('[data-save-error="UNSUPPORTED_SAVE_VERSION"]')
        original=page.evaluate('localStorage.getItem("astraeon-iso-v1")')
        assert json.loads(original)==future
        assert page.locator('#create').count()==0
        page.evaluate('window.dispatchEvent(new Event("pagehide"));document.dispatchEvent(new Event("visibilitychange"))')
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")')==original
        page.reload(wait_until='load')
        page.wait_for_selector('[data-save-error="UNSUPPORTED_SAVE_VERSION"]')
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")')==original
        passed('normal future-save path blocks creation and all overwrite paths, including reload')
        context.close()

        context,page=open_page('/tools/combat.html')
        page.wait_for_function('document.getElementById("result").textContent.includes("finalDamage")')
        r=json.loads(page.locator('#result').inner_text())
        assert r['result']['finalDamage']==75 and r['hpApplication']['hpAfter']==5
        page.locator('#config').fill('{"critical":{"multiplier":2}}')
        value=json.loads(page.locator('#input').input_value())
        value['attacker']['stats']['CRIT']=100
        page.locator('#input').fill(json.dumps(value));page.locator('#resolve').click()
        r=json.loads(page.locator('#result').inner_text())
        assert r['result']['critical'] and r['result']['finalDamage']==181
        passed('standalone developer inspection uses same resolver/config/RNG/HP boundary')
        context.close()
        context,page=open_page('/')
        page.wait_for_selector('#create')
        assert page.evaluate('typeof window.AstraeonCombatDev')=='undefined'
        assert page.evaluate('typeof window.AstraeonProgressionDev')=='undefined'
        passed('normal URL boots without developer mutation APIs')
        context.close();browser.close()
    assert not errors,errors
    assert not http_errors,http_errors
    report={'ok':True,'checks':checks,'errors':errors,'httpErrors':http_errors}
finally:
    report.setdefault('ok',False)
    report.update({'checks':checks,'errors':errors,'httpErrors':http_errors})
    (args.output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS',len(checks),'combat browser acceptance groups')
