const fs=require('fs'),{JSDOM}=require('jsdom');
const html=fs.readFileSync(require('path').join(__dirname,'index.html'),'utf8');
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'http://localhost/'});
const w=dom.window;
const R=[]; const ck=(n,p,d)=>{R.push(p);console.log(`${p?'PASS':'FAIL'}  ${n}${d?'  → '+d:''}`)};
setTimeout(()=>{
 try{
  w.eval('window.__M=()=>M;');
  const M=w.__M();
  ck('catalog loads',Array.isArray(M)&&M.length===145,'entries='+M.length);
  const byId=i=>M.find(m=>m.id===i);
  ['claude-fable-5','claude-opus-5','claude-sonnet-5','claude-haiku-45','gpt-56-sol','gpt-56-terra','gpt-56-luna','gemini-31-pro','gemini-37-flash','grok-46','grok-41-fast']
    .forEach(i=>ck('present: '+i,!!byId(i)));
  ['claude37','claude35sonnet','claude3opus','gpt35turbo','grok3','bloom176b']
    .forEach(i=>ck('removed: '+i,!byId(i)));
  ck('all entries have sovereignty',M.every(m=>m.sovereignty&&m.sovereignty.uae));
  ck('all entries have numeric pricing',M.every(m=>typeof m.pIn==='number'&&typeof m.pOut==='number'));
  ck('all scores in range',M.every(m=>['q','s','c','l'].every(k=>typeof m.scores[k]==='number'&&m.scores[k]>=0&&m.scores[k]<=100)));
  ck('Opus 5 priced $5/$25',byId('claude-opus-5').pIn===5&&byId('claude-opus-5').pOut===25);
  ck('Sonnet 5 priced $2/$10',byId('claude-sonnet-5').pIn===2&&byId('claude-sonnet-5').pOut===10);
  ck('Grok 4.6 priced $2/$6',byId('grok-46').pIn===2&&byId('grok-46').pOut===6);
  ck('GPT-5.6 Luna priced $0.20/$1.20',byId('gpt-56-luna').pIn===0.2&&byId('gpt-56-luna').pOut===1.2);
  // hero counters derived
  const t=w.document.getElementById('hs-total');
  ck('hero total counter updated',t&&t.textContent==='145','shows '+(t&&t.textContent));
  const sb=w.document.getElementById('sbMeta');
  ck('sidebar meta shows updated count',sb&&/145/.test(sb.textContent),sb&&sb.textContent);
  // no stale May 2026 copy left in visible text
  const body=w.document.body.textContent;
  // The only remaining "May 2026" is the ranked-8 infographic, which is a dated
  // snapshot and must stay labelled as one rather than be silently re-dated.
  const mays=(body.match(/May 2026/g)||[]).length;
  ck('stale May 2026 copy removed except the labelled snapshot',mays<=2,'occurrences='+mays);
  ck('ranked-8 snapshot is flagged as not refreshed',/Not refreshed in the Aug 2026 update/.test(body));
  ck('upcoming list no longer calls Claude 5 "expected"',!/Claude 5[\s\S]{0,40}Expected H2 2026/.test(body));
  ck('upcoming list shows Grok 4.6 shipped',/Grok 4\.6/.test(body));
  ck('deprecation warnings surfaced',/Retires 16 Oct 2026/.test(body));
 }catch(e){ck('suite ran',false,e.stack.split('\n').slice(0,3).join(' | '));}
 const f=R.filter(x=>!x).length;
 console.log('\n'+'='.repeat(60));console.log(`${R.length-f}/${R.length} passed`);
 process.exit(f?1:0);
},2500);
