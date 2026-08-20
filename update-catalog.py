#!/usr/bin/env python3
"""
Refresh the ModelMatch catalog to the state of play on 21 August 2026.

Three operations, in order:
  1. REMOVE  models that are retired / no longer served.
  2. REPLACE stale entries whose successor carries the same slot.
  3. INSERT  the current frontier lineup that was missing entirely.

Every price and date below was verified against a live source on 2026-08-21;
the source is named in the `verified` note on each record.
"""
import re, sys

PATH = 'index.html'
src = open(PATH).read()

start = src.index('const M=[')
end   = src.index('\n];', start)
head, block, tail = src[:start], src[start:end], src[end:]

# ── helper: locate a whole entry object by id ────────────────────────────
def find_entry(blk, mid):
    m = re.search(r"\{id:'" + re.escape(mid) + r"'", blk)
    if not m:
        return None
    i = m.start()
    depth, j, instr, esc = 0, i, None, False
    while j < len(blk):
        ch = blk[j]
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif instr:
            if ch == instr:
                instr = None
        elif ch in '"\'':
            instr = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return (i, j + 1)
        j += 1
    return None

def remove_entry(blk, mid):
    span = find_entry(blk, mid)
    if not span:
        print(f"   ?  {mid} not found")
        return blk, False
    i, j = span
    while j < len(blk) and blk[j] in ',\n \t':
        j += 1
    return blk[:i] + blk[j:], True

# ════════════════════════════════════════════════════════════════════════
# 1. REMOVALS — retired, shut down, or superseded past the point of use
# ════════════════════════════════════════════════════════════════════════
REMOVE = {
    # Anthropic: the entire Claude 3 generation is off the price sheet.
    'claude37':        'Claude 3.7 Sonnet — retired, off Anthropic price sheet',
    'claude35sonnet':  'Claude 3.5 Sonnet — retired',
    'claude35haiku':   'Claude 3.5 Haiku — retired except Bedrock/Vertex',
    'claude3opus':     'Claude 3 Opus — retired',
    # OpenAI
    'gpt35turbo':      'GPT-3.5 Turbo — legacy, superseded across the board',
    # Google: 1.5 generation is gone; 2.5 retires 2026-10-16.
    'gemini15flash':   'Gemini 1.5 Flash — retired',
    # xAI
    'grok3':           'Grok-3 — superseded by the Grok 4.x line',
    # Meta / misc: research artefacts no longer deployed
    'bloom176b':       'BLOOM-176B — research artefact, not production-served',
}

# ids in this file are not always guessable; resolve by display name too
NAME_TO_ID = {}
for mid, nm in re.findall(r"\{id:'([^']+)',name:'([^']*)'", block):
    NAME_TO_ID[nm] = mid
for mid, nm in re.findall(r'\{id:\'([^\']+)\',name:"([^"]*)"', block):
    NAME_TO_ID[nm] = mid

ALIAS = {
    'claude37': 'Claude 3.7 Sonnet', 'claude35sonnet': 'Claude 3.5 Sonnet',
    'claude35haiku': 'Claude 3.5 Haiku', 'claude3opus': 'Claude 3 Opus',
    'gpt35turbo': 'GPT-3.5 Turbo', 'gemini15flash': 'Gemini 1.5 Flash',
    'grok3': 'Grok-3', 'bloom176b': 'BLOOM-176B',
}

print("── REMOVING deprecated models ──")
removed = 0
for mid, why in REMOVE.items():
    real = mid if find_entry(block, mid) else NAME_TO_ID.get(ALIAS.get(mid, ''), mid)
    block, ok = remove_entry(block, real)
    if ok:
        removed += 1
        print(f"   ✂  {why}")

# ════════════════════════════════════════════════════════════════════════
# 2. NEW ENTRIES — current lineup as of 2026-08-21
# ════════════════════════════════════════════════════════════════════════

