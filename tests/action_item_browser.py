"""Disposable Action Item execution acceptance for both classes; no visual claim."""
import argparse
import json
import os
import tempfile
from pathlib import Path
import town_service_navigation
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8011')
parser.add_argument('--browser',default=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name=='nt' else '/usr/bin/chromium'))
parser.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'astraeon-action-item-browser')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
checks,errors,http_errors,report=[],[],[],{}

def passed(name,evidence=None):
    checks.append({'name':name,'evidence':evidence});print('PASS',name,flush=True)
def dev(page,expression):
    return page.evaluate('()=>{const d=AstraeonProgressionDev;'+expression+'}')
def snapshot(page): return dev(page,'return d.snapshot()')
def idle(page): page.wait_for_function('!AstraeonQA.snapshot().action')
def world_point(page,x,y):
    s=page.evaluate('AstraeonQA.snapshot()');b=page.locator('#world').bounding_box();v,c=s['view'],s['camera']
    return (b['x']+b['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-c['x'])*v['zoom'],b['y']+b['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-c['y'])*v['zoom'])

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
        def open_page(path='/?qa=1&dev=1',fixture=None):
            context=browser.new_context(viewport={'width':1280,'height':800})
            context.add_init_script('''if(location.protocol==='http:'||location.protocol==='https:'){
                const fixture=sessionStorage.getItem('astraeon-action-item-test-fixture');
                if(fixture){localStorage.setItem('astraeon-iso-v1',fixture);sessionStorage.removeItem('astraeon-action-item-test-fixture');}
            }''')
            if fixture: context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps(fixture))+')')
            page=context.new_page();page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
            page.goto(args.url.rstrip('/')+path,wait_until='load');return context,page

        for cls,skill,passive,node in [('0','rising-edge','sword-mastery','qi'),('12','ember-bloom','arcane-mastery','fire')]:
            context,page=open_page();page.wait_for_selector('#create')
            page.locator('#newname').fill('Action Item smoke '+cls);page.locator('#newclass').select_option(cls);page.locator('#create').click()
            page.wait_for_selector('#world');page.wait_for_function('AstraeonQA.snapshot().time>.5')
            initial=snapshot(page);assert initial['saveVersion']==5
            assert len(initial['itemInventory']['instances'])==2
            assert initial['equippedItems']['weapon'] in initial['itemInventory']['instances']
            assert initial['equippedItems']['armor'] in initial['itemInventory']['instances']
            passed('new character has canonical starter instances and owned equipment IDs',{'cls':cls})

            town_service_navigation.npc_interaction(page,'merchant')
            before=snapshot(page);page.locator('[data-buy="herb:5"]').click()
            after=snapshot(page);assert after['gold']==before['gold']-5
            assert after['itemInventory']['stacks']['herb']==before['inventory']['herb']+1
            page.locator('[data-sell="herb:2"]').click();assert snapshot(page)['gold']==before['gold']-3
            dev(page,'d.addStack("ore",12);d.addStack("shard",10);d.addStack("herb",5)')
            page.locator('[data-open="systems"]').click();page.locator('[data-nav="craft"]').click()
            before=snapshot(page);page.locator('[data-craft="0"]').click()
            after=snapshot(page);assert after['inventory']['potion']==before['inventory']['potion']+1
            assert after['itemInventory']['stacks']['herb']==before['inventory']['herb']-2
            created={}
            for index,definition,slot in [(1,'astral-blade','weapon'),(2,'warden-plate','armor'),(4,'spirit-charm','relic')]:
                before=snapshot(page)['itemInventory'];page.locator(f'[data-craft="{index}"]').click()
                after=snapshot(page)['itemInventory'];new_ids=set(after['instances'])-set(before['instances'])
                assert len(new_ids)==1,(definition,new_ids)
                instance_id=new_ids.pop();assert after['instances'][instance_id]['definitionId']==definition
                created[slot]=instance_id
            assert len(set(created.values()))==3
            before_rations=snapshot(page)['inventory']['ration']
            page.locator('[data-craft="3"]').click()
            assert snapshot(page)['inventory']['ration']==before_rations+1
            passed('merchant buy/sell and all current crafts mutate canonical stacks and unique gear instances',{'cls':cls,'instances':created})

            page.locator('[data-open="inventory"]').click();baseline=dev(page,'return d.getDerivedStats()')
            for key in ['blade','plate','charm']: page.locator(f'[data-item="{key}"]').click()
            equipped=dev(page,'return d.getDerivedStats()')
            assert equipped['physicalATK']==baseline['physicalATK']+9 and equipped['magicATK']==baseline['magicATK']+9
            assert equipped['DEF']==baseline['DEF']+2
            assert dev(page,'return d.getEquipment()')==created
            assert len(dev(page,'return d.getEquipmentModifiers()'))==3
            before_inventory=dev(page,'return d.getInventory()')
            assert dev(page,'return d.unequip("weapon")')['ok']
            assert dev(page,'return d.getDerivedStats()')['physicalATK']==baseline['physicalATK']+3
            assert dev(page,'return d.getInventory()')==before_inventory
            dev(page,f'd.setCurrentHP(40);for(let i=0;i<20;i++){{d.equip("{created["weapon"]}","weapon");d.unequip("weapon")}}d.equip("{created["weapon"]}","weapon")')
            assert snapshot(page)['currentHP']==40
            assert dev(page,'return d.getDerivedStats()')==equipped
            assert snapshot(page)['maxHP']==baseline['maxHP']
            assert snapshot(page)['maxSP']==baseline['maxSP']
            passed('weapon/armor/relic modifiers enter Stats once; unequip reverses; repeated equip does not heal or drift',{'cls':cls})

            # One synchronous JS turn excludes frame regeneration from input/effect evidence.
            page.locator('#modal .close').click()
            result=dev(page,'''d.addStack("potion",5);d.addStack("ration",5);d.setCurrentHP(1);d.setCurrentSP(1);
                const before=d.snapshot(),gear=d.getEquipment(),stats=d.getDerivedStats(),slots=d.getLoadout(),skills=d.getActionRuntime();
                window.dispatchEvent(new KeyboardEvent("keydown",{key:"q"}));window.dispatchEvent(new KeyboardEvent("keyup",{key:"q"}));
                const after=d.snapshot(),clocks=d.getActionItemRuntime();document.querySelector("[data-action=potion]").click();
                return {before,after,repeated:d.snapshot(),clocks,afterClocks:d.getActionItemRuntime(),gear,afterGear:d.getEquipment(),stats,afterStats:d.getDerivedStats(),slots,afterSlots:d.getLoadout(),skills,afterSkills:d.getActionRuntime()};''')
            assert result['after']['currentHP']==46
            assert result['after']['inventory']['potion']==result['before']['inventory']['potion']-1
            assert result['after']==result['repeated'] and result['clocks']==result['afterClocks']
            for key in ['gear','stats','slots','skills']: assert result[key]==result['after'+key.capitalize()]
            assert len(result['slots'])==8 and result['clocks']['groups']['hp-potion']>0
            passed('Q reaches Action Item runtime; immediate pointer repeat heals/debits/starts clocks once; gear/Stats/eight slots/skill clocks intact',{'cls':cls})

            page.locator('[data-open="inventory"]').click()
            result=dev(page,'''d.setCurrentSP(1);const before=d.snapshot();document.querySelector("[data-item=ration]").click();
                const after=d.snapshot(),clocks=d.getActionItemRuntime();document.querySelector("[data-item=ration]").click();
                return {before,after,repeated:d.snapshot(),clocks,afterClocks:d.getActionItemRuntime()};''')
            assert result['after']['currentSP']==21
            assert result['after']['inventory']['ration']==result['before']['inventory']['ration']-1
            assert result['after']==result['repeated'] and result['clocks']==result['afterClocks']
            assert set(result['clocks']['groups'])=={'hp-potion','sp-potion'}
            passed('Ration Bag path shares execution core; independent HP/SP groups and repeated-input rejection',{'cls':cls})
            result=dev(page,'''d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP);
                const before=d.snapshot(),clocks=d.getActionItemRuntime(),c={now:AstraeonQA.snapshot().time,intent:"inventory"};
                const hp=d.requestActionItem("potion",c),sp=d.requestActionItem("ration",c);
                return {hp,sp,before,after:d.snapshot(),clocks,afterClocks:d.getActionItemRuntime()};''')
            assert result['hp']['code']==result['sp']['code']=='FULL_RESOURCES'
            assert result['before']==result['after'] and result['clocks']==result['afterClocks']
            passed('full HP/SP rejection preserves both inventory and cooldowns',{'cls':cls})
            page.locator('#modal .close').click()
            page.wait_for_function('AstraeonQA.snapshot().time>=AstraeonProgressionDev.getActionItemRuntime().items.potion&&AstraeonQA.snapshot().time>=AstraeonProgressionDev.getActionItemRuntime().items.ration')
            page.locator('[data-open="inventory"]').click()
            result=dev(page,'''d.setCurrentHP(1);d.setCurrentSP(1);const c={now:AstraeonQA.snapshot().time,intent:"inventory"},before=d.snapshot(),clocks=d.getActionItemRuntime();
                const ticket=d.prepareActionItem("potion",c),prepared=d.snapshot(),preparedClocks=d.getActionItemRuntime();
                const commit=d.commitActionItem(ticket,c),after=d.snapshot(),newClocks=d.getActionItemRuntime(),duplicate=d.commitActionItem(ticket,c);
                return {ticket,before,prepared,clocks,preparedClocks,commit,after,duplicate,repeated:d.snapshot(),newClocks,repeatedClocks:d.getActionItemRuntime()};''')
            assert result['ticket']['ok'] and result['before']==result['prepared'] and result['clocks']==result['preparedClocks']
            assert result['commit']['ok'] and result['commit']['effectResults'][0]['applied']==45
            assert result['duplicate']['code']=='ALREADY_COMMITTED' and result['after']==result['repeated'] and result['newClocks']==result['repeatedClocks']
            assert result['after']['itemInventory']['nextItemSerial']==result['before']['itemInventory']['nextItemSerial']
            passed('live prepare is non-mutating and owned commit exact-once with resource/debit evidence',{'cls':cls})
            page.locator('#modal .close').click()
            dev(page,'d.setBaseLevel(8);d.setBaseJobLevel(20);d.addSkillPoints(50)')
            for expression in [f'd.learnSkill("{skill}")',f'd.rankUpSkill("{skill}")',f'd.learnSkill("{passive}")',f'd.assignSkill(7,"{skill}")',f'd.setSkillNode("{skill}","{node}")']:
                assert dev(page,'return '+expression)['ok'],expression
            page.locator('[data-open="journal"]').click();page.locator('[data-quest="2"]').click()
            assert dev(page,'return d.moveSkill(7,0)')['ok']
            result=dev(page,'d.setCurrentSP(d.snapshot().maxSP);const before=d.snapshot().currentSP,cost=d.getActionSlotState(0).cost;window.dispatchEvent(new KeyboardEvent("keydown",{key:"1"}));window.dispatchEvent(new KeyboardEvent("keyup",{key:"1"}));return {before,after:d.snapshot().currentSP,cost}')
            assert result['before']-result['after']==result['cost'],result;idle(page)
            assert dev(page,'return d.moveSkill(0,7)')['ok']
            passed('learned slot 1 input remains executable separately from Action Item',{'cls':cls})
            slots=dev(page,'return d.getLoadout()');inventory=dev(page,'return d.getInventory()');equipment=dev(page,'return d.getEquipment()');item_clocks=dev(page,'return d.getActionItemRuntime()')
            page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
            assert dev(page,'return d.getInventory()')==inventory and dev(page,'return d.getEquipment()')==equipment
            assert dev(page,'return d.getActionItemRuntime()')==item_clocks
            passed('town to field preserves canonical ownership and existing cooldown timestamps',{'cls':cls})
            page.mouse.click(*world_point(page,14.5,22));page.wait_for_function('Math.hypot(AstraeonQA.snapshot().save.x-14.5,AstraeonQA.snapshot().save.y-22)<.5',timeout=60000)
            page.evaluate('AstraeonCombatDev.setPolicy({rolls:[.5,.5,.5]})')
            expected=dev(page,'return d.getDerivedStats()')
            for _ in range(20):
                idle(page);result=dev(page,'d.resetActionCooldowns();d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP);return d.executeActionSlot(7)');assert result['ok'],result
                try:
                    page.wait_for_function('(id)=>AstraeonCombatDev.results().some(e=>e.result.input.context.sourceSkillId===id)',arg=skill,timeout=1500);break
                except PlaywrightTimeout: pass
            else: raise AssertionError('Learned slot 8 did not contact field actor')
            record=page.evaluate('(id)=>AstraeonCombatDev.results().find(e=>e.result.input.context.sourceSkillId===id)',skill)
            stat='physicalATK' if cls=='0' else 'magicATK'
            assert record['result']['input']['attacker']['stats'][stat]==expected[stat]
            assert record['result']['input']['context']['sourceRank']==2
            assert record['result']['input']['context']['nodeId']==node
            assert record['hpAfter']==record['hpApplication']['hpAfter']
            comparison=page.evaluate('''record=>{const input=structuredClone(record.result.input);input.attacker.stats.physicalATK-=6;input.attacker.stats.magicATK-=6;return AstraeonCombatDev.inspect(input,[.5,.5,.5])}''',record)
            assert record['result']['finalDamage']>comparison['finalDamage']
            passed('Potion/Ration use canonical quantity; learned rank/Node/slot 8 and equipped stats reach live resolver damage',{'cls':cls,'equippedDamage':record['result']['finalDamage'],'withoutWeaponBonus':comparison['finalDamage']})

            before=snapshot(page);page.evaluate('AstraeonCombatDev.setPolicy(null)');idle(page)
            dev(page,'d.setCurrentHP(d.snapshot().maxHP);d.setCurrentSP(d.snapshot().maxSP)')
            # Walk/target actual actors; kills do not pull distant enemies into attack range.
            for _ in range(3):
                qa=page.evaluate('AstraeonQA.snapshot()');kills=qa['save']['kills']
                living=[e for e in qa['enemies'] if e['hp']>0]
                target=min(living,key=lambda e:(e['transform']['position']['x']-qa['save']['x'])**2+(e['transform']['position']['y']-qa['save']['y'])**2)
                at=target['transform']['position'];x,y=world_point(page,at['x'],at['y']);page.mouse.click(x,y-16)
                button=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(button['x']+button['width']/2,button['y']+button['height']/2);page.mouse.down()
                try: page.wait_for_function('(kills)=>AstraeonQA.snapshot().save.kills>kills',arg=kills,timeout=60000)
                finally: page.mouse.up()
            after=snapshot(page)
            assert after['baseLevel']>before['baseLevel'] or after['baseExp']>before['baseExp']
            assert after['baseJobLevel']>before['baseJobLevel'] or after['baseJobExp']>before['baseJobExp']
            assert after['gold']>before['gold']
            assert after['quest'] is None or after['quest']['progress']>before['quest']['progress']
            assert after['inventory']['ore']>=before['inventory']['ore']+1 and after['inventory']['herb']>=before['inventory']['herb']+1
            assert after['itemInventory']['stacks']['ore']==after['inventory']['ore']
            passed('Basic Attack kill rewards use canonical materials and retain Base/Job EXP/gold/quest credit',{'cls':cls})

            idle(page);return_clocks=dev(page,'return d.getActionItemRuntime()');return_inventory=dev(page,'return d.getInventory()')
            page.locator('[data-open="map"]').click();page.locator('[data-travel="0"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===0')
            assert dev(page,'return d.getActionItemRuntime()')==return_clocks and dev(page,'return d.getInventory()')==return_inventory
            before=snapshot(page);death={**before,'currentHP':1,'hp':1,'zone':2,'x':17,'y':22,'guard':0,'invulnUntil':0}
            page.evaluate('(s)=>sessionStorage.setItem("astraeon-action-item-test-fixture",JSON.stringify(s))',death)
            page.reload(wait_until='load');page.wait_for_selector('#world')
            page.locator('[data-open="character"]').click()
            result=dev(page,'''d.setCurrentHP(1);d.setCurrentSP(1);const c={now:AstraeonQA.snapshot().time,intent:"inventory"};
                const used=d.requestActionItem("potion",c);d.setCurrentHP(1);window.actionItemDeathTicket=d.prepareActionItem("ration",c);
                return {used,ticket:window.actionItemDeathTicket,state:d.snapshot(),clocks:d.getActionItemRuntime()};''')
            assert result['used']['ok'] and result['ticket']['ok']
            before=result['state'];death_clocks=result['clocks']
            page.locator('#modal .close').click();page.wait_for_function('AstraeonQA.snapshot().animation.state==="death"',timeout=60000)
            assert snapshot(page)['currentHP']==0
            page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=60000)
            after=snapshot(page)
            for key in ['itemInventory','equippedItems','learnedSkills','skillPointSpending','actionLoadout']: assert after[key]==before[key],key
            assert after['actionLoadout']==slots
            assert dev(page,'return d.getActionItemRuntime()')==death_clocks
            assert dev(page,'return d.commitActionItem(window.actionItemDeathTicket,{now:AstraeonQA.snapshot().time,intent:"inventory"})')['code']=='STALE_PACKAGE'
            passed('actual enemy death/respawn preserves remaining consumables and clocks; invalidates ticket without refund',{'cls':cls})
            page.locator('[data-open="character"]').click();dev(page,'d.save()');before=snapshot(page)
            for _ in range(3):
                page.reload(wait_until='load');page.wait_for_selector('#world');page.locator('[data-open="character"]').click();after=snapshot(page)
                assert dev(page,'return d.getActionItemRuntime().groups')=={}
                for key in ['itemInventory','equippedItems','inventory','equipment','resourceBase','maxHP','maxSP','learnedSkills','skillPointSpending','statPointSpending','actionLoadout','skillNodes','quest','worldClaims']: assert after[key]==before[key],key
                dev(page,'d.save()')
            passed('town/field, enemy death/respawn and repeated saves retain item identity/serial/equipment and learned loadout',{'cls':cls})
            context.close()

        legacy={'name':'Legacy item smoke','saveVersion':4,'cls':12,'lv':4,'gold':123,'inventory':{'herb':3,'ore':8,'potion':4,'ration':2,'blade':2,'plate':1,'charm':1,'token':9},'equipment':{'weapon':'Astral Blade','armor':'Warden Plate','relic':'Spirit Charm','oldSlot':'kept'},'quest':{'id':2,'progress':2},'worldClaims':{'legacy':True},'loadout':{'old':['scroll']}}
        context,page=open_page(fixture=legacy);page.wait_for_selector('#world');page.locator('[data-open="character"]').click()
        expected=snapshot(page);assert expected['saveVersion']==5 and len(expected['itemInventory']['instances'])==4
        for key in ['inventory','equipment','quest','worldClaims','loadout','gold']:
            if key=='inventory':
                for id,q in legacy[key].items(): assert expected[key][id]==q
            else: assert expected[key]==legacy[key]
        assert expected['learnedSkills']=={} and expected['legacySkillControls'] is True
        derived=dev(page,'return d.getDerivedStats()')
        for _ in range(5):
            dev(page,'d.save()');page.reload(wait_until='load');page.wait_for_selector('#world');page.locator('[data-open="character"]').click();after=snapshot(page)
            for key in ['itemInventory','equippedItems','inventory','equipment','resourceBase','maxHP','maxSP','statPoints','skillPoints']: assert after[key]==expected[key],key
            assert dev(page,'return d.getDerivedStats()')==derived
        page.locator('#modal .close').click();assert dev(page,'return d.executeActionSlot(3)')['ok']
        passed('legacy v4 stacks/equipped strings migrate once to v5, retain historical data and stay playable across five reloads')
        context.close()

        context,page=open_page('/tools/inventory.html');page.wait_for_function('AstraeonInventoryHarness.snapshot()')
        page.locator('#definition').select_option('ore');page.locator('#amount').fill('3');page.locator('#add-stack').click()
        assert json.loads(page.locator('#inventory').inner_text())['stacks']['ore']==3
        page.locator('#amount').fill('1');page.locator('#remove-stack').click()
        assert json.loads(page.locator('#inventory').inner_text())['stacks']['ore']==2
        page.locator('#definition').select_option('astral-blade');page.locator('#create-instance').click()
        state=page.evaluate('AstraeonInventoryHarness.snapshot()');id=next(i for i,v in state['itemInventory']['instances'].items() if v['definitionId']=='astral-blade')
        page.locator('#instance').select_option(id);page.locator('#equip').click()
        assert json.loads(page.locator('#equipment').inner_text())['slots']['weapon']==id
        page.locator('#delete-instance').click();assert 'ITEM_EQUIPPED' in page.locator('#status').inner_text()
        page.locator('#unequip').click();page.locator('#delete-instance').click()
        assert id not in json.loads(page.locator('#inventory').inner_text())['instances']
        page.locator('#create-instance').click();state=page.evaluate('AstraeonInventoryHarness.snapshot()')
        assert id not in state['itemInventory']['instances']
        page.locator('#save').click();expected=page.evaluate('AstraeonInventoryHarness.snapshot()')
        page.locator('#reload').click();assert page.evaluate('AstraeonInventoryHarness.snapshot()')==expected
        page.locator('#inspect-migration').click();assert json.loads(page.locator('#migration-result').inner_text())['saveVersion']==5
        assert page.evaluate('AstraeonInventoryHarness.snapshot()')==expected
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        passed('developer harness inspect/add/remove/create/delete/equip/unequip/save/reload/migration uses isolated canonical APIs')
        page.locator('#action-item').select_option('potion')
        for _ in range(3): page.locator('#give-consumable').click()
        page.locator('#set-item-resources').click();before=page.evaluate('AstraeonInventoryHarness.snapshot()')
        page.locator('#prepare-consumable').click();assert page.evaluate('AstraeonInventoryHarness.snapshot()')==before
        page.locator('#commit-consumable').click();result=json.loads(page.locator('#action-item-result').inner_text());assert result['ok'] and result['resourceAfter']['currentHP']==46
        page.locator('#commit-consumable').click();assert json.loads(page.locator('#action-item-result').inner_text())['code']=='ALREADY_COMMITTED'
        page.locator('#use-consumable').click();assert json.loads(page.locator('#action-item-result').inner_text())['code']=='COOLDOWN'
        page.locator('#advance-item-time').click();page.locator('#use-consumable').click();assert json.loads(page.locator('#action-item-result').inner_text())['ok']
        page.locator('#full-item-resources').click();page.locator('#use-consumable').click();assert json.loads(page.locator('#action-item-result').inner_text())['code']=='FULL_RESOURCES'
        page.locator('#reset-item-cooldowns').click();assert json.loads(page.locator('#action-item-state').inner_text())['runtime']['groups']=={}
        page.locator('#action-item').select_option('ration');page.locator('#give-consumable').click();page.locator('#set-item-resources').click();page.locator('#use-consumable').click()
        result=json.loads(page.locator('#action-item-result').inner_text());assert result['ok'] and result['resourceAfter']['currentSP']==21
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        passed('isolated Action Item harness descriptor/effects/eligibility/prepare/commit/time/full/reset controls')
        context.close()
        context,page=open_page('/');page.wait_for_selector('#create')
        assert page.evaluate('typeof AstraeonProgressionDev')=='undefined'
        assert page.evaluate('typeof AstraeonCombatDev')=='undefined'
        assert page.evaluate('typeof AstraeonInventoryHarness')=='undefined'
        passed('normal URL boots without unintended developer mutation APIs')
        context.close();browser.close()
    assert not errors and not http_errors,(errors,http_errors)
    report['result']='passed'
except Exception as error:
    report.update(result='failed',failure=str(error));raise
finally:
    report.update(checks=checks,runtimeErrors=errors,httpErrors=http_errors)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'Action Item browser acceptance groups')
