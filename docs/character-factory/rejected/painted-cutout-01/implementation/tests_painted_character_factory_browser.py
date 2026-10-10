"""Inspect the pilot using the existing ASTRAEON layer compositor in Chrome."""
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'authoring/characters/swordsman-production/fresh-2d/painted-rig-01'
URL='http://127.0.0.1:8011/authoring/characters/swordsman-production/fresh-2d/painted-rig-01/review.html'


async def main():
    errors=[]
    evidence=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        page=await browser.new_page(viewport={'width':1280,'height':1000},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        await page.goto(URL)
        await page.wait_for_function('window.paintedPilotState?.ready === true')
        await page.locator('#play').click()
        for action in ('Idle','Walk','BasicAttack'):
            await page.select_option('#motion',action)
            await page.wait_for_function('(a)=>window.paintedPilotState?.action === a',arg=action)
            for variant in ('default','training','steel'):
                await page.select_option('#variant',variant)
                await page.wait_for_function('(v)=>window.paintedPilotState?.variant === v',arg=variant)
                count=await page.evaluate('window.paintedPilotState.count')
                for index in range(count):
                    await page.locator('#frame').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input"))}',index)
                    await page.wait_for_function('(i)=>window.paintedPilotState?.index === i',arg=index)
                    evidence.append(await page.evaluate('window.paintedPilotState'))
            if action=='BasicAttack':
                await page.select_option('#variant','default')
                await page.wait_for_function('window.paintedPilotState.variant === "default"')
                await page.locator('#frame').evaluate('(el)=>{el.value=8;el.dispatchEvent(new Event("input"))}')
                await page.wait_for_function('window.paintedPilotState.index === 8')
                await page.screenshot(path=str(FOLDER/'review-attack.png'),full_page=True)
        await page.select_option('#motion','Idle')
        await page.wait_for_function('window.paintedPilotState.action === "Idle"')
        await page.locator('#frame').evaluate('(el)=>{el.value=0;el.dispatchEvent(new Event("input"))}')
        await page.wait_for_function('window.paintedPilotState.index === 0')
        await page.screenshot(path=str(FOLDER/'review-dark.png'),full_page=True)
        await page.locator('#background').click()
        await page.screenshot(path=str(FOLDER/'review-light.png'),full_page=True)
        await page.locator('#sockets').check()
        await page.locator('#stage').screenshot(path=str(FOLDER/'review-grip.png'))
        await page.locator('#sockets').uncheck()
        await page.locator('#layers .card').filter(has=page.locator('h3',has_text='Weapon')).click()
        await page.wait_for_function('window.paintedPilotState.hidden.includes("Weapon")')
        await page.locator('#stage').screenshot(path=str(FOLDER/'review-weapon-removed.png'))
        await page.locator('#layers .card').filter(has=page.locator('h3',has_text='Weapon')).click()
        await page.select_option('#motion','Walk')
        await page.wait_for_function('window.paintedPilotState.action === "Walk"')
        await page.select_option('#speed','0.25')
        await page.locator('#play').click()
        await page.wait_for_timeout(600)
        quarter=await page.evaluate('window.paintedPilotState.index')
        await page.select_option('#speed','1')
        await page.wait_for_timeout(300)
        normal=await page.evaluate('window.paintedPilotState.index')
        assert quarter!=normal,'Playback did not advance'
        assert not errors,errors
        await browser.close()
    report={'status':'PASS','url':URL,'compositor':'existing AstraeonModularSprites.draw',
            'checkedFrames':len(evidence),'variants':['default','training','steel'],
            'motionActions':['Idle','Walk','BasicAttack'],'directions':['SE'],
            'backgrounds':['dark','light'],'speeds':[1,0.25],'errors':errors,
            'scope':'Pilot review only; not a complete runtime definition or gameplay acceptance'}
    (FOLDER/'browser-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    asyncio.run(main())
