import html, json

PAGE_CSS = """
:root{--bg:#f7f4ee;--ink:#3a342b;--accent:#8a5a2b;--card:#fffdf8;--line:#e5ddcf}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:"Noto Serif SC","Songti SC","STSong","SimSun",serif;padding-bottom:60px}
.wrap{max-width:1100px;margin:0 auto;padding:0 18px}
header{padding:46px 0 10px;border-bottom:2px solid var(--line);margin-bottom:24px}
header h1{font-size:30px;letter-spacing:2px;color:var(--accent)}
header .sub{margin-top:6px;font-size:14px;color:#8a8174}
nav.bar{margin:14px 0 20px;display:flex;gap:14px;flex-wrap:wrap}
nav.bar a{color:var(--ink);text-decoration:none;border:1px solid var(--line);padding:7px 16px;border-radius:20px;font-size:14px;background:#fff}
nav.bar a.on{background:var(--accent);color:#fff;border-color:var(--accent)}
nav.bar a:hover{border-color:var(--accent)}
nav.bar .sep{align-self:center;color:#c9bfae;font-size:15px;user-select:none}
.filter{margin:6px 0 20px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:10px}
.filter .ft{font-size:13.5px;color:#8a8174;margin-bottom:10px;letter-spacing:.5px}
.filter .chips{display:flex;flex-wrap:wrap;gap:9px}
.filter label{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:20px;padding:6px 14px;font-size:13.5px;cursor:pointer;background:#fff;user-select:none;transition:.12s}
.filter label:hover{border-color:var(--accent)}
.filter label input{accent-color:var(--accent);width:14px;height:14px;cursor:pointer}
.filter label.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.filter .info{margin-top:10px;font-size:13px;color:#8a8174}
.filter .info b{color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;cursor:pointer;transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column}
.card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(60,45,20,.14)}
.card img{width:100%;height:330px;object-fit:cover;display:block;background:#eee}
.card .meta{padding:12px 14px 14px;flex:1;display:flex;flex-direction:column;gap:6px}
.card .fn{font-size:12px;color:#a29784;letter-spacing:.5px}
.card .desc{font-size:14px;line-height:1.7;color:var(--ink)}
.card .people{margin-top:auto;font-size:12.5px;color:var(--accent)}
.card .people b{font-weight:600}
.card .people.none{color:#a29784}
.pager{margin:28px 0 8px;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap}
.pager button{border:1px solid var(--line);background:#fff;color:var(--ink);padding:8px 14px;border-radius:8px;font-size:14px;cursor:pointer;font-family:inherit}
.pager button:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}
.pager button:disabled{opacity:.4;cursor:default}
.pager .pg{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:34px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff;cursor:pointer}
.pager .pg.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.lb{position:fixed;inset:0;background:rgba(0,0,0,.93);display:none;z-index:99;align-items:center;justify-content:center;flex-direction:column}
.lb.on{display:flex}
.lb img{max-width:92vw;max-height:70vh;object-fit:contain;border-radius:4px}
.lb .cap{max-width:640px;margin-top:16px;color:#eee;font-size:15px;line-height:1.8;text-align:center;padding:0 20px}
.lb .cap .t{color:#cfb795;font-size:13px;display:block;margin-bottom:5px}
.lb .nav{position:absolute;top:50%;transform:translateY(-50%);color:#fff;font-size:40px;cursor:pointer;padding:12px;user-select:none;background:rgba(255,255,255,.06);border-radius:8px}
.lb .nav.l{left:16px}.lb .nav.r{right:16px}
.lb .x{position:absolute;top:18px;right:26px;color:#fff;font-size:34px;cursor:pointer}
.stats{margin:22px 0;padding:16px 20px;background:var(--card);border:1px solid var(--line);border-radius:10px;font-size:15px;line-height:1.9}
.portal .sel{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:26px}
.portal .sel a{display:block;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;transition:.15s}
.portal .sel a:hover{transform:translateY(-3px);box-shadow:0 10px 26px rgba(60,45,20,.16)}
.portal .sel img{width:100%;height:230px;object-fit:cover}
.portal .sel .t{padding:15px 18px}
.portal .sel .t h2{font-size:20px;color:var(--accent)}
.portal .sel .t p{margin-top:6px;font-size:14px;color:#8a8174;line-height:1.7}
footer{margin-top:46px;text-align:center;font-size:12px;color:#a29784}
@media(max-width:560px){.grid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}.card img{height:220px}}
"""

