import {chromium} from '../tmp/factory-assets/browser/node_modules/playwright/index.mjs';
import {writeFileSync} from 'node:fs';
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-webgl','--ignore-gpu-blocklist']});
try {
 const page=await browser.newPage({viewport:{width:1280,height:800}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 const wait=fn=>page.waitForFunction(fn,null,{timeout:25000});
 const state=()=>page.evaluate(()=>window.factoryLocation);
 const xy=async i=>{const v=(await state()).labItems[i];return[v.x,800-v.y]};
 const pour=async()=>{await page.mouse.move(...await xy(0));await page.mouse.down();await page.waitForTimeout(140);await page.mouse.move(...await xy(2),{steps:14})};
 const reset=async()=>{await page.mouse.up();await page.mouse.click(1020,748,{delay:140});await wait(()=>window.factoryLocation.labStep===0&&window.factoryLocation.labSampleMl===0)};
 await page.goto('http://127.0.0.1:8011/?role=chemist');await wait(()=>window.factoryLocation);
 await page.evaluate(()=>window.factoryInstance.SendMessage('Factory exploration','CompleteTask'));await wait(()=>window.factoryLocation.labUnlocked);
 let s=await state();await page.mouse.click(s.labScreenX,800-s.labScreenY,{delay:140});await wait(()=>window.factoryLocation.labOpen);
 // A human can leave the target before releasing: already measured volume must still count.
 await pour();await wait(()=>window.factoryLocation.labSampleMl>=27.1);await page.mouse.move(650,520,{steps:2});await page.waitForTimeout(250);await page.mouse.up();await wait(()=>window.factoryLocation.labStep===1);
 const toleranceVolume=(await state()).labSampleMl;if(toleranceVolume<27||toleranceVolume>30)throw Error('Tolerance failed');
 await reset();await pour();await wait(()=>window.factoryLocation.labStep===1);await page.waitForTimeout(2200);
 s=await state();if(Math.abs(s.labSampleMl-30)>.001||s.labHeld!=='')throw Error('Long hold did not stop at 30');await page.mouse.up();
 await page.screenshot({path:'docs/game/lab-quality-review/pour-assist.png'});
 // Reset and a second uninterrupted hold must work, then transfer the same portion.
 await reset();await pour();await wait(()=>window.factoryLocation.labStep===1);await page.mouse.up();await page.mouse.move(...await xy(2));await page.mouse.down();await page.waitForTimeout(140);await page.mouse.move(...await xy(3),{steps:14});await wait(()=>window.factoryLocation.labStep===2);await page.mouse.up();
 s=await state();if(Math.abs(s.labFlaskMl-30)>.01)throw Error('Transfer changed assisted portion');
 const report={status:errors.length?'failed':'passed',checks:['27–30 ml accepted without exact timing','moving outside cylinder before release still accepts portion','holding automatically stops at exactly 30 ml','holding beyond stop cannot overflow','reset and second assisted pour','30 ml transfers intact'],unlock:'diagnostic; task-file gating covered by quality-review regression',toleranceVolume,state:s,scriptErrors:errors};
 writeFileSync('docs/game/lab-quality-review/pour-assist-validation.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(errors.length)throw Error('Browser errors');
} finally {await browser.close()}
