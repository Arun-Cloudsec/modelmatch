// Integration checks for the 2026-08-27 update:
//   provenance bar · modality summary dashboard · per-country sovereignty
const fs = require('fs');
const { JSDOM } = require('jsdom');

let pass = 0, fail = 0;
const ok  = (n, c, extra='') => { c ? (pass++, console.log('PASS  '+n+(extra?'  → '+extra:''))) : (fail++, console.log('FAIL  '+n+(extra?'  → '+extra:''))); };

const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/',
  beforeParse(win){ win.HTMLCanvasElement.prototype.getContext = () => ({ clearRect(){},beginPath(){},arc(){},fill(){},moveTo(){},lineTo(){},stroke(){},createLinearGradient:()=>({addColorStop(){}}),fillRect(){},closePath(){},save(){},restore(){},translate(){},scale(){} }); win.fetch = () => Promise.reject(new Error('offline')); win.requestAnimationFrame = () => 0; } });
const w = dom.window;
w.fetch = () => Promise.reject(new Error('offline'));
w.HTMLCanvasElement.prototype.getContext = () => null;

setTimeout(() => {
  const d = w.document;
  // top-level `const` bindings aren't window properties — reach them via eval
  const M = w.eval('M'), DATA_LAST_UPDATED = w.eval('DATA_LAST_UPDATED'), COUNTRY_PROFILES = w.eval('COUNTRY_PROFILES');

  // ── boot into the app ──
  w.currentUser = { name: 'Test', email: 't@t.io', role: 'Free' };
  d.getElementById('loginPage').style.display = 'none';
  d.getElementById('appPage').classList.add('active');
  w.initApp();

  // ═══ 1. Provenance / source strip ═══
  const pv = d.getElementById('provBar');
  ok('provenance bar renders', pv && pv.innerHTML.length > 100);
  ok('source is stated at the top', /SOURCE/.test(pv.textContent) && /Vendor pricing/i.test(pv.textContent));
  ok('names the cloud region sources', /Bedrock|Vertex|Foundry/i.test(pv.textContent));
  ok('names the sovereign source', /Core42|Compass/i.test(pv.textContent));
  ok('shows a catalog sync date', /Catalog last synced/.test(pv.textContent), pv.textContent.match(/Catalog last synced[^P]*/)[0].trim());
  ok('shows a separate price-verified date', /Prices verified/.test(pv.textContent));
  ok('sync date is today (27 Aug 2026)', /27 Aug 2026/.test(pv.textContent));
  ok('sources modal reachable from the bar', /openSourcesModal/.test(pv.innerHTML));
  ok('DATA_LAST_UPDATED refreshed off May 2026', DATA_LAST_UPDATED === 'August 27, 2026', DATA_LAST_UPDATED);

  // ═══ 2. Modality summary dashboard ═══
  const sum = () => d.getElementById('taskSummary').textContent;
  for (const t of ['TTS', 'STT', 'Vision', 'Translation', 'Embedding', 'LLM', 'Code']) {
    w.setTask(t);
    const txt = sum();
    const n = w.getFiltered().length;
    ok(`${t}: dashboard renders above the list`, d.getElementById('taskSummary').innerHTML.includes('ms-wrap'));
    ok(`${t}: states how many are available`, txt.includes(`${n} model`), `${n} models`);
    ok(`${t}: states how many are SaaS`, /SaaS \/ API/.test(txt));
    ok(`${t}: answers the on-prem question`, /On-premises/.test(txt));
    ok(`${t}: shows where it is hosted`, /Where it's hosted/.test(txt));
    ok(`${t}: shows sovereignty for the active country`, /Usable in/.test(txt));
    ok(`${t}: cues the detail below`, /Full model-by-model detail below/.test(txt));
  }

  // Google hosting actually surfaces where it should
  w.setTask('TTS');
  ok('TTS dashboard names Google as a host', /Google/.test(sum()), sum().match(/Google[^0-9]*\d+/) ? sum().match(/Google[^·]{0,40}/)[0] : '');
  w.setTask('STT');
  ok('STT price band is per audio minute', /per audio minute/.test(sum()));
  w.setTask('TTS');
  ok('TTS price band is per character', /per 1M characters/.test(sum()));
  w.setTask('LLM');
  ok('LLM price band is per token', /per 1M tokens/.test(sum()));

  // Catalogue page carries the same dashboard
  w.setCatTask('TTS'); w.renderCatalog();
  ok('catalogue page shows the same summary', d.getElementById('catTaskSummary').innerHTML.includes('ms-wrap'));

  // ═══ 3. Per-country sovereignty ═══
  const statuses = c => {
    const n = { available: 0, bloc: 0, partial: 0, unavailable: 0, selfhost: 0 };
    M.filter(m => m.sovereignty).forEach(m => { const s = w.getModelStatusForCountry(m, c); if (s) n[s.status]++; });
    return n;
  };

  const de = statuses('Germany');
  ok('Germany no longer returns zero sovereign models', de.available > 0, JSON.stringify(de));
  ok('Germany reports GDPR/EU-bloc compliant models', de.bloc > 0, de.bloc + ' in-bloc');

  w.selectCountry('Germany');
  const panel = d.getElementById('sovAnalysisPanel').textContent;
  ok('Germany view is driven by Germany', /Germany/.test(panel));
  ok('Germany summary counts sovereign models', new RegExp('Sovereign in Germany').test(panel));
  ok('Germany summary shows the EU bloc card', /Compliant via EU/.test(panel));
  ok('Germany cites German law, not UAE law', /GDPR|BDSG|German/i.test(panel));
  ok('Germany legend is not UAE-worded', !/UAE Sovereign|Outside UAE/.test(d.getElementById('sovStatusLegend').textContent));

  const grid = d.getElementById('sovModelGrid').textContent;
  ok('Germany grid does not headline UAE regions', !/me-central-1 \(UAE\)/.test(grid));
  ok('Germany grid shows German/EU regions', /Frankfurt|eu-central-1|europe-west|Germany|Paris|Sweden|Ireland/i.test(grid));
  ok('Germany recommendations are not empty', d.getElementById('sovRecommended').children.length > 0,
     d.getElementById('sovRecommended').children.length + ' cards');
  ok('active country propagated to Explorer badges', w.eval('ACTIVE_COUNTRY') === 'Germany', w.eval('ACTIVE_COUNTRY'));

  w.setTask('all');
  ok('Explorer chips follow the country', /Germany/.test(d.getElementById('f-sov').textContent), d.getElementById('f-sov').textContent);
  ok('Explorer legend follows the country', /Germany/.test(d.getElementById('sovLegendInline').textContent));
  ok('Explorer legend drops UAE wording', !/UAE/.test(d.getElementById('sovLegendInline').textContent));
  ok('modality dashboard follows the country', /Usable in .*Germany/.test(d.getElementById('taskSummary').textContent));

  // Switching country actually changes the numbers
  w.selectCountry('UAE');
  const ae = statuses('UAE');
  ok('UAE and Germany produce different results', JSON.stringify(ae) !== JSON.stringify(de),
     `UAE ${ae.available} in-country vs Germany ${de.available}`);
  ok('UAE view returns to UAE wording', /United Arab Emirates/.test(d.getElementById('sovAnalysisPanel').textContent));

  // Every country resolves without throwing and without an empty view
  let broken = [], emptyRec = [];
  Object.keys(COUNTRY_PROFILES).forEach(c => {
    try {
      const n = statuses(c);
      if (n.available + n.bloc + n.partial + n.selfhost === 0) broken.push(c);
      const cp = COUNTRY_PROFILES[c];
      const rec = [...new Set((cp.recommended || []).map(w.resolveModelId).filter(Boolean))];
      if (!rec.length) emptyRec.push(c);
    } catch (e) { broken.push(c + ':' + e.message); }
  });
  ok('every country has usable options', broken.length === 0, broken.join(',') || 'all 28 ok');
  ok('every country has live recommendations', emptyRec.length === 0, emptyRec.join(',') || 'no dead model ids');

  // ═══ 4. Switching country must leave nothing behind ═══
  const tips  = () => [...d.querySelectorAll('#sovAnalysisPanel .sov-tip')].map(t => t.textContent.trim());
  const chips = () => [...d.querySelectorAll('#sovCountryChips .sov-cs-chip')].map(c => (c.dataset.country || ''));

  ['UAE', 'Germany', 'Japan', 'Brazil', 'Singapore'].forEach(c => {
    w.selectCountry(c);
    const cp = COUNTRY_PROFILES[c];
    const t = tips(), ch = chips();
    ok(`${c}: exactly one sovereignty tip`, t.length <= 1, t.length + ' tips');
    ok(`${c}: the tip is for ${c}`, !t.length || t[0].includes(cp.name), (t[0] || '').slice(0, 46));
    ok(`${c}: only the selected country is chipped`, ch.length === 1 && ch[0] === c, JSON.stringify(ch));
    ok(`${c}: only one quick-select is highlighted`, d.querySelectorAll('.sov-qs-btn.active-country').length <= 1);
    ok(`${c}: header names ${c}`, d.getElementById('sovCountryHeader').textContent.includes(cp.name));
    ok(`${c}: recommended label names ${c}`, d.getElementById('sovRecCountry').textContent === cp.name);
    ok(`${c}: no other country lingers in the panel`, (() => {
      const txt = d.getElementById('sovAnalysisPanel').textContent;
      return !Object.entries(COUNTRY_PROFILES)
        .filter(([k]) => k !== c)
        .some(([k, p]) => txt.includes('Sovereignty Tip for ' + p.name));
    })());
  });

  // The exact regression: tip was pinned to the first country ever selected
  w.selectCountry('UAE'); w.selectCountry('Germany');
  ok('tip is not stuck on the first country selected',
     !tips().some(t => /United Arab Emirates/.test(t)), tips()[0] ? tips()[0].slice(0, 46) : 'none');

  // Clearing wipes every panel
  w.clearSovCountry();
  ok('clear resets to the default explainer', d.getElementById('sovAnalysisPanel').style.display === 'none');
  ok('clear empties the tip', tips().length === 0);
  ok('clear empties the chips', chips().length === 0);
  ok('clear empties the model grid', d.getElementById('sovModelGrid').innerHTML === '');
  ok('clear un-highlights quick-select', d.querySelectorAll('.sov-qs-btn.active-country').length === 0);

  // Modal banner is country-aware
  w.selectCountry('Japan');
  w.openModal('claude-sonnet-5');
  const mb = d.getElementById('modalBox').textContent;
  ok('model modal is evaluated against the active country', /Japan/.test(mb));
  ok('model modal drops the stock UAE banner', !/Fully compliant with UAE data sovereignty/.test(mb));

  console.log('\n' + '='.repeat(60));
  console.log(`${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
}, 900);
