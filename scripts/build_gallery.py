# -*- coding: utf-8 -*-
"""Rebuild gallery.html from data/ai-ux-patterns.csv (all patterns embedded, offline)."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "ai-ux-patterns.csv"
OUT = ROOT / "gallery.html"

rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
data = [{
    "no": r["No"], "cat": r["Pattern Category"], "name": r["Pattern Name"],
    "kw": r["Keywords"], "prob": r["Problem"], "sol": r["Solution"],
    "do": r["Do"], "dont": r["Don't"], "code": r["Code Example"],
    "anti": r["Anti-Pattern"], "when": r["When to Use"],
    "trust": r["Trust Impact"], "sev": r["Severity"],
} for r in rows]

payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
total = len(data)
ncat = len({d["cat"] for d in data})

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>AI-Native Interface Patterns — Gallery</title>
<style>
  :root {
    --bg:#e9ebee; --surface:#f6f7f8; --surface-2:#eef0f2; --raise:#fff;
    --ink:#14181d; --muted:#5b636c; --faint:#868f99;
    --line:#d2d7dd; --line-strong:#b9c0c8;
    --cyan:#0d7280; --cyan-ink:#0a5a66; --brass:#8a6a25;
    --ok:#3f7d4e; --ok-bg:#e3efe6; --crit:#a23b2f; --crit-bg:#f4e2df;
    --warnpill:#8a6a25; --warnpill-bg:#f0e6cf;
    --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono",Menlo,Consolas,monospace;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  }
  @media (prefers-color-scheme:dark){:root{
    --bg:#0d1015; --surface:#151a21; --surface-2:#10151b; --raise:#1b212a;
    --ink:#e7eaee; --muted:#8b949e; --faint:#6b747d;
    --line:#242b34; --line-strong:#333c47;
    --cyan:#35c4d6; --cyan-ink:#7bdcea; --brass:#d8b25c;
    --ok:#6fbf83; --ok-bg:#16241a; --crit:#e06a5c; --crit-bg:#2a1714;
    --warnpill:#d8b25c; --warnpill-bg:#2a2417;
  }}
  *{box-sizing:border-box;}
  body{margin:0; background:var(--bg); color:var(--ink); font-family:var(--sans); font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased;}
  .page{padding:clamp(18px,4vw,40px) 18px 80px;}
  .wrap{max-width:1180px; margin:0 auto;}
  .mono{font-family:var(--mono);}
  h1{font-size:clamp(22px,4vw,34px); letter-spacing:-.02em; margin:0; text-wrap:balance;}
  .eyebrow{font-family:var(--mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--cyan-ink); font-weight:600;}
  header.top{border:1px solid var(--line-strong); background:var(--surface); border-radius:6px; padding:20px 22px; margin-bottom:20px;}
  header.top .sub{color:var(--muted); margin-top:8px; max-width:70ch; font-size:14.5px;}
  header.top .stats{display:flex; gap:22px; flex-wrap:wrap; margin-top:14px; font-family:var(--mono); font-size:12px; color:var(--muted);}
  header.top .stats b{color:var(--ink); font-size:18px; font-weight:700; display:block; font-variant-numeric:tabular-nums;}
  .controls{position:sticky; top:0; z-index:5; background:var(--bg); padding:10px 0 12px; margin-bottom:6px;}
  .searchrow{display:flex; gap:10px; flex-wrap:wrap; align-items:center;}
  #q{flex:1; min-width:220px; font-family:var(--sans); font-size:15px; color:var(--ink); background:var(--raise); border:1px solid var(--line-strong); border-radius:6px; padding:11px 14px;}
  #q::placeholder{color:var(--faint);}
  #q:focus-visible{outline:2px solid var(--cyan); outline-offset:1px;}
  #count{font-family:var(--mono); font-size:12px; color:var(--muted); white-space:nowrap;}
  .chips{display:flex; gap:7px; flex-wrap:wrap; margin-top:12px;}
  .chip{font-family:var(--mono); font-size:11.5px; border:1px solid var(--line-strong); background:var(--surface); color:var(--muted); border-radius:20px; padding:5px 11px; cursor:pointer;}
  .chip:hover{color:var(--ink);}
  .chip[aria-pressed="true"]{background:var(--cyan); border-color:var(--cyan); color:#fff;}
  @media (prefers-color-scheme:dark){.chip[aria-pressed="true"]{color:#04222a;}}
  .chip .c{opacity:.7; margin-left:5px;}
  .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:12px; margin-top:14px;}
  .card{border:1px solid var(--line); background:var(--surface); border-radius:6px; overflow:hidden; display:flex; flex-direction:column;}
  .card-head{padding:14px 16px; cursor:pointer; display:flex; flex-direction:column; gap:8px;}
  .card-head:focus-visible{outline:2px solid var(--cyan); outline-offset:-2px;}
  .card-cat{display:flex; align-items:center; justify-content:space-between; gap:8px;}
  .card-cat .cat{font-family:var(--mono); font-size:10.5px; text-transform:uppercase; letter-spacing:.09em; color:var(--brass); font-weight:600;}
  .card-cat .no{font-family:var(--mono); font-size:10.5px; color:var(--faint); font-variant-numeric:tabular-nums;}
  .card h3{font-size:15.5px; letter-spacing:-.01em; margin:0; line-height:1.3;}
  .card .prob{color:var(--muted); font-size:13.5px; line-height:1.45;}
  .pills{display:flex; gap:6px; flex-wrap:wrap; margin-top:2px;}
  .pill{font-family:var(--mono); font-size:10px; letter-spacing:.04em; text-transform:uppercase; padding:3px 7px; border-radius:4px; font-weight:600;}
  .pill.trust-High{background:var(--crit-bg); color:var(--crit);}
  .pill.trust-Medium{background:var(--warnpill-bg); color:var(--warnpill);}
  .pill.trust-Low{background:var(--surface-2); color:var(--muted);}
  .pill.sev{background:transparent; border:1px solid var(--line-strong); color:var(--faint);}
  .card-body{display:none; padding:0 16px 16px; flex-direction:column; gap:12px; border-top:1px solid var(--line); margin-top:2px; padding-top:14px;}
  .card.open .card-body{display:flex;}
  .card.open .chev{transform:rotate(90deg);}
  .chev{color:var(--faint); transition:transform .15s; font-size:12px;}
  @media (prefers-reduced-motion:reduce){.chev{transition:none;}}
  .field .k{font-family:var(--mono); font-size:10px; text-transform:uppercase; letter-spacing:.1em; color:var(--faint); margin-bottom:4px;}
  .field .v{font-size:13.5px; line-height:1.5;}
  .dodont{display:grid; grid-template-columns:1fr 1fr; gap:10px;}
  @media (max-width:520px){.dodont{grid-template-columns:1fr;}}
  .dd{border-radius:5px; padding:9px 11px; font-size:13px; line-height:1.45;}
  .dd.do{background:var(--ok-bg);} .dd.dont{background:var(--crit-bg);}
  .dd .lab{font-family:var(--mono); font-size:10px; text-transform:uppercase; letter-spacing:.08em; font-weight:700; margin-bottom:4px; display:block;}
  .dd.do .lab{color:var(--ok);} .dd.dont .lab{color:var(--crit);}
  .code{font-family:var(--mono); font-size:12px; line-height:1.55; background:var(--surface-2); border:1px solid var(--line); border-radius:5px; padding:10px 12px; overflow-x:auto; white-space:pre-wrap; word-break:break-word; color:var(--ink);}
  .code.anti{border-style:dashed; color:var(--muted);}
  .when{font-size:12.5px; color:var(--muted);} .when b{color:var(--ink); font-weight:600;}
  .empty{text-align:center; color:var(--muted); font-family:var(--mono); font-size:13px; padding:60px 20px; display:none;}
  footer{margin-top:26px; font-family:var(--mono); font-size:11.5px; color:var(--faint); line-height:1.6; border-top:1px solid var(--line); padding-top:12px;}
</style>
</head>
<body>
<div class="page"><div class="wrap">
  <header class="top">
    <div class="eyebrow">ai-ux · design intelligence</div>
    <h1 style="margin-top:6px">AI-Native Interface Patterns</h1>
    <p class="sub">A searchable, code-ready UX pattern library for products built on LLMs, agents, and voice — the parts of the interface that classic design systems never covered. Each pattern pairs the problem with a concrete do / don't and a paste-ready snippet.</p>
    <div class="stats">
      <span><b>__TOTAL__</b>patterns</span>
      <span><b>__NCAT__</b>categories</span>
      <span><b>MIT</b>open source</span>
    </div>
  </header>
  <div class="controls">
    <div class="searchrow">
      <input id="q" type="search" placeholder="Search patterns — e.g. streaming, hallucination, tool call, undo…" aria-label="Search patterns" />
      <span id="count"></span>
    </div>
    <div class="chips" id="chips"></div>
  </div>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty">No patterns match that filter.</div>
  <footer>
    <span style="color:var(--cyan-ink); font-weight:600">ai-ux database developed by Azka</span> · MIT · generated from <span style="color:var(--muted)">data/ai-ux-patterns.csv</span>.<br>
    Click any card to expand. Patterns describe UX approaches, not endorsements of any specific product.
  </footer>
</div></div>
<script id="data" type="application/json">__PAYLOAD__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var grid=document.getElementById('grid'), chipsEl=document.getElementById('chips');
  var countEl=document.getElementById('count'), emptyEl=document.getElementById('empty'), qEl=document.getElementById('q');
  var activeCat=null, query='';
  var cats={}; DATA.forEach(function(d){cats[d.cat]=(cats[d.cat]||0)+1;});
  var catNames=Object.keys(cats).sort();
  function mkChip(label,count,val){
    var b=document.createElement('button'); b.className='chip'; b.setAttribute('aria-pressed',String(activeCat===val));
    b.innerHTML=label+(count!=null?' <span class="c">'+count+'</span>':'');
    b.onclick=function(){activeCat=(activeCat===val?null:val); render(); syncChips();};
    b._val=val; return b;
  }
  chipsEl.appendChild(mkChip('All',DATA.length,null));
  catNames.forEach(function(c){chipsEl.appendChild(mkChip(c,cats[c],c));});
  function syncChips(){Array.prototype.forEach.call(chipsEl.children,function(ch){ch.setAttribute('aria-pressed',String(activeCat===ch._val));});}
  function el(t,c,x){var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;}
  function card(d){
    var c=el('div','card');
    var head=el('div','card-head'); head.tabIndex=0; head.setAttribute('role','button');
    var catRow=el('div','card-cat');
    catRow.appendChild(el('span','cat',d.cat));
    var right=el('span'); right.style.display='flex'; right.style.gap='8px'; right.style.alignItems='center';
    right.appendChild(el('span','no','#'+d.no)); right.appendChild(el('span','chev','▶'));
    catRow.appendChild(right); head.appendChild(catRow);
    head.appendChild(el('h3',null,d.name)); head.appendChild(el('p','prob',d.prob));
    var pills=el('div','pills');
    pills.appendChild(el('span','pill trust-'+d.trust,'trust '+d.trust));
    pills.appendChild(el('span','pill sev','sev '+d.sev));
    head.appendChild(pills); c.appendChild(head);
    var body=el('div','card-body');
    function field(k,v){var f=el('div','field'); f.appendChild(el('div','k',k)); f.appendChild(el('div','v',v)); return f;}
    body.appendChild(field('Solution',d.sol));
    var dd=el('div','dodont');
    var doB=el('div','dd do'); doB.appendChild(el('span','lab','Do')); doB.appendChild(el('span',null,d.do));
    var dontB=el('div','dd dont'); dontB.appendChild(el('span','lab',"Don't")); dontB.appendChild(el('span',null,d.dont));
    dd.appendChild(doB); dd.appendChild(dontB); body.appendChild(dd);
    var cf=el('div','field'); cf.appendChild(el('div','k','Code')); cf.appendChild(el('pre','code',d.code)); body.appendChild(cf);
    var af=el('div','field'); af.appendChild(el('div','k','Anti-pattern')); af.appendChild(el('pre','code anti',d.anti)); body.appendChild(af);
    var w=el('div','when'); w.innerHTML='<b>When:</b> '; w.appendChild(document.createTextNode(d.when)); body.appendChild(w);
    c.appendChild(body);
    function toggle(){c.classList.toggle('open');}
    head.onclick=toggle;
    head.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault(); toggle();}};
    return c;
  }
  function render(){
    var q=query.trim().toLowerCase(), shown=0; grid.textContent='';
    DATA.forEach(function(d){
      if(activeCat && d.cat!==activeCat) return;
      if(q){var hay=(d.name+' '+d.cat+' '+d.kw+' '+d.prob+' '+d.sol+' '+d.when).toLowerCase(); if(hay.indexOf(q)===-1) return;}
      grid.appendChild(card(d)); shown++;
    });
    countEl.textContent=shown+' / '+DATA.length+' shown';
    emptyEl.style.display=shown?'none':'block';
  }
  qEl.addEventListener('input',function(){query=qEl.value; render();});
  render();
})();
</script>
</body>
</html>
"""

HTML = HTML.replace("__PAYLOAD__", payload).replace("__TOTAL__", str(total)).replace("__NCAT__", str(ncat))
OUT.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT.name}: {total} patterns / {ncat} categories")