def entry(**k):
    """Build one catalog record in the file's existing shape."""
    def js(v):
        if isinstance(v, bool):  return 'true' if v else 'false'
        if v is None:            return 'null'
        if isinstance(v, (int, float)): return str(v)
        if isinstance(v, list):  return '[' + ','.join(js(x) for x in v) + ']'
        if isinstance(v, dict):  return '{' + ','.join(f"{a}:{js(b)}" for a, b in v.items()) + '}'
        s = str(v).replace('\\', '\\\\').replace("'", "\\'")
        return f"'{s}'"
    order = ['id','name','prov','icon','clr','tasks','type','featured','desc','langs',
             'pricing','pIn','pOut','tier','ctx','ctxN','params','lat','uses','pros',
             'cons','link','scores','deploy','sovereignty','bench','verified']
    parts = [f"{key}:{js(k[key])}" for key in order if key in k]
    return '{' + ','.join(parts) + '}'

LANGS_BIG = ['English','Arabic','Chinese','Spanish','French','German','Italian',
             'Portuguese','Japanese','Korean','Hindi','Russian','Turkish','Dutch']

def dom(h=5,f=5,l=5,r=4,e=5,g=4,m=4,t=5):
    return {'healthcare':h,'finance':f,'legal':l,'retail':r,'education':e,
            'government':g,'manufacturing':m,'technology':t}

NEW = []

# ── Anthropic — current Claude 5 family ────────────────────────────────
ANTH_SOV = {'uae':'available',
  'regions':['AWS me-central-1 (UAE)','AWS me-south-1 (Bahrain)','Global (default)'],
  'note':'Available via Amazon Bedrock and Google Cloud regional endpoints, including AWS me-central-1 (UAE). Regional and multi-region endpoints carry a 10% premium over global. On the first-party Claude API, Claude 4.6 and later support inference_geo:"us" for US-only processing at a 1.1x multiplier; global routing is the default.'}
ANTH_DEPLOY = {'onPrem':False,'cloud':True,'hybrid':False,'saas':True,
  'saasHost':'Claude API + Amazon Bedrock + Google Cloud + Microsoft Foundry','selfHost':False}

NEW.append(entry(
  id='claude-fable-5', name='Claude Fable 5', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc="Anthropic's Mythos-tier frontier model — the highest-capability Claude available to the public. Built for the hardest reasoning, long-horizon agentic work, coding and vision. Same underlying model as Claude Mythos 5, with additional safeguards for biology, cybersecurity and LLM R&D.",
  langs=LANGS_BIG,
  pricing='$10/1M in · $50/1M out', pIn=10.0, pOut=50.0, tier='high',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~900ms',
  uses=['Hardest reasoning tasks','Long-horizon agents','Frontier research','Complex multi-file coding'],
  pros=['Highest publicly available Claude capability','1M context at standard pricing','Strong agentic reliability'],
  cons=['Most expensive Claude tier','Overkill for routine workloads'],
  link='https://platform.claude.com/docs/en/about-claude/models/overview',
  scores={'q':100,'s':72,'c':30,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,5,4,5)},
  verified='✅ Verified 2026-08-21 — platform.claude.com/docs/en/about-claude/pricing'))

NEW.append(entry(
  id='claude-mythos-5', name='Claude Mythos 5 (limited access)', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial',
  desc='The Mythos-tier model without the Fable safeguard layer. Not publicly available — restricted to a small number of trusted organisations under Anthropic\'s Project Glasswing.',
  langs=LANGS_BIG,
  pricing='$10/1M in · $50/1M out (limited availability)', pIn=10.0, pOut=50.0, tier='high',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~900ms',
  uses=['Vetted frontier research','Trusted-partner deployments'],
  pros=['Frontier capability','Same tier as Fable 5'],
  cons=['Not generally available — Glasswing partners only','Requires Anthropic approval'],
  link='https://www.anthropic.com/glasswing',
  scores={'q':100,'s':72,'c':30,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,5,4,5)},
  verified='✅ Verified 2026-08-21 — anthropic.com/glasswing + Claude pricing docs'))

