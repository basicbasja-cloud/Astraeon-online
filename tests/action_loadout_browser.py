"""Disposable eight-slot gameplay/harness acceptance. No visual acceptance claim."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--browser', default=os.environ.get('ASTRAEON_BROWSER',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name == 'nt' else '/usr/bin/chromium'))
parser.add_argument('--output', type=Path, default=Path(tempfile.gettempdir())/'astraeon-action-loadout-browser')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
checks, errors, http_errors, report = [], [], [], {}

def passed(name, evidence=None):
    checks.append({'name':name, 'evidence':evidence})
    print('PASS', name, flush=True)

def dev(page, expression):
    return page.evaluate('()=>{const d=AstraeonProgressionDev;'+expression+'}')

def snapshot(page):
    return dev(page, 'return d.snapshot()')

def idle(page):
    page.wait_for_function('!AstraeonQA.snapshot().action')

def world_point(page, x, y):
    s=page.evaluate('AstraeonQA.snapshot()'); b=page.locator('#world').bounding_box()
    v,c=s['view'],s['camera']
    return (b['x']+b['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-c['x'])*v['zoom'],
            b['y']+b['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-c['y'])*v['zoom'])

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser,headless=True,
            args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt'
                  else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
        def open_page(path='/?qa=1&dev=1', fixture=None):
            context=browser.new_context(viewport={'width':1280,'height':800})
            context.add_init_script('''if(location.protocol==='http:'||location.protocol==='https:'){
                const fixture=sessionStorage.getItem('astraeon-loadout-test-fixture');
                if(fixture){localStorage.setItem('astraeon-iso-v1',fixture);sessionStorage.removeItem('astraeon-loadout-test-fixture');}
            }''')
            if fixture:
                context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps(fixture))+')')
            page=context.new_page();page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
            page.goto(args.url.rstrip('/')+path,wait_until='load')
            return context,page

        for cls,ids,passive,node,stat in [
            ('0',['rising-edge','iron-guard','second-wind','jade-tempest'],'sword-mastery','qi','physicalATK'),
            ('12',['ember-bloom','frost-ward','aether-mend','tempest'],'arcane-mastery','fire','magicATK')]:
            context,page=open_page()
            page.wait_for_selector('#create');page.locator('#newname').fill('Eight-slot smoke '+cls)
            page.locator('#newclass').select_option(cls);page.locator('#create').click()
            page.wait_for_selector('#world');page.wait_for_function('AstraeonQA.snapshot().time>.5')
            assert snapshot(page)['actionLoadout']==[None]*8
            dev(page,'d.grantJobExp(30);d.setBaseJobLevel(20);d.addSkillPoints(50);d.setBaseLevel(8)')
            assert dev(page,f'return d.learnSkill("{ids[0]}")')['ok']
            for _ in range(2): assert dev(page,f'return d.rankUpSkill("{ids[0]}")')['ok']
            for skill in ids[1:]: assert dev(page,f'return d.learnSkill("{skill}")')['ok']
            base=dev(page,'return d.getDerivedStats()')[stat]
            assert dev(page,f'return d.learnSkill("{passive}")')['ok']
            assert dev(page,'return d.getDerivedStats()')[stat]==base+2
            for slot,skill in enumerate(ids): assert dev(page,f'return d.assignSkill({slot},"{skill}")')['ok']
            assert dev(page,f'return d.setSkillNode("{ids[0]}","{node}")')['ok']
            for expression,code in [(f'd.assignSkill(7,"{ids[0]}")','ALREADY_ASSIGNED'),
                                    (f'd.assignSkill(0,"{passive}")','NOT_USABLE'),
                                    ('d.assignSkill(8,null)','INVALID_SLOT')]:
                before=snapshot(page)
                assert dev(page,'return '+expression)['code']==code
                assert snapshot(page)['actionLoadout']==before['actionLoadout']
                assert snapshot(page)['skillPointSpending']==before['skillPointSpending']
            passed('new character, Job/points, four actives, rank, passive, Node and assignment validation',{'cls':cls})

            # Real shipped key and pointer controls, then each developer slot intent.
            for slot,skill in enumerate(ids):
                idle(page);dev(page,'d.resetActionCooldowns();d.setCurrentSP(d.snapshot().maxSP)')
                if slot%2: page.locator(f'[data-action="skill{slot+1}"]').click()
                else: page.keyboard.press(str(slot+1))
                page.wait_for_function('(id)=>AstraeonProgressionDev.getActionRuntime().actions[id]>0',arg=skill)
                idle(page)
                assert dev(page,f'return d.moveSkill({slot},{slot+4})')['ok']
                result=dev(page,f'd.resetActionCooldowns();d.setCurrentSP(d.snapshot().maxSP);const r=d.executeActionSlot({slot+4});const sp=d.snapshot().currentSP,c=d.getActionRuntime();const rejected=d.executeActionSlot({slot+4});return {{r,rejected,sp,after:d.snapshot().currentSP,c,afterCD:d.getActionRuntime()}}')
                assert result['r']['ok'],result
                assert result['r']['slot']==slot+4 and result['r']['actionId']==skill
                assert result['r']['resourceBefore']-result['r']['resourceAfter']==result['r']['cost']
                assert result['rejected']['code']=='FORBIDDEN_STATE'
                assert result['sp']==result['after'] and result['c']==result['afterCD']
                idle(page)
                assert dev(page,f'return d.moveSkill({slot+4},{slot})')['ok']
            passed('all eight slots launch via shared runtime; original keys/pointers work; cost commits once',{'cls':cls})

            # Second, independent skill allows observing cooldown after Timeline is idle.
            dev(page,'d.resetActionCooldowns();d.setCurrentSP(d.snapshot().maxSP);d.executeActionSlot(1)')
            idle(page)
            result=dev(page,'const before=d.snapshot().currentSP,c=d.getActionRuntime(),r=d.executeActionSlot(1);return {r,before,after:d.snapshot().currentSP,c,afterCD:d.getActionRuntime()}')
            assert result['r']['code']=='COOLDOWN' and result['before']==result['after'] and result['c']==result['afterCD']
            result=dev(page,'d.resetActionCooldowns();d.setCurrentSP(0);const c=d.getActionRuntime(),r=d.executeActionSlot(0);return {r,sp:d.snapshot().currentSP,c,after:d.getActionRuntime()}')
            assert result['r']['code']=='RESOURCE' and result['sp']==0 and result['c']==result['after']
            # Access-key click is synchronous: exclude frame regeneration from cost comparison.
            result=dev(page,'d.setCurrentSP(d.snapshot().maxSP);const before=d.snapshot().currentSP,slots=d.getLoadout(),cost=d.getActionSlotState(0).cost;document.querySelector("[data-action=skill1]").click();return {before,after:d.snapshot().currentSP,cost,slots,afterSlots:d.getLoadout()}')
            assert result['before']-result['after']==result['cost'] and result['slots']==result['afterSlots']
            idle(page)
            result=dev(page,'const slots=d.getLoadout(),before=d.snapshot();d.setCurrentHP(1);document.querySelector("[data-action=potion]").click();document.querySelector("[data-action=attack]").click();return {slots,afterSlots:d.getLoadout(),before,after:d.snapshot()}')
            assert result['slots']==result['afterSlots']
            assert result['after']['inventory']['potion']==result['before']['inventory']['potion']-1
            assert result['after']['currentHP']>1
            idle(page)
            passed('cooldown/resource rejection is atomic; native skill cost exact; Basic Attack/Potion outside slots',{'cls':cls})

            page.locator('[data-open="character"]').click()
            before=snapshot(page);other='12' if cls=='0' else '0'
            page.locator(f'[data-training="{other}"]').click()
            dormant=dev(page,'return d.getActionSlotState(0)')
            assert dormant['blockedReason']=='WRONG_CLASS' and not dormant['eligible']
            after=snapshot(page)
            for key in ['actionLoadout','learnedSkills','skillPointSpending','skillPoints']: assert after[key]==before[key],key
            page.locator(f'[data-training="{cls}"]').click();page.locator('#modal .close').click()
            idle(page)
            passed('ordinary town training retains ranks/payment/intent and makes other class slots dormant',{'cls':cls})

            slots=dev(page,'return d.getLoadout()')
            page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click()
            page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
            assert dev(page,'return d.getLoadout()')==slots
            # In-combat configuration rule from Backbone; even empty slots are locked.
            result=dev(page,'const r=d.moveSkill(0,7);return {r,slots:Array.from({length:8},(_,i)=>d.getActionSlotState(i))}')
            assert result['r']['ok'] and result['r']['lockDuration']>0
            assert all(s['cooldownRemaining']>0 for s in result['slots'])
            page.mouse.click(*world_point(page,14.5,22))
            page.wait_for_function('Math.hypot(AstraeonQA.snapshot().save.x-14.5,AstraeonQA.snapshot().save.y-22)<.5',timeout=60000)
            page.evaluate('AstraeonCombatDev.setPolicy({rolls:[.5,.5,.5]})')
            for _ in range(20):
                idle(page)
                result=dev(page,'d.resetActionCooldowns();d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP);return d.executeActionSlot(7)')
                assert result['ok'],result
                try:
                    page.wait_for_function('(id)=>AstraeonCombatDev.results().some(e=>e.result.input.context.sourceSkillId===id)',arg=ids[0],timeout=1500)
                    break
                except PlaywrightTimeout: pass
            else: raise AssertionError('High slot did not contact an existing field actor')
            record=page.evaluate('(id)=>AstraeonCombatDev.results().find(e=>e.result.input.context.sourceSkillId===id)',ids[0])
            assert record['result']['ok'] and record['result']['input']['context']['sourceRank']==3
            assert record['result']['input']['context']['nodeId']==node
            assert record['hpAfter']==record['hpApplication']['hpAfter']
            idle(page)
            page.locator('[data-open="map"]').click();page.locator('[data-travel="0"]').click()
            page.wait_for_function('AstraeonQA.snapshot().save.zone===0')
            assert dev(page,'return d.getLoadout()')==[None,*ids[1:],None,None,None,ids[0]]
            page.locator('[data-open="journal"]').click();page.locator('[data-dungeon="0"]').click()
            page.wait_for_function('AstraeonQA.snapshot().dungeon!==null')
            assert dev(page,'return d.getSlot(7)')==ids[0]
            page.locator('[data-open="systems"]').click();page.locator('[data-nav="raid"]').click()
            page.locator('#leave-dungeon').click();page.wait_for_function('AstraeonQA.snapshot().dungeon===null&&AstraeonQA.snapshot().save.zone===0')
            assert dev(page,'return d.getSlot(7)')==ids[0]
            passed('field edits lock all eight; high slot rank/Node reaches real resolver; town/field/dungeon retain assignments',{'cls':cls})

            # Existing enemy death/respawn, beside an existing actor, on disposable storage.
            before=snapshot(page)
            death={**before,'currentHP':1,'hp':1,'zone':2,'x':17,'y':22,'guard':0,'invulnUntil':0}
            page.evaluate('(s)=>sessionStorage.setItem("astraeon-loadout-test-fixture",JSON.stringify(s))',death)
            page.reload(wait_until='load');page.wait_for_selector('#world')
            page.wait_for_function('AstraeonQA.snapshot().animation.state==="death"',timeout=60000)
            dead=snapshot(page);assert dead['currentHP']==0
            assert dev(page,'return d.executeActionSlot(7)')['code']=='DEAD'
            page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=60000)
            restored=snapshot(page)
            for key in ['actionLoadout','learnedSkills','skillPointSpending']: assert restored[key]==before[key],key
            assert len(set(filter(None,restored['actionLoadout'])))==4
            passed('real enemy death rejects skills; town respawn retains unique slots/ranks/payments',{'cls':cls})

            idle(page)
            result=dev(page,'d.resetActionCooldowns();d.setCurrentSP(d.snapshot().maxSP);return d.executeActionSlot(7)')
            assert result['ok'];idle(page)
            page.locator('[data-open="character"]').click();dev(page,'d.save()')
            before=snapshot(page)
            assert dev(page,'return Object.keys(d.getActionRuntime().actions).length')>0
            page.reload(wait_until='load');page.wait_for_selector('#world');page.locator('[data-open="character"]').click()
            after=snapshot(page)
            for key in ['actionLoadout','learnedSkills','skillPointSpending','skillPoints','skillNodes','inventory','equipment','quest','worldClaims','discovered','resourceBase','maxHP','maxSP','zone','x','y']: assert after[key]==before[key],key
            assert dev(page,'return d.getActionRuntime().actions')=={}
            assert page.locator('[data-action="skill5"]').count()==0
            passed('save/reload retains configuration/progression/world/gear and resets transient cooldowns; no new HUD',{'cls':cls})
            context.close()

        legacy={'name':'Legacy loadout smoke','saveVersion':4,'cls':12,'skillNodes':{'tempest':'ice'},'loadout':{'historical':['scroll']}}
        context,page=open_page(fixture=legacy);page.wait_for_selector('#world')
        result=dev(page,'const before=d.snapshot(),r=d.executeActionSlot(3);return {before,r,after:d.snapshot()}')
        assert result['r']['ok'] and result['r']['source']=='legacy'
        for key in ['learnedSkills','skillPointSpending','skillPoints','actionLoadout','loadout']: assert result['before'][key]==result['after'][key]
        assert result['after']['learnedSkills']=={} and result['after']['actionLoadout']==[None]*8
        passed('returning fixed-button legacy action uses shared commit without free ranks/points or historical data loss')
        context.close()

        context,page=open_page('/tools/progression.html')
        page.wait_for_function('AstraeonProgressionHarness.snapshot()')
        page.locator('#points').fill('20');page.locator('#skill-points').click()
        page.locator('#job-level').fill('12');page.locator('#set-job').click()
        page.locator('#skill-id').select_option('rising-edge');page.locator('#learn-skill').click();page.locator('#assign-skill').click()
        page.locator('#slot-target').fill('8');page.locator('#move-slot').click()
        page.locator('#skill-slot').fill('8');page.locator('#execute-slot').click()
        result=json.loads(page.locator('#action-result').inner_text());assert result['ok'] and result['slot']==7
        page.locator('#execute-slot').click();assert 'FORBIDDEN_STATE' in page.locator('#status').inner_text()
        page.locator('#time-step').fill('1');page.locator('#advance-action-time').click()
        page.locator('#execute-slot').click();assert 'COOLDOWN' in page.locator('#status').inner_text()
        page.locator('#action-time').fill('3');page.locator('#set-action-time').click()
        page.locator('#execute-slot').click();assert json.loads(page.locator('#action-result').inner_text())['ok']
        page.locator('#reset-cooldowns').click();assert json.loads(page.locator('#action-runtime').inner_text())['cooldowns']['actions']=={}
        page.locator('#slot-target').fill('1');page.locator('#swap-slots').click()
        page.locator('#skill-slot').fill('1');page.locator('#save').click();before=page.evaluate('AstraeonProgressionHarness.snapshot()')
        page.locator('#clear-slot').click();page.locator('#reload').click()
        assert page.evaluate('AstraeonProgressionHarness.snapshot()')==before
        page.locator('#skill-slot').fill('8');page.locator('#assign-skill').click();assert 'ALREADY_ASSIGNED' in page.locator('#status').inner_text()
        assert len(json.loads(page.locator('#action-runtime').inner_text())['slots'])==8
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        passed('isolated harness moves/swaps/clears, executes, shows cost/cooldown, sets/advances time, resets and reloads')
        context.close()
        context,page=open_page('/');page.wait_for_selector('#create')
        assert page.evaluate('typeof AstraeonProgressionDev')=='undefined'
        assert page.evaluate('typeof AstraeonCombatDev')=='undefined'
        passed('ordinary URL boots without developer mutation APIs')
        context.close();browser.close()
    assert not errors and not http_errors,(errors,http_errors)
    report['result']='passed'
except Exception as error:
    report.update(result='failed',failure=str(error));raise
finally:
    report.update(checks=checks,runtimeErrors=errors,httpErrors=http_errors)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'loadout browser acceptance groups')
