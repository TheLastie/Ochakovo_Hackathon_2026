import {chromium} from '../tmp/factory-assets/browser/node_modules/playwright/index.mjs';
import {writeFileSync} from 'node:fs';
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 const context=await browser.newContext({viewport:{width:1280,height:800}});const page=await context.newPage();const errors=[],assets=[],attempts=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/\/Build\//.test(r.url()))assets.push(r.url());});
 const intro=async()=>{await page.goto('http://127.0.0.1:8000/?loadingCheck='+Date.now()+'#shift');await page.locator('#game-menu-start').click();await page.waitForFunction(()=>document.querySelector('#game-menu').hidden);};
 const launch=async()=>{await page.frameLocator('#character-frame').locator('.start').click();await page.locator('#profession-film-skip').click();};
 const ready=async()=>{await page.waitForFunction(()=>document.querySelector('#character-frame').hidden,null,{timeout:120000});const frame=page.frame({url:/\/static\/unity\//});await frame.waitForFunction(()=>window.factoryLocation?.triangles>0,null,{timeout:60000});attempts.push(frame.url());};
 for(let i=0;i<2;i++){await intro();await launch();await ready();}
 await intro();await page.route(/\/Build\/WebGL\.[a-f0-9]{16}\.loader\.js/,r=>r.abort(),{times:1});await launch();await page.frameLocator('#character-frame').locator('.launch-status').filter({hasText:'Не удалось загрузить игру'}).waitFor();await launch();await ready();
 if(errors.length)throw Error(errors.join('\n'));
 if(!assets.every(url=>/WebGL\.[a-f0-9]{16}\.(loader\.js|framework\.js|data|wasm)$/.test(url)))throw Error('Unversioned asset');
 if(new Set(attempts.map(url=>new URL(url).searchParams.get('attempt'))).size!==3)throw Error('Retry reused index URL');
 const result={status:'passed',checks:['first launch','repeat launch in same browser context','loader failure returns to selection','retry after loader failure loads real Unity','all four build assets use content hashes','fresh manifest URL for each attempt'],attempts,assets:[...new Set(assets)],scriptErrors:errors};writeFileSync('docs/game/location/loading-validation.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close();}