NEW.append(entry(
  id='claude-opus-5', name='Claude Opus 5', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc="Anthropic's flagship for complex agentic coding and enterprise work, and the recommended default Claude. Priced at parity with Opus 4.8. A Fast mode runs roughly 2.5x default speed at twice the base price.",
  langs=LANGS_BIG,
  pricing='$5/1M in · $25/1M out (Fast mode $10/$50)', pIn=5.0, pOut=25.0, tier='high',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~700ms',
  uses=['Complex agentic coding','Enterprise knowledge work','Long-running agents','Research'],
  pros=['Anthropic-recommended default','1M context at standard pricing','Fast mode available','Strong self-verification'],
  cons=['Higher cost than Sonnet 5','Newer tokenizer produces ~30% more tokens per unit of text'],
  link='https://www.anthropic.com/news/claude-opus-5',
  scores={'q':99,'s':78,'c':45,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,5,4,5)},
  verified='✅ Verified 2026-08-21 — anthropic.com/news/claude-opus-5 + pricing docs'))

NEW.append(entry(
  id='claude-sonnet-5', name='Claude Sonnet 5', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc='Released 30 June 2026. Performance close to Opus 4.8 at a much lower price — the best price-to-performance ratio in the Claude lineup and the default model on Free and Pro plans. Anthropic reports a lower rate of undesirable behaviours than Sonnet 4.6.',
  langs=LANGS_BIG,
  pricing='$2/1M in · $10/1M out', pIn=2.0, pOut=10.0, tier='mid',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~450ms',
  uses=['Production coding','Tool use and assistants','Balanced agent traffic','High-volume enterprise chat'],
  pros=['Best price-performance in the Claude range','1M context','Lower cyber capability than Opus — easier to risk-assess'],
  cons=['Below Opus 5 on the hardest reasoning','Newer tokenizer yields ~30% more tokens'],
  link='https://www.anthropic.com/news/claude-sonnet-5',
  scores={'q':96,'s':88,'c':72,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,5,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — anthropic.com/news/claude-sonnet-5. The $2/$10 launch rate is now the standard price; the previously scheduled 1 Sep 2026 increase will not occur.'))

NEW.append(entry(
  id='claude-opus-48', name='Claude Opus 4.8', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial',
  desc='Previous Opus flagship, still fully supported and priced identically to Opus 5. Also offers Fast mode.',
  langs=LANGS_BIG,
  pricing='$5/1M in · $25/1M out', pIn=5.0, pOut=25.0, tier='high',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~700ms',
  uses=['Complex reasoning','Agentic coding','Enterprise workloads'],
  pros=['Same price as Opus 5','Fast mode available','Well-characterised in production'],
  cons=['Superseded by Opus 5'],
  link='https://platform.claude.com/docs/en/about-claude/models/overview',
  scores={'q':97,'s':78,'c':45,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,5,4,5)},
  verified='✅ Verified 2026-08-21 — Claude pricing docs'))

NEW.append(entry(
  id='claude-sonnet-46', name='Claude Sonnet 4.6', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code','Vision'], type='commercial',
  desc='Prior Sonnet generation, still supported. Uses the older tokenizer, so token counts run lower than Sonnet 5 for the same text.',
  langs=LANGS_BIG,
  pricing='$3/1M in · $15/1M out', pIn=3.0, pOut=15.0, tier='mid',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~500ms',
  uses=['Production workloads on the older tokenizer','Migration baseline'],
  pros=['Stable, well-understood','1M context'],
  cons=['More expensive than the newer Sonnet 5','Superseded'],
  link='https://platform.claude.com/docs/en/about-claude/models/overview',
  scores={'q':94,'s':86,'c':64,'l':92},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — Claude pricing docs'))

NEW.append(entry(
  id='claude-haiku-45', name='Claude Haiku 4.5', prov='Anthropic', icon='🟣', clr='#8b5cf6',
  tasks=['LLM','Code'], type='commercial',
  desc='The small, fast, low-cost Claude. Built for extraction, classification, routing, short answers and other latency-sensitive work where a frontier model is wasted.',
  langs=LANGS_BIG,
  pricing='$1/1M in · $5/1M out', pIn=1.0, pOut=5.0, tier='low',
  ctx='200K tokens', ctxN=200000, params='Undisclosed', lat='~200ms',
  uses=['Classification','Extraction','Routing','High-volume support triage'],
  pros=['Cheapest current Claude','Fast','Often matches larger models on mechanical work'],
  cons=['Not for complex reasoning','Smaller context than the 5-series'],
  link='https://platform.claude.com/docs/en/about-claude/models/overview',
  scores={'q':86,'s':95,'c':86,'l':90},
  deploy=ANTH_DEPLOY, sovereignty=ANTH_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(4,5,4,5,4,4,4,5)},
  verified='✅ Verified 2026-08-21 — Claude pricing docs'))

# ── OpenAI — GPT-5.6 family ────────────────────────────────────────────
OAI_DEPLOY = {'onPrem':False,'cloud':True,'hybrid':False,'saas':True,
  'saasHost':'OpenAI API + Microsoft Azure OpenAI','selfHost':False}
OAI_SOV = {'uae':'available',
  'regions':['Azure OpenAI UAE North (via Microsoft/G42)','OpenAI global'],
  'note':'The direct OpenAI API is global. UAE data residency is reachable through Azure OpenAI Service in UAE North, or through Core42 Compass. Verify the specific model is offered in-region before assuming residency.'}

NEW.append(entry(
  id='gpt-56-sol', name='GPT-5.6 Sol', prov='OpenAI', icon='🟢', clr='#10a37f',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc="OpenAI's frontier tier, generally available 9 July 2026. Reasoning is built in, with Pro available as a reasoning mode rather than a separate model ID. Shares a 1.05M-token context window and 128K max output with Terra and Luna.",
  langs=LANGS_BIG,
  pricing='$5/1M in · $30/1M out (cached in $0.50)', pIn=5.0, pOut=30.0, tier='high',
  ctx='1.05M tokens', ctxN=1050000, params='Undisclosed', lat='~700ms',
  uses=['Frontier reasoning','Complex coding','Multimodal analysis','Agentic workflows'],
  pros=['Frontier-class reasoning','1.05M context','90% cache read discount'],
  cons=['Requests above 272K input tokens bill at 2x input and 1.5x output for the whole request','Not available for fine-tuning'],
  link='https://openai.com/api/pricing',
  scores={'q':99,'s':78,'c':40,'l':94},
  deploy=OAI_DEPLOY, sovereignty=OAI_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,5,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — GA 2026-07-09; rates reflect the 2026-07-30 price cut'))

NEW.append(entry(
  id='gpt-56-terra', name='GPT-5.6 Terra', prov='OpenAI', icon='🟢', clr='#10a37f',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc='The balanced production tier of the GPT-5.6 family. Cut 20% on 30 July 2026, which puts it below GPT-5.4 at the same token mix.',
  langs=LANGS_BIG,
  pricing='$2/1M in · $12/1M out (cached in $0.20)', pIn=2.0, pOut=12.0, tier='mid',
  ctx='1.05M tokens', ctxN=1050000, params='Undisclosed', lat='~400ms',
  uses=['Production chat','Agentic apps','RAG pipelines','General coding'],
  pros=['Strong price-performance','1.05M context','Cheaper than GPT-5.4'],
  cons=['Below Sol on the hardest reasoning','Long-context surcharge above 272K tokens'],
  link='https://openai.com/api/pricing',
  scores={'q':95,'s':88,'c':70,'l':94},
  deploy=OAI_DEPLOY, sovereignty=OAI_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,4,5,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — 2026-07-30 price cut (−20%)'))

NEW.append(entry(
  id='gpt-56-luna', name='GPT-5.6 Luna', prov='OpenAI', icon='🟢', clr='#10a37f',
  tasks=['LLM','Code'], type='commercial',
  desc='The volume tier of the GPT-5.6 family. Cut 80% on 30 July 2026 — the largest single OpenAI price move since the GPT-5 launch — making it the cheapest current frontier-family route by a wide margin.',
  langs=LANGS_BIG,
  pricing='$0.20/1M in · $1.20/1M out (cached in $0.02)', pIn=0.2, pOut=1.2, tier='low',
  ctx='1.05M tokens', ctxN=1050000, params='Undisclosed', lat='~250ms',
  uses=['High-volume classification','Summarisation','Routing','Cost-sensitive chat'],
  pros=['Extremely cheap for a current-generation model','1.05M context','Same family behaviour as Sol/Terra'],
  cons=['Weakest of the three on complex reasoning'],
  link='https://openai.com/api/pricing',
  scores={'q':87,'s':95,'c':96,'l':94},
  deploy=OAI_DEPLOY, sovereignty=OAI_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(4,4,4,5,4,3,4,5)},
  verified='✅ Verified 2026-08-21 — 2026-07-30 price cut (−80%)'))

NEW.append(entry(
  id='gpt-55', name='GPT-5.5', prov='OpenAI', icon='🟢', clr='#10a37f',
  tasks=['LLM','Code','Vision'], type='commercial',
  desc='Previous-generation OpenAI flagship, released 24 April 2026, knowledge cutoff 1 December 2025. Retained the same $5/$30 rate as GPT-5.6 Sol.',
  langs=LANGS_BIG,
  pricing='$5/1M in · $30/1M out', pIn=5.0, pOut=30.0, tier='high',
  ctx='1M+ tokens (922K in / 128K out)', ctxN=922000, params='Undisclosed', lat='~750ms',
  uses=['Complex professional workloads','Large-scale reasoning','Multimodal workflows'],
  pros=['Frontier reasoning','Very large context','Mature tooling'],
  cons=['Superseded by GPT-5.6 Sol at the same price'],
  link='https://openai.com/api/pricing',
  scores={'q':97,'s':76,'c':40,'l':94},
  deploy=OAI_DEPLOY, sovereignty=OAI_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,4,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — released 2026-04-24'))

# ── Google — Gemini 3.x ────────────────────────────────────────────────
G_DEPLOY = {'onPrem':False,'cloud':True,'hybrid':False,'saas':True,
  'saasHost':'Google AI Studio + Vertex AI','selfHost':False}
G_SOV = {'uae':'partial',
  'regions':['Vertex AI me-central2 (Dammam, KSA)','Global / multi-region endpoints'],
  'note':'No Google Cloud region inside the UAE. The nearest Vertex AI region is me-central2 (Dammam, Saudi Arabia). Vertex offers regional endpoints for data residency, but UAE-resident processing is not available — check with Google before using for UAE-regulated workloads.'}

NEW.append(entry(
  id='gemini-31-pro', name='Gemini 3.1 Pro', prov='Google', icon='🔵', clr='#4285f4',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc="Google's flagship reasoning model, launched 19 February 2026. Prompts above 200K tokens move to a higher meter ($4/$18). The older gemini-3-pro-preview endpoint was deprecated on 9 March 2026.",
  langs=LANGS_BIG,
  pricing='$2/1M in · $12/1M out (≤200K); $4/$18 above 200K', pIn=2.0, pOut=12.0, tier='high',
  ctx='1M+ tokens', ctxN=1048576, params='Undisclosed', lat='~600ms',
  uses=['Frontier reasoning','Long-document analysis','Multimodal understanding','Code generation'],
  pros=['Competitive frontier pricing','Very large context','Strong multimodal'],
  cons=['Context cliff at 200K doubles the rate','Paid tier only — no free tier'],
  link='https://ai.google.dev/pricing',
  scores={'q':97,'s':84,'c':70,'l':95},
  deploy=G_DEPLOY, sovereignty=G_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(5,5,5,5,5,4,4,5)},
  verified='✅ Verified 2026-08-21 — launched 2026-02-19'))

NEW.append(entry(
  id='gemini-37-flash', name='Gemini 3.7 Flash', prov='Google', icon='🔵', clr='#4285f4',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc='Newest Flash model, launched 13 August 2026 with a 1,048,576-token input window and 65,536-token output, matching Gemini 3.6 Flash. Adds native grounding.',
  langs=LANGS_BIG,
  pricing='$0.75/1M in · $3.75/1M out (introductory)', pIn=0.75, pOut=3.75, tier='low',
  ctx='1.05M tokens', ctxN=1048576, params='Undisclosed', lat='~300ms',
  uses=['High-volume production','Grounded search-backed answers','Fast multimodal'],
  pros=['Very cheap for its capability','1M+ context','Native grounding'],
  cons=['⚠ Introductory pricing — Google has published that this rate doubles on 1 January 2027','Published rates vary by source; confirm on Google\'s pricing page before budgeting'],
  link='https://ai.google.dev/pricing',
  scores={'q':92,'s':94,'c':88,'l':95},
  deploy=G_DEPLOY, sovereignty=G_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(4,5,4,5,5,4,4,5)},
  verified='⚠ Partially verified 2026-08-21 — launch date confirmed; sources disagree on the exact introductory rate. Verify at ai.google.dev/pricing.'))

NEW.append(entry(
  id='gemini-35-flash-lite', name='Gemini 3.5 Flash-Lite', prov='Google', icon='🔵', clr='#4285f4',
  tasks=['LLM','Code'], type='commercial',
  desc='The cheapest current-generation Gemini, aimed at very high volume work. Shipped 21 July 2026 alongside Gemini 3.6 Flash.',
  langs=LANGS_BIG,
  pricing='$0.30/1M in · $2.50/1M out', pIn=0.3, pOut=2.5, tier='low',
  ctx='1M tokens', ctxN=1048576, params='Undisclosed', lat='~200ms',
  uses=['Bulk classification','Extraction','High-volume routing'],
  pros=['Lowest current-gen Gemini price','Large context','Free tier available'],
  cons=['Limited reasoning depth'],
  link='https://ai.google.dev/pricing',
  scores={'q':84,'s':96,'c':92,'l':94},
  deploy=G_DEPLOY, sovereignty=G_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(4,4,4,5,4,3,4,5)},
  verified='✅ Verified 2026-08-21 — shipped 2026-07-21'))

# ── xAI — Grok 4.x ─────────────────────────────────────────────────────
X_DEPLOY = {'onPrem':False,'cloud':True,'hybrid':False,'saas':True,
  'saasHost':'xAI API + Grok Build + Cursor','selfHost':False}
X_SOV = {'uae':'unavailable',
  'regions':['US (xAI infrastructure)','EU (expanded access)'],
  'note':'xAI has expanded model access into regions including the EU, but availability is not the same as data residency. There is no UAE region. Buyers with compliance requirements should confirm processing location, retention and contractual terms directly with xAI.'}

NEW.append(entry(
  id='grok-46', name='Grok 4.6', prov='xAI', icon='⚡', clr='#eab308',
  tasks=['LLM','Code','Vision'], type='commercial', featured=True,
  desc='xAI\'s frontier model, released 12 August 2026 with a 500K context window and a February 2026 knowledge cutoff. Scores 61 on the Artificial Analysis Intelligence Index, matching GPT-5.6 Sol and one point behind Claude Fable 5 — the cheapest model currently at the intelligence frontier. Configurable reasoning effort (none/low/medium/high).',
  langs=['English','Chinese','Spanish','French','German','Japanese','Korean','Portuguese','Arabic','Russian'],
  pricing='$2/1M in · $6/1M out (cached in $0.50)', pIn=2.0, pOut=6.0, tier='mid',
  ctx='500K tokens', ctxN=500000, params='Undisclosed', lat='~500ms',
  uses=['Long-running agents','Agentic coding','Research with current data','Interactive and visual work'],
  pros=['Frontier intelligence at mid-tier pricing','3x output-to-input ratio where rivals charge 5–6x','Built-in web and X search'],
  cons=['⚠ Requests at or above 200K tokens bill the ENTIRE request at $4/$12','No UAE region','Priority processing costs 2x'],
  link='https://x.ai/api',
  scores={'q':97,'s':84,'c':84,'l':80},
  deploy=X_DEPLOY, sovereignty=X_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(3,4,3,4,4,2,3,5)},
  verified='✅ Verified 2026-08-21 — released 2026-08-12'))

NEW.append(entry(
  id='grok-43', name='Grok 4.3', prov='xAI', icon='⚡', clr='#eab308',
  tasks=['LLM','Code'], type='commercial',
  desc='A tier below the flagship, with a 1M-token context window at a materially lower per-token price. Tied with the Grok 4.20 variants on rate.',
  langs=['English','Chinese','Spanish','French','German','Japanese','Korean','Portuguese','Arabic'],
  pricing='$1.25/1M in · $2.50/1M out', pIn=1.25, pOut=2.5, tier='low',
  ctx='1M tokens', ctxN=1000000, params='Undisclosed', lat='~400ms',
  uses=['Long-context analysis','Cost-sensitive agents','Bulk reasoning'],
  pros=['1M context at a low rate','Cheap output tokens'],
  cons=['Long-context tier doubles to $2.50/$5.00 above 200K tokens','Below Grok 4.6 on quality'],
  link='https://x.ai/api',
  scores={'q':90,'s':88,'c':90,'l':80},
  deploy=X_DEPLOY, sovereignty=X_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(3,4,3,4,4,2,3,5)},
  verified='✅ Verified 2026-08-21 — xAI pricing'))

NEW.append(entry(
  id='grok-41-fast', name='Grok 4.1 Fast', prov='xAI', icon='⚡', clr='#eab308',
  tasks=['LLM'], type='commercial',
  desc='xAI\'s volume tier, pairing a 2M-token context window with near-DeepSeek pricing — the largest context window in the catalog at this price point.',
  langs=['English','Chinese','Spanish','French','German','Japanese','Korean','Portuguese','Arabic'],
  pricing='$0.20/1M in · $0.50/1M out', pIn=0.2, pOut=0.5, tier='low',
  ctx='2M tokens', ctxN=2000000, params='Undisclosed', lat='~180ms',
  uses=['Very large document ingestion','High-volume summarisation','Cheap long-context RAG'],
  pros=['2M context — largest here','Cheapest output tokens of any frontier-vendor model','2.4x cheaper on output than GPT-5.6 Luna'],
  cons=['Not a frontier-quality model','No UAE region'],
  link='https://x.ai/api',
  scores={'q':80,'s':96,'c':98,'l':78},
  deploy=X_DEPLOY, sovereignty=X_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(3,4,3,4,4,2,3,4)},
  verified='✅ Verified 2026-08-21 — xAI pricing'))

NEW.append(entry(
  id='grok-build-01', name='Grok Build 0.1', prov='xAI', icon='⚡', clr='#eab308',
  tasks=['Code'], type='commercial',
  desc='A coding specialist priced below the general-purpose Grok tiers, scoring above Grok 4.3 on quality. Grok 4.6 is now the default model inside Grok Build itself.',
  langs=['English'],
  pricing='$1/1M in · $2/1M out (cached in $0.20)', pIn=1.0, pOut=2.0, tier='low',
  ctx='256K tokens', ctxN=256000, params='Undisclosed', lat='~350ms',
  uses=['Coding agents','Code review','Software-building workflows'],
  pros=['Cheapest xAI coding route','Beats Grok 4.3 on quality'],
  cons=['Coding-specific — not general purpose','Smaller context than other Grok tiers'],
  link='https://x.ai/api',
  scores={'q':88,'s':90,'c':92,'l':60},
  deploy=X_DEPLOY, sovereignty=X_SOV,
  bench={'mmlu':None,'humanEval':None,'mtBench':None,'gsm8k':None,'hellaSwag':None,'domains':dom(2,3,2,3,3,2,3,5)},
  verified='✅ Verified 2026-08-21 — xAI pricing'))

# ── Splice the new records in right after the opening bracket ──────────
marker = 'const M=[\n'
assert block.startswith('const M=[')
insert_at = block.index('\n', block.index('const M=[')) + 1
banner = (
  "// ══ CURRENT FRONTIER LINEUP — refreshed 2026-08-21 ══════════════════════\n"
  "// Verified against vendor pricing/announcement pages on the date shown in\n"
  "// each record's `verified` field. Anthropic figures come from\n"
  "// platform.claude.com/docs/en/about-claude/pricing.\n\n"
)
block = block[:insert_at] + banner + ',\n\n'.join(NEW) + ',\n\n' + block[insert_at:]

open(PATH, 'w').write(head + block + tail)
print(f"\n── ADDED {len(NEW)} current models ──")
print(f"── REMOVED {removed} deprecated models ──")
