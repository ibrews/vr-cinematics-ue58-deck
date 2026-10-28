// Strict class QA. Run fleet-load-guard admit light before launching this script.
// Usage: node tools/qa_offline.mjs <deck-url> <output-dir>
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || path.join(os.homedir(), '.cache/spatial-deck/video-deps/node_modules/playwright-core'));
const [base, out] = process.argv.slice(2);
assert(base && out, 'Provide deck URL and output directory');
mkdirSync(out, {recursive:true});
const browser = await chromium.launch({executablePath:process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args:['--autoplay-policy=no-user-gesture-required',...(process.env.SD_HOST_RESOLVER_RULES?['--host-resolver-rules='+process.env.SD_HOST_RESOLVER_RULES]:[])]});
const report = {url:base, host:os.hostname(), errors:[], externalRequests:[], httpErrors:[], talks:[], looks:[], print:[]};
try {
 const context = await browser.newContext({viewport:{width:1920,height:1080}});
 const origin = new URL(base).origin;
 // Block Google Fonts explicitly and reject/count every other off-origin resource too.
 await context.route('**/*', route => {
  const u = new URL(route.request().url());
  if (/^https?:$/.test(u.protocol) && (['fonts.googleapis.com','fonts.gstatic.com'].includes(u.hostname) || u.origin !== origin)) {
   report.externalRequests.push(u.href); return route.abort();
  }
  return route.continue();
 });
 context.on('page', p => {
  p.on('pageerror', e => report.errors.push(e.message));
  p.on('console', m => {if(m.type()==='error')report.errors.push(m.text()+' @ '+m.location().url);});
  p.on('response', r => {if(r.status()>=400)report.httpErrors.push(r.status()+' '+r.url());});
 });
 const p = await context.newPage();
 const url = query => {const u=new URL(base);u.search=query;return u.href;};
 for (const talk of ['a','b']) {
  await p.goto(url('talk='+talk), {waitUntil:'load',timeout:60000});
  await p.waitForTimeout(500);
  const count = await p.evaluate(()=>allSlides.length);
  for(let i=0;i<count;i++) {
   await p.evaluate(i=>goTo(i),i);
   await p.waitForTimeout(180);
   await p.waitForFunction(()=>[...document.querySelectorAll('.slide.active img')].every(im=>im.complete&&im.naturalWidth>0));
  }
  const videos = await p.evaluate(()=>[...document.querySelectorAll('video.full-media')].map(v=>({poster:v.getAttribute('poster'),label:v.getAttribute('aria-label'),credit:v.title})));
  assert(videos.length>0 && videos.every(v=>v.poster&&v.label&&v.credit));
  report.talks.push({talk,slides:count,videos:videos.length});
 }
 await p.goto(new URL('review/looks/',base).href,{waitUntil:'load',timeout:60000});
 const links=await p.locator('a.open').evaluateAll(as=>as.map(a=>a.href));
 assert.equal(links.length,13);
 for(const link of links) {
  const look=new URL(link).searchParams.get('look');
  await p.goto(link,{waitUntil:'load',timeout:60000});
  assert.equal(await p.evaluate(()=>document.body.dataset.look),look);
  // Exercise the iframe recolorer as well as the top-level look stylesheet.
  const idx=await p.evaluate(()=>allSlides.findIndex(s=>s.dataset.sdMod==='pmre/camera-toy'));
  assert(idx>=0);
  await p.evaluate(i=>goTo(i),idx);await p.waitForTimeout(450);
  await p.screenshot({path:path.join(out,'look-'+look+'.png')});
  report.looks.push(look);
 }
 for(const talk of ['a','b']) {
  await p.goto(url('talk='+talk+'&print'),{waitUntil:'load',timeout:60000});
  const posters=await p.evaluate(()=>{
   const clips=SECTIONS.flatMap(s=>s.cases).filter(c=>/\.(mp4|webm)$/i.test(c.img||''));
   return clips.map(c=>{const im=[...document.querySelectorAll('img.full-media')].find(i=>i.getAttribute('src')===c.poster);return {poster:c.poster,decoded:!!im?.complete&&im.naturalWidth>0};});
  });
  assert(posters.length>0&&posters.every(p=>p.decoded));
  assert.equal(await p.locator('video.full-media').count(),0);
  await p.pdf({path:path.join(out,'talk-'+talk+'.pdf'),printBackground:true,preferCSSPageSize:true});
  report.print.push({talk,posters});
 }
 await p.goto(url('shot=2'),{waitUntil:'load',timeout:60000});
 await p.screenshot({path:path.join(out,'video-poster-shot.png')});
 assert.equal(report.externalRequests.length,0,JSON.stringify(report.externalRequests));
 assert.equal(report.errors.length,0,JSON.stringify(report.errors));
 assert.equal(report.httpErrors.length,0,JSON.stringify(report.httpErrors));
 report.verdict='PASS';
} catch(e) {report.verdict='FAIL';report.failure=e.stack;process.exitCode=1;}
finally {await browser.close();writeFileSync(path.join(out,'offline-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));}
