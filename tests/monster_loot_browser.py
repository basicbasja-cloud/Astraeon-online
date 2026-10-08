"""Disposable two-class Monster Loot acceptance, real kills plus fixed fixtures.
No art/visual acceptance. Live targeting retries retain authoritative evidence.
"""
import argparse,json,os,tempfile,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8011')
parser.add_argument('--browser',default=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name=='nt' else '/usr/bin/chromium'))
parser.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'astraeon-monster-loot-browser')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
checks,errors,http_errors,timing=[],[],[],[];report={}
def passed(name,evidence=None):checks.append({'name':name,'evidence':evidence});print('PASS',name,flush=True)
def qa(page):return page.evaluate('AstraeonQA.snapshot()')
def dev(page,code):return page.evaluate('()=>{const d=AstraeonProgressionDev,l=AstraeonMonsterLootDev;'+code+'}')
def saved(page):return dev(page,'return d.snapshot()')
def point(page,x,y):
    s=qa(page);b=page.locator('#world').bounding_box();v,c=s['view'],s['camera']
    return (b['x']+b['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-c['x'])*v['zoom'],b['y']+b['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-c['y'])*v['zoom'])
def close_menu(page):
    if qa(page)['windowName']:page.locator('#modal .close').click()
def idle(page):page.wait_for_function('!AstraeonQA.snapshot().action')
def approach_step(page,at,cls,instance_id,event):
    s=qa(page);origin={'x':s['save']['x'],'y':s['save']['y']}
    # Pick the closest of the actual eight input directions. Screen-sign pairs
    # can point south despite a northward target under this non-square basis.
    buttons=page.evaluate('''({at,origin})=>{const dx=at.x-origin.x,dy=at.y-origin.y,choices=[[['w'],0,-1],[['s'],0,1],[['a'],-1,0],[['d'],1,0],[['w','a'],-1,-1],[['w','d'],1,-1],[['s','a'],-1,1],[['s','d'],1,1]];return choices.map(([keys,x,y])=>{const direction=AstraeonMotion.cameraMovement(x,y,AstraeonView.inverse);return {keys,score:direction.x*dx+direction.y*dy}}).sort((a,b)=>b.score-a.score)[0].keys}''',{'at':at,'origin':origin})
    timing.append({'class':cls,'event':event,'enemyId':instance_id,'player':origin,'actor':at,'buttons':buttons})
    for button in buttons:page.keyboard.down(button)
    try:page.wait_for_function('p=>{const s=AstraeonQA.snapshot().save;return Math.hypot(s.x-p.x,s.y-p.y)>1}',arg=origin,timeout=15000)
    finally:
        for button in buttons:page.keyboard.up(button)