SUB_JS = """
var ALL=ITEMS;
var PER=12, PAGE=0, SEL=new Set();
function esc(v){return String(v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function peopleOf(it){return it[3]?it[3].split('、'):[];}
function match(it){
  if(SEL.size===0) return true;
  var ps=peopleOf(it);
  if(SEL.has('__none__')){
    if(ps.length===0) return SEL.size===1;
    return false;
  }
  return Array.from(SEL).every(function(p){return ps.indexOf(p)>=0;});
}
function filtered(){return ALL.filter(match);}
function setSel(name,on){
  if(on) SEL.add(name); else SEL.delete(name);
  PAGE=0; render(); updateChips();
}
function updateChips(){
  document.querySelectorAll('.filter label').forEach(function(l){
    var v=l.getAttribute('data-v');
    l.classList.toggle('on', SEL.has(v));
    var cb=l.querySelector('input'); if(cb) cb.checked=SEL.has(v);
  });
}
function render(){
  var arr=filtered(), pages=Math.max(1,Math.ceil(arr.length/PER));
  if(PAGE>=pages)PAGE=pages-1; if(PAGE<0)PAGE=0;
  var slice=arr.slice(PAGE*PER,(PAGE+1)*PER);
  var g='';
  slice.forEach(function(it,si){
    var idx=PAGE*PER+si;
    var pe='';
    if(it[3]) pe='<div class="people"><b>'+esc(it[3])+'</b></div>';
    else pe='<div class="people none">未识别到标记人物</div>';
    g+='<figure class="card" data-idx="'+idx+'" onclick="lbOpen('+idx+')">'
      +'<img loading="lazy" src="'+esc(it[0])+'" alt="'+esc(it[1])+'">'
      +'<figcaption class="meta"><div class="fn">'+esc(it[1])+'</div>'
      +'<div class="desc">'+esc(it[2])+'</div>'+pe+'</figcaption></figure>';
  });
  document.getElementById('grid').innerHTML=g;
  document.getElementById('info').innerHTML='共 <b>'+arr.length+'</b> 张 · 第 '+(PAGE+1)+' / '+pages+' 页'+(SEL.size?(' · 筛选:'+Array.from(SEL).map(function(n){return n==='__none__'?'未识别到标记人物':esc(n);}).join('、')):'');
  var p='<button '+(PAGE===0?'disabled':'')+' onclick="goto('+(PAGE-1)+')">‹ 上一页</button>';
  for(var i=0;i<pages;i++){
    p+='<span class="pg'+(i===PAGE?' on':'')+'" onclick="goto('+i+')">'+(i+1)+'</span>';
  }
  p+='<button '+(PAGE>=pages-1?'disabled':'')+' onclick="goto('+(PAGE+1)+')">下一页 ›</button>';
  document.getElementById('pager').innerHTML=p;
  CURarr=arr;
}
function goto(p){PAGE=p;render();}
var CURarr=[];
function lbOpen(i){
  var it=CURarr[i];
  CUR=i;
  document.getElementById('lbimg').src=it[0];
  document.getElementById('lbcap').innerHTML='<span class=t>'+esc(it[1])+'</span>'+(it[3]?'<div>人物:'+esc(it[3])+'</div>':'')+esc(it[2]);
  document.getElementById('lightbox').classList.add('on');
  document.body.style.overflow='hidden';
}
function lbClose(){document.getElementById('lightbox').classList.remove('on');document.body.style.overflow='';}
function lbMove(d){
  var n=CURarr.length;if(!n)return;
  var ni=((CUR+d)%n+n)%n;
  if(ni<0||ni>=n)return;
  var pg=Math.floor(ni/PER);
  if(pg!==PAGE){PAGE=pg;render();}
  var it=CURarr[ni];
  CUR=ni;
  document.getElementById('lbimg').src=it[0];
  document.getElementById('lbcap').innerHTML='<span class=t>'+esc(it[1])+'</span>'+(it[3]?'<div>人物:'+esc(it[3])+'</div>':'')+esc(it[2]);
}
document.addEventListener('click',function(e){
  var c=e.target.closest('.card');if(!c)return;
  var i=parseInt(c.getAttribute('data-idx'),10);if(!isNaN(i))lbOpen(i);
});
document.addEventListener('keydown',function(e){
  if(!document.getElementById('lightbox').classList.contains('on'))return;
  if(e.key==='Escape')lbClose();if(e.key==='ArrowLeft')lbMove(-1);if(e.key==='ArrowRight')lbMove(1);
});
document.getElementById('lightbox').addEventListener('click',function(e){if(e.target===this)lbClose();});
render();
"""

