"""Disposable two-class lifecycle encounters; core timing comes from state, not art."""
import argparse,json,os,tempfile,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8011');parser.add_argument('--browser',default=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name=='nt' else '/usr/bin/chromium'));parser.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'astraeon-monster-lifecycle-browser');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
checks,errors,http_errors,timing=[],[],[],[];report={}
def passed(name,evidence=None):checks.append({'name':name,'evidence':evidence});print('PASS',name,flush=True)
def qa(page):return page.evaluate('AstraeonQA.snapshot()')
def dev(page,code):return page.evaluate('()=>{const d=AstraeonProgressionDev,l=AstraeonMonsterLifecycleDev;'+code+'}')
def inspect(page,id):return dev(page,'return l.inspect('+json.dumps(id)+')')
def point(page,x,y):
    s=qa(page);b=page.locator('#world').bounding_box();v,c=s['view'],s['camera']
    return (b['x']+b['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-c['x'])*v['zoom'],b['y']+b['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-c['y'])*v['zoom'])
def place(page,x,y):assert dev(page,f'return l.placePlayer({x},{y})')['ok']
def close(page):
    if qa(page)['windowName']:page.locator('#modal .close').click()
def wait_state(page,id,states):page.wait_for_function('({id,states})=>states.includes(AstraeonMonsterLifecycleDev.inspect(id)?.state)',arg={'id':id,'states':states},timeout=40000)
def fight(page,id):
    deadline=time.monotonic()+90;attempts=0
    while inspect(page,id)['hp']>0:
        assert time.monotonic()<deadline,('bounded encounter',inspect(page,id),qa(page)['navigation'])
        close(page);dev(page,'d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP)')
        actor=inspect(page,id);place(page,actor['position']['x'],actor['position']['y']-.7)
        # One real gameplay Basic Attack input per bounded hold. No fake HP debit.
        x,y=point(page,actor['position']['x'],actor['position']['y']);page.mouse.click(x,y-16);box=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down()
        try:page.wait_for_function('id=>AstraeonMonsterLifecycleDev.inspect(id)?.hp===0',arg=id,timeout=8000)
        except PlaywrightTimeout:attempts+=1;timing.append({'event':'bounded Basic Attack retry','id':id,'state':inspect(page,id)})
        finally:page.mouse.up()
    return attempts
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
        def open_page(path='/?qa=1&dev=1'):
            context=browser.new_context(viewport={'width':1280,'height':800});page=context.new_page();page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
            page.goto(args.url.rstrip('/')+path,wait_until='load');return context,page
        for cls,skill in [('0','rising-edge'),('12','ember-bloom')]:
            context,page=open_page();page.wait_for_selector('#create');page.locator('#newname').fill('Lifecycle '+cls);page.locator('#newclass').select_option(cls);page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_function('AstraeonQA.snapshot().time>.3');passed('normal character boot; town has no hostile field monsters',{'class':cls});assert not qa(page)['enemies']
            page.locator('[data-open="character"]').click()
            setup=dev(page,f'''d.setBaseLevel(8);d.setBaseJobLevel(20);d.addSkillPoints(50);const learned=d.learnSkill('{skill}'),assigned=d.assignSkill(7,'{skill}');AstraeonMonsterLootDev.prepareFixture('proof-equipment');const gear=AstraeonMonsterLootDev.commitFixture().instanceRewards[0];d.equip(gear.instanceId,'weapon');return {{learned,assigned,gear,stats:d.getDerivedStats()}}''');assert setup['learned']['ok'] and setup['assigned']['ok']
            close(page);page.locator('[data-open="journal"]').click();page.locator('[data-quest="2"]').click();page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2');page.locator('[data-open="character"]').click()
            actor=qa(page)['enemies'][0]['lifecycle'];id=actor['instanceId'];home=actor['home'];assert actor['alive'] and actor['lifeGeneration']==1 and actor['spawnId']!=actor['definitionId'];passed('field actor has separate definition/spawn/runtime/life identity',{'class':cls,'actor':actor})
            place(page,home['x'],home['y']-10);close(page);wait_state(page,id,['IDLE']);assert inspect(page,id)['targetId'] is None;passed('outside authored detection stays idle',{'class':cls})
            start=inspect(page,id)['position'];place(page,home['x'],home['y']-5);wait_state(page,id,['CHASE']);page.wait_for_function('({id,start})=>{const m=AstraeonMonsterLifecycleDev.inspect(id);return m.targetId==="player"&&Math.hypot(m.position.x-start.x,m.position.y-start.y)>.1}',arg={'id':id,'start':start},timeout=30000);passed('detection records acquisition and authoritative chase movement',{'class':cls,'actor':inspect(page,id)})
            # Keep the player stationary: actual chase must close to a contact
            # band that can hit, rather than relying on dev placement inside it.
            wait_state(page,id,['ATTACK']);hp=dev(page,'return d.snapshot().currentHP');page.wait_for_function('hp=>AstraeonQA.snapshot().save.currentHP<hp',arg=hp,timeout=30000)
            incoming=qa(page)['incomingCombat'][-1];assert incoming['result']['ok'] and incoming['hp']['appliedDamage']>0 and any(t['stage']=='defense' for t in incoming['result']['trace']);passed('enemy cadence/contact reaches shared Combat and Player HP authority',{'class':cls,'incoming':incoming})
            hp_monster=inspect(page,id)['hp'];place(page,home['x'],home['y']-14);wait_state(page,id,['RETURN']);assert inspect(page,id)['targetId'] is None;wait_state(page,id,['IDLE']);assert inspect(page,id)['hp']==hp_monster;passed('home leash releases target, returns and retains HP',{'class':cls,'actor':inspect(page,id)})
            before=dev(page,'return d.snapshot()');life=inspect(page,id)['lifeGeneration'];retries=fight(page,id);dead=inspect(page,id);assert dead['lifeGeneration']==life and dead['state'] in ['DEAD','RESPAWN_WAIT'] and not dead['targetId'];after=dev(page,'return d.snapshot()');reward=dead['rewardResult'];assert reward['committed'] and reward['killCredit']==1 and reward['questCredit']==1 and after['gold']==before['gold']+reward['currencyGranted'];assert reward['baseExp']==13 and reward['jobExp']>0;passed('real Basic Attack produces one authoritative death/reward, EXP/gold/quest once',{'class':cls,'death':dead,'retries':retries})
            page.locator('[data-open="character"]').click();before=dev(page,'return d.snapshot()');duplicate=dev(page,'return l.repeatDeath('+json.dumps(id)+')');assert duplicate['duplicate'] and duplicate['deathEvent'] is None and dev(page,'return d.snapshot()')==before;assert inspect(page,id)['hp']==0;assert inspect(page,id)['respawnReadyAt']>qa(page)['time'];passed('dead phase cannot attack/reward again; paused menu cannot advance respawn',{'class':cls})
            place(page,14.5,14.5);close(page);page.wait_for_function('({id,life})=>{const m=AstraeonMonsterLifecycleDev.inspect(id);return m?.lifeGeneration===life+1&&m.hp>0}',arg={'id':id,'life':life},timeout=60000);next_life=inspect(page,id);assert next_life['deathId'] is None and next_life['spawnId']==dead['spawnId'] and next_life['instanceId']==id;passed('respawn waits on simulation clock and reuses stable spawn/instance with new life',{'class':cls,'newLife':next_life})
            place(page,home['x'],home['y']-.7);page.wait_for_function('!AstraeonQA.snapshot().action');dev(page,'d.resetActionCooldowns();d.setCurrentSP(d.snapshot().maxSP);return d.executeActionSlot(7)');page.wait_for_function('(skill)=>AstraeonCombatDev.results().some(r=>r.result.input.context.sourceSkillId===skill)',arg=skill,timeout=30000);fight(page,id);second=inspect(page,id);assert second['deathId']!=dead['deathId'] and second['lifeGeneration']==life+1;events=[e for e in qa(page)['loot']['events'] if e['deathId'].startswith(id+':')];assert len(events)==2 and len({e['deathId'] for e in events})==2;assert dev(page,'return d.snapshot().inventory.herb')>=before['inventory']['herb']+1;assert dev(page,'return d.getEquipped("weapon")')==setup['gear']['instanceId'];passed('second life learned skill/Basic Attack rewards legitimately; gear remains canonical',{'class':cls,'events':events})
            item=dev(page,'d.setCurrentHP(1);d.resetActionItemCooldowns();const before=d.getQuantity("potion"),used=d.requestActionItem("potion",{now:AstraeonQA.snapshot().time});return {before,used,after:d.getQuantity("potion")}');assert item['used']['ok'] and item['after']==item['before']-1;passed('Action Item remains separate and canonical',{'class':cls})
            # Next legitimate life is allowed to kill the disposable player.
            place(page,home['x'],home['y']-.7);dev(page,'d.setCurrentHP(1)');page.wait_for_function('AstraeonQA.snapshot().save.currentHP===0',timeout=60000);at_death=qa(page);assert all(e['lifecycle']['targetId'] is None for e in at_death['enemies']);assert any(e.get('reason')=='PLAYER_DEATH' for e in at_death['lifecycle']['events']);page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=30000);assert not qa(page)['enemies'];passed('actual player death releases all targets; respawn retires stale attacks',{'class':cls})
            page.locator('[data-open="character"]').click();dev(page,'d.save()');saved=dev(page,'return d.snapshot()');page.reload(wait_until='load');page.wait_for_selector('#world');page.locator('[data-open="character"]').click();loaded=dev(page,'return d.snapshot()');
            for key in ['itemInventory','equippedItems','gold','kills','baseExp','baseJobExp','quest']:assert loaded[key]==saved[key],key
            assert qa(page)['loot']['events']==[];assert not qa(page)['enemies'];passed('save/reload preserves committed rewards without transient death/AI replay',{'class':cls})
            close(page);page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2');before=dev(page,'return d.snapshot()');page.locator('[data-open="map"]').click();page.locator('[data-travel="0"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===0');after=dev(page,'return d.snapshot()');assert after['kills']==before['kills'] and after['itemInventory']==before['itemInventory'];assert not qa(page)['enemies'] and not qa(page)['hostileShots'];passed('town/field travel preserves items and retires attack ownership',{'class':cls});context.close()
        context,page=open_page('/tools/monster-lifecycle.html');page.wait_for_function('AstraeonMonsterLifecycleHarness.snapshot().monster');page.locator('#detect').click();assert page.evaluate('AstraeonMonsterLifecycleHarness.snapshot().monster.state')=='CHASE';page.locator('#attack').click();page.locator('#kill').click();assert page.evaluate('AstraeonMonsterLifecycleHarness.snapshot().monster.state')=='DEAD';page.locator('#respawn').click();assert page.evaluate('AstraeonMonsterLifecycleHarness.snapshot().monster.lifeGeneration')==2;assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None;passed('isolated harness exposes deterministic lifecycle/loot/new-life without playable save');context.close()
        context,page=open_page('/');page.wait_for_selector('#create');page.locator('#newname').fill('Normal lifecycle boot');page.locator('#create').click();page.wait_for_selector('#world');assert page.evaluate('typeof AstraeonMonsterLifecycleDev')=='undefined';assert page.evaluate('typeof AstraeonMonsterLifecycleHarness')=='undefined';passed('normal URL character boots with no lifecycle mutation API');context.close();browser.close()
    assert not errors and not http_errors,(errors,http_errors);report['result']='passed'
except Exception as error:report.update(result='failed',failure=str(error));raise
finally:
    report.update(checks=checks,runtimeErrors=errors,httpErrors=http_errors,liveTargetingObservations=timing);(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'Monster Lifecycle browser groups',flush=True)