def kill_to(page,target_count,cls,preferred_ids=None):
    deadline=time.monotonic()+240;retries=0
    while qa(page)['save']['kills']<target_count:
        assert time.monotonic()<deadline,('bounded live kill deadline',cls,qa(page)['loot'])
        close_menu(page);idle(page)
        dev(page,'d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP)')
        s=qa(page);living=[e for e in s['enemies'] if e['hp']>0]
        # Per-life respawns may be nearer than the replacement under test.
        # Prefer its actual identity, then retain ordinary input/kill assertions.
        preferred=[e for e in living if e['rewardIdentity']['monsterInstanceId'] in (preferred_ids or set())]
        if preferred:living=preferred
        if not living:
            page.wait_for_function('AstraeonQA.snapshot().enemies.some(e=>e.hp>0)',timeout=40000);continue
        target=min(living,key=lambda e:(e['transform']['position']['x']-s['save']['x'])**2+(e['transform']['position']['y']-s['save']['y'])**2)
        # Click authority uses actor position; presentation transform can lag chase.
        # A stale projected click near the field gate can select travel instead.
        at=target['lifecycle']['position'];x,y=point(page,at['x'],at['y'])
        visible=page.evaluate('p=>document.elementFromPoint(p.x,p.y)?.id==="world"',{'x':x,'y':y-16})
        if not visible:
            # A clamped visible "ground" click may be a map gate. Use ordinary
            # directional input first, retaining the bounded movement condition.
            # No position/HP/AI mutation; actual travel is asserted separately.
            approach_step(page,at,cls,target['rewardIdentity']['monsterInstanceId'],'bounded keyboard waypoint for offscreen actor')
            continue
        page.mouse.click(x,y-16)
        # Existing warrior attacks stop movement. Approach the actor BEFORE hold.
        # This wait reads actual identity/HP/distance, not animation timing.
        try:
            page.wait_for_function('''({id,reach})=>{const q=AstraeonQA.snapshot(),e=q.enemies.find(e=>e.rewardIdentity.monsterInstanceId===id);return !e||e.hp===0||Math.hypot(q.save.x-e.transform.position.x,q.save.y-e.transform.position.y)<=reach}''',arg={'id':target['rewardIdentity']['monsterInstanceId'],'reach':2.3 if cls=='0' else 5.9},timeout=30000)
        except PlaywrightTimeout:
            state=qa(page);evidence={'class':cls,'event':'approach timeout','player':{'x':state['save']['x'],'y':state['save']['y'],'hp':state['save']['hp'],'zone':state['save']['zone']},'target':target,'navigation':state['navigation'],'action':state['action'],'click':{'x':x,'y':y-16},'element':page.evaluate('p=>document.elementFromPoint(p.x,p.y)?.outerHTML.slice(0,150)',{'x':x,'y':y-16})};timing.append(evidence);print(json.dumps(evidence),flush=True);raise
        b=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2);page.mouse.down()
        missed=False
        try:page.wait_for_function('(kills)=>AstraeonQA.snapshot().save.kills>kills',arg=s['save']['kills'],timeout=7000)
        except PlaywrightTimeout:
            missed=True;retries+=1;print('RETRY Basic Attack',cls,'kills',s['save']['kills'],'target',target['rewardIdentity']['monsterInstanceId'],flush=True);timing.append({'class':cls,'event':'retarget after bounded Basic Attack wait','kills':s['save']['kills'],'enemyId':target['rewardIdentity']['monsterInstanceId']})
        finally:page.mouse.up()
        if missed:
            # Range alone is insufficient at a projectile muzzle blocked by a
            # corner. Ordinary input approaches after the original bounded miss.
            idle(page);current=next((e for e in qa(page)['enemies'] if e['rewardIdentity']['monsterInstanceId']==target['rewardIdentity']['monsterInstanceId'] and e['hp']>0),None)
            if current:approach_step(page,current['lifecycle']['position'],cls,current['rewardIdentity']['monsterInstanceId'],'ordinary closer approach after bounded miss')
    return retries

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
        def open_page(path='/?qa=1&dev=1'):
            context=browser.new_context(viewport={'width':1280,'height':800});context.add_init_script('''if(location.protocol.startsWith('http')){const s=sessionStorage.getItem('astraeon-loot-death-fixture');if(s){localStorage.setItem('astraeon-iso-v1',s);sessionStorage.removeItem('astraeon-loot-death-fixture')}}''')
            page=context.new_page();page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
            page.goto(args.url.rstrip('/')+path,wait_until='load');return context,page
        for cls,skill in [('0','rising-edge'),('12','ember-bloom')]:
            context,page=open_page();page.wait_for_selector('#create');page.locator('#newname').fill('Loot smoke '+cls);page.locator('#newclass').select_option(cls);page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_function('AstraeonQA.snapshot().time>.5')
            passed('normal new-character boot with canonical v5 ownership',{'cls':cls})
            page.locator('[data-open="character"]').click()
            result=dev(page,'''const before=d.snapshot(),candidate=l.prepareFixture('proof-multi',[0,.99,0,0]),prepared=d.snapshot(),commit=l.commitFixture(),after=d.snapshot(),duplicate=l.duplicateFixture();return {before,candidate,prepared,commit,after,duplicate,repeated:d.snapshot()}''')
            assert result['before']==result['prepared'] and result['candidate']['ok']
            r=result['commit'];assert r['ok'] and len(r['stackRewards'])==2 and len(r['instanceRewards'])==1 and r['currencyGranted']==7
            assert result['after']['inventory']['herb']==result['before']['inventory']['herb']+3
            assert result['after']['inventory']['potion']==result['before']['inventory']['potion']+1
            assert result['duplicate']['code']=='ALREADY_COMMITTED' and result['after']==result['repeated']
            assert result['after']['kills']==result['before']['kills'] and result['after']['baseExp']==result['before']['baseExp'] and result['after']['baseJobExp']==result['before']['baseJobExp']
            passed('fixed RNG immutable candidate, mixed canonical stack/gear/currency commit, duplicate grants nothing',{'cls':cls,'deathId':r['deathId'],'instance':r['instanceRewards'][0]})
            instance=r['instanceRewards'][0]['instanceId'];assert result['after']['equippedItems']==result['before']['equippedItems']
            result=dev(page,f'''const before=d.getDerivedStats(),equipped=d.equip('{instance}','weapon');d.setCurrentHP(1);const quantity=d.getQuantity('potion'),used=d.requestActionItem('potion',{{now:AstraeonQA.snapshot().time,intent:'inventory'}});return {{before,equipped,after:d.getDerivedStats(),quantity,remaining:d.getQuantity('potion'),used}}''')
            assert result['equipped']['ok'] and result['after']['physicalATK']==result['before']['physicalATK']+6 and result['after']['magicATK']==result['before']['magicATK']+6
            assert result['used']['ok'] and result['used']['resourceAfter']['currentHP']==46 and result['remaining']==result['quantity']-1
            passed('looted canonical gear equips into Stats; canonically looted Potion executes Action Item',{'cls':cls})
            result=dev(page,"const a=l.prepareFixture('proof-none'),commit=l.commitFixture(),duplicate=l.duplicateFixture();return {a,commit,duplicate}")
            assert result['a']['resolution']['itemRewards']==[] and result['commit']['ok'] and result['duplicate']['code']=='ALREADY_COMMITTED'
            passed('no-drop lifecycle commits once',{'cls':cls})
            result=dev(page,"l.prepareFixture('proof-material');const first=l.commitFixture(),old=l.inspectFixture(),next=l.newFixtureLife(),second=l.commitFixture();return {first,old,next,second,identity:l.inspectFixture()}")
            assert result['first']['ok'] and result['second']['ok'] and result['first']['deathId']!=result['second']['deathId']
            assert result['old']['monsterInstanceId']==result['identity']['monsterInstanceId'] and result['identity']['lifeGeneration']==2
            passed('same instance respawn/new life creates fresh legitimate entitlement',{'cls':cls})
            dev(page,'d.setBaseLevel(8);d.setBaseJobLevel(20);d.addSkillPoints(50);d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP)')
            assert dev(page,f'return d.learnSkill("{skill}")')['ok'];assert dev(page,f'return d.assignSkill(7,"{skill}")')['ok']
            close_menu(page);page.locator('[data-open="journal"]').click();page.locator('[data-quest="2"]').click()
            before=saved(page);page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
            assert saved(page)['itemInventory']==before['itemInventory']
            initial_ids={e['rewardIdentity']['monsterInstanceId'] for e in qa(page)['enemies']}
            before=saved(page);event_count=len(qa(page)['loot']['events']);page.evaluate('AstraeonCombatDev.setPolicy({rolls:[.5,.5,.5]})')
            page.mouse.click(*point(page,14.5,22));page.wait_for_function('Math.hypot(AstraeonQA.snapshot().save.x-14.5,AstraeonQA.snapshot().save.y-22)<.5',timeout=60000)
            expected=dev(page,'return d.getDerivedStats()')
            for _ in range(20):
                idle(page);dev(page,'d.resetActionCooldowns();d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP);return d.executeActionSlot(7)')
                try:page.wait_for_function('(id)=>AstraeonCombatDev.results().some(e=>e.result.input.context.sourceSkillId===id)',arg=skill,timeout=1500);break
                except PlaywrightTimeout:pass
            else:raise AssertionError('Learned skill failed to contact real enemy')
            record=page.evaluate('(id)=>AstraeonCombatDev.results().find(e=>e.result.input.context.sourceSkillId===id)',skill)
            stat='physicalATK' if cls=='0' else 'magicATK';assert record['result']['input']['attacker']['stats'][stat]==expected[stat]
            comparison=page.evaluate('''record=>{const input=structuredClone(record.result.input);input.attacker.stats.physicalATK-=6;input.attacker.stats.magicATK-=6;return AstraeonCombatDev.inspect(input,[.5,.5,.5])}''',record)
            assert record['result']['finalDamage']>comparison['finalDamage']
            passed('learned skill and looted equipment Stats reach live Combat Resolution',{'cls':cls,'damage':record['result']['finalDamage'],'withoutLootedBlade':comparison['finalDamage']})
            retries=kill_to(page,before['kills']+5,cls);idle(page)
            after=saved(page);events=qa(page)['loot']['events'][event_count:];kills=after['kills']-before['kills']
            assert len(events)==kills and len({e['deathId'] for e in events})==kills
            assert sum(e['killCredit'] for e in events)==kills and sum(e['questCredit'] for e in events)==5
            assert after['gold']==before['gold']+sum(e['currencyGranted'] for e in events)
            assert after['baseLevel']>before['baseLevel'] or after['baseExp']>before['baseExp']
            assert after['baseJobLevel']>before['baseJobLevel'] or after['baseJobExp']>before['baseJobExp']
            assert after['inventory']['herb']>=before['inventory']['herb']+2 and after['inventory']['ore']>=before['inventory']['ore']+1 and after['quest'] is None
            assert after['itemInventory']['stacks']['herb']==after['inventory']['herb']
            passed('real Basic Attack kills produce one event/death and preserve material/gold/Base EXP/Job EXP/quest completion',{'cls':cls,'kills':kills,'events':events,'retargets':retries})
            result=dev(page,'''const dead=AstraeonQA.snapshot().enemies.find(e=>e.hp===0),before=d.snapshot(),events=l.snapshot().events.length,duplicate=l.repeatDeath(dead.rewardIdentity.monsterInstanceId);return {before,after:d.snapshot(),events,afterEvents:l.snapshot().events.length,duplicate}''')
            assert result['duplicate']['code']=='ALREADY_COMMITTED' and result['before']==result['after'] and result['events']==result['afterEvents']
            passed('actual gameplay duplicate death route rejects without gold/EXP/quest/item duplication',{'cls':cls})
            page.wait_for_function('(ids)=>AstraeonQA.snapshot().enemies.some(e=>e.hp>0&&!ids.includes(e.rewardIdentity.monsterInstanceId))',arg=list(initial_ids),timeout=40000)
            population=qa(page);new_ids={e['rewardIdentity']['monsterInstanceId'] for e in population['enemies'] if e['hp']>0}-initial_ids
            prior=saved(page)['kills'];kill_to(page,prior+3,cls,preferred_ids=new_ids)
            page.wait_for_function('(ids)=>AstraeonQA.snapshot().loot.events.some(e=>ids.some(id=>e.deathId.startsWith(id+":")))',arg=list(new_ids),timeout=40000)
            passed('actual field replacement spawn has new identity and can reward on death',{'cls':cls,'replacementIds':sorted(new_ids)})
            close_menu(page);idle(page);before=saved(page);page.locator('[data-open="map"]').click();page.locator('[data-travel="0"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===0')
            assert saved(page)['itemInventory']==before['itemInventory'] and saved(page)['kills']==before['kills']
            passed('town/field travel retains canonical loot and creates no reward',{'cls':cls})
            page.locator('[data-open="character"]').click();dev(page,'d.save()');before=saved(page)
            for _ in range(2):
                page.reload(wait_until='load');page.wait_for_selector('#world');page.locator('[data-open="character"]').click();after=saved(page)
                for key in ['itemInventory','equippedItems','inventory','equipment','gold','kills','baseExp','baseJobExp','quest']:assert after[key]==before[key],key
                assert qa(page)['loot']['events']==[];dev(page,'d.save()')
            passed('repeated save/reload preserves stack/ItemInstance/currency/serial with no death replay',{'cls':cls})
            death={**before,'currentHP':1,'hp':1,'zone':2,'x':17,'y':22,'guard':0,'invulnUntil':0}
            page.evaluate('(s)=>sessionStorage.setItem("astraeon-loot-death-fixture",JSON.stringify(s))',death);page.reload(wait_until='load');page.wait_for_selector('#world')
            page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=60000);after=saved(page)
            assert after['itemInventory']==before['itemInventory'] and after['kills']==before['kills'] and after['gold']==max(0,before['gold']-8) and qa(page)['loot']['events']==[]
            passed('actual enemy kills player; player respawn preserves loot/serial and grants no free reward',{'cls':cls})
            context.close()
        context,page=open_page('/tools/monster-loot.html');page.wait_for_function('AstraeonMonsterLootHarness.snapshot()')
        before=page.evaluate('AstraeonMonsterLootHarness.snapshot()');page.locator('#resolve').click();prepared=page.evaluate('AstraeonMonsterLootHarness.snapshot()');assert before['inventory']==prepared['inventory'] and before['gold']==prepared['gold']
        page.locator('#commit').click();assert json.loads(page.locator('#result').inner_text())['ok'];page.locator('#duplicate').click();assert json.loads(page.locator('#result').inner_text())['code']=='ALREADY_COMMITTED'
        page.locator('#new-life').click();page.locator('#commit').click();assert json.loads(page.locator('#result').inner_text())['ok'];assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        passed('isolated harness validation/RNG/candidate/commit/duplicate/new-life exposes exact ownership and allocator evidence')
        context.close();context,page=open_page('/');page.wait_for_selector('#create')
        for name in ['AstraeonMonsterLootDev','AstraeonProgressionDev','AstraeonCombatDev','AstraeonMonsterLootHarness']:assert page.evaluate('typeof '+name)=='undefined'
        passed('normal URL boots without developer mutation globals');context.close();browser.close()
    assert not errors and not http_errors,(errors,http_errors);report['result']='passed'
except Exception as error:report.update(result='failed',failure=str(error));raise
finally:
    report.update(checks=checks,runtimeErrors=errors,httpErrors=http_errors,liveTargetingObservations=timing)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'Monster Loot browser acceptance groups',flush=True)