def page(title, body, nav_on=None, items=None, people_list=None, counts=(0, 0, 0), config=None):
    """整页 HTML 模板。counts=(彩色,黑白,证件照 张数) 用于导航/页脚计数。

    items: [{"rel","fn","desc","people"}, ...]  按展示顺序
    people_list: 该分类出现的全部人物名(用于生成筛选 chips)
    """
    if items is None:
        items = []
    config = config or {}
    people_order = config.get("people_order", [])
    n_c, n_b, n_i = counts

    def nlink(href, txt, cur):
        cls = ' class="on"' if cur else ''
        return f'<a href="{href}"{cls}>{txt}</a>'

    nav = ['<nav class="bar">' + nlink("./", "门户", nav_on is None) + '<span class="sep">|</span>',
           nlink("color.html", f"彩色 · {n_c}", nav_on == "color"),
           nlink("bw.html", f"黑白 · {n_b}", nav_on == "bw"),
           nlink("id.html", f"证件照 · {n_i}", nav_on == "id") + '</nav>']
    items_json = json.dumps([(c['rel'], c['fn'], c['desc'].replace(chr(10), ' '), c['people']) for c in items], ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    # 人物筛选 chips(该分类出现的人物 + 未识别项)。排序: 自定义顺序(用户指定)在前,其余按字典序
    chips = ''
    if people_list:
        rank = {p: i for i, p in enumerate(people_order)}
        pl = sorted(people_list, key=lambda x: (rank.get(x, 99), x))
        parts = []
        for name in pl:
            parts.append(f'<label data-v="{html.escape(name)}"><input type="checkbox" onchange="setSel(this.closest(\'label\').getAttribute(\'data-v\'),this.checked)">{html.escape(name)}</label>')
        # 「未识别到标记人物」tag 仅当该分类确实存在无标记照片时显示
        none_items = [c for c in items if not c['people']]
        none_lbl = ''
        if none_items:
            none_lbl = '<label data-v="__none__"><input type="checkbox" onchange="setSel(this.closest(\'label\').getAttribute(\'data-v\'),this.checked)">未识别到标记人物</label>'
        can_sel = '<a href="#" onclick="SEL.clear();render();updateChips();return false;" style="font-size:13px;color:#8a8174;margin-left:auto;align-self:center">清空筛选</a>'
        chips = f'<div class="filter"><div class="ft">人物筛选(可多选,勾选多人时需同时出现才显示)</div><div class="chips">{"".join(parts)}{none_lbl}{can_sel}</div><div class="info" id="info"></div></div>'

    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="{'noindex, nofollow' if config.get('noindex', True) else 'index, follow'}">
<title>{html.escape(title)}</title><style>{PAGE_CSS}</style></head>
<body><div class="wrap"><header><h1>{html.escape(config.get("title", "家庭老照片档案"))}</h1>
<div class="sub">{html.escape(config.get("subtitle", "扫描整理"))} · 共 {n_c + n_b + n_i} 张 · 点击照片看大图与说明</div>
{''.join(nav)}</header>{chips}{body}<footer>{html.escape(config.get("footer", "家庭老照片档案"))}</footer></div>
<div class="lb" id="lightbox"><span class="x" onclick="lbClose()">×</span>
<span class="nav l" onclick="lbMove(-1)">‹</span><img id="lbimg" src="">
<span class="nav r" onclick="lbMove(1)">›</span><div class="cap" id="lbcap"></div></div>
<script>
var ITEMS={items_json};
{SUB_JS if items else ''}
</script></body></html>"""
