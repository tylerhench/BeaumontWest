#!/usr/bin/env python3
"""Generate the Beaumont West Solutions static site."""
import re, os, shutil, html

# ---------------------------------------------------------------- EDIT HERE
# Change any of these once and every page picks it up on the next build.
BRAND         = "Beaumont West Solutions"
SITE_URL      = "https://beaumontwest.com"   # no trailing slash
EMAIL         = "hello@beaumontwest.com"
PHONE_DISPLAY = "(555) 014-2200"
PHONE_LINK    = "+15550142200"               # digits only, with country code
YEAR          = "2026"
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "assets")   # logo + icon source files
OUT  = HERE                           # pages are written next to this script

# ---------------------------------------------------------------- brand SVGs
def read(name):
    with open(os.path.join(SRC, name)) as f:
        return f.read()

def strip_shell(svg, idpfx):
    """Return inner markup of an svg, with ids namespaced, sized by CSS."""
    inner = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.S)
    inner = re.sub(r'<title>.*?</title>', '', inner, flags=re.S)
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    for old in re.findall(r'id="([^"]+)"', inner):
        inner = inner.replace('id="%s"' % old, 'id="%s-%s"' % (idpfx, old))
        inner = inner.replace('url(#%s)' % old, 'url(#%s-%s)' % (idpfx, old))
    return inner.strip()

def viewbox(svg):
    return re.search(r'viewBox="([^"]+)"', svg).group(1)

LOCKUP_H   = read("bws-lockup-horizontal.svg")
LOCKUP_REV = read("bws-lockup-primary-reversed.svg")
BADGE_FULL = read("bws-logo-primary.svg")

def header_lockup(idpfx):
    """Horizontal lockup with the badge's B and S removed.

    The usage guide reserves the full mark for 64px and up; at header scale the
    badge lands around 34px, so the simplified badge is the correct one to pair
    with the wordmark."""
    svg = LOCKUP_H
    # the two cream letterform paths inside the badge group are the B and the S
    letters = re.findall(r'<path d="[^"]+" fill="#FDF0DC"/>', svg)
    for p in letters:
        svg = svg.replace(p, '')
    return ('<svg class="lockup lockup--header" viewBox="%s" role="img" '
            'aria-label="Beaumont West Solutions">%s</svg>'
            % (viewbox(LOCKUP_H), strip_shell(svg, idpfx)))

def footer_lockup(idpfx):
    return ('<svg class="lockup lockup--footer" viewBox="%s" role="img" '
            'aria-label="Beaumont West Solutions">%s</svg>'
            % (viewbox(LOCKUP_REV), strip_shell(LOCKUP_REV, idpfx)))

def badge(idpfx, cls="badge"):
    return ('<svg class="%s" viewBox="%s" role="img" aria-label="Beaumont West '
            'Solutions mark">%s</svg>'
            % (cls, viewbox(BADGE_FULL), strip_shell(BADGE_FULL, idpfx)))

# ------------------------------------------------------------------ dividers
RIDGE = """<div class="divider divider--ridge" aria-hidden="true">
<svg viewBox="0 0 1440 150" preserveAspectRatio="none" focusable="false">
<path class="ridge-far" d="M0,150 L0,90 L199,60 L419,78 L680,44 L919,72 L1180,52 L1440,70 L1440,150 Z"/>
<path class="ridge-back" d="M0,150 L0,96 L180,58 L320,82 L559,40 L760,78 L980,50 L1150,80 L1379,46 L1440,60 L1440,150 Z"/>
<path class="ridge-front" d="M0,150 L0,118 L119,106 L250,46 L330,94 L470,18 L640,102 L720,62 L790,90 L900,34 L1029,98 L1139,56 L1209,86 L1330,30 L1440,82 L1440,150 Z"/>
</svg></div>"""

def wave(to="paper"):
    """Teal above, light below — the coastal counterpart to the ridge."""
    return """<div class="divider divider--wave to-%s" aria-hidden="true">
<svg viewBox="0 0 1440 92" preserveAspectRatio="none" focusable="false">
<path class="wave" d="M0,0 L1440,0 L1440,30 C1250,84 1080,88 920,52 C760,16 620,-4 460,34 C300,72 158,70 0,8 Z"/>
</svg></div>""" % to

RIDGE_CREAM = RIDGE.replace('divider--ridge"', 'divider--ridge from-cream"')
WAVE = wave("paper")
WAVE_CREAM = wave("cream")

# ----------------------------------------------------------------------- CSS
CSS = r"""
:root{
  --teal:#1B4552; --teal-mid:#38606E; --teal-deep:#143641;
  --cream:#FDF0DC; --paper:#FBF6EC; --coral:#E86F51; --peach:#F4A261;
  --rule:#C9D3D6;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --body:"Newsreader",Georgia,"Times New Roman",serif;
  --shell:min(1120px,100% - 48px);
  --r:14px;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{
  margin:0;background:var(--paper);color:var(--teal);
  font-family:var(--body);font-size:18px;line-height:1.65;font-optical-sizing:auto;
  font-synthesis-weight:none;-webkit-font-smoothing:antialiased;
}
img,svg{max-width:100%}
a{color:inherit}

/* ---------- type ---------- */
h1,h2,h3,h4,.display{
  font-family:var(--display);font-weight:600;
  font-variation-settings:"wdth" 108;
  line-height:1.05;letter-spacing:-.012em;margin:0;
}
h1{font-size:clamp(38px,5.6vw,68px);line-height:1.0;letter-spacing:-.022em}
h2{font-size:clamp(28px,3.8vw,44px);letter-spacing:-.018em}
h3{font-size:clamp(19px,2vw,22px);line-height:1.2;letter-spacing:-.005em}
p{margin:0 0 1.1em}
p:last-child{margin-bottom:0}
.eyebrow{
  font-family:var(--display);font-weight:600;font-size:12px;
  letter-spacing:.19em;text-transform:uppercase;color:var(--teal-mid);
  margin:0 0 18px;display:block;font-variation-settings:"wdth" 100;
}
.lede{font-size:clamp(19px,2.1vw,22px);line-height:1.55;color:var(--teal-mid);max-width:56ch}
.small{font-size:15px;line-height:1.6;color:var(--teal-mid)}

/* ---------- layout ---------- */
.wrap{width:var(--shell);margin-inline:auto}
.section{padding-block:clamp(64px,8.5vw,110px)}
.section--tight{padding-block:clamp(48px,6vw,76px)}
.band-paper{background:var(--paper)}
.band-cream{background:var(--cream)}
.band-teal{background:var(--teal);color:var(--cream)}
.band-teal .eyebrow{color:rgba(253,240,220,.7)}
.band-teal .lede,.band-teal .small{color:rgba(253,240,220,.82)}
.head{max-width:62ch;margin-bottom:clamp(36px,4.5vw,56px)}
.head--center{margin-inline:auto;text-align:center}
.grid{display:grid;gap:22px}
.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(268px,1fr))}
.split{display:grid;gap:clamp(32px,5vw,72px);grid-template-columns:1fr;align-items:start}
@media(min-width:900px){.split{grid-template-columns:0.85fr 1.15fr}}

/* ---------- buttons ---------- */
.btn{
  display:inline-flex;align-items:center;gap:10px;
  font-family:var(--display);font-weight:600;font-size:13.5px;
  letter-spacing:.09em;text-transform:uppercase;text-decoration:none;
  padding:15px 28px;border-radius:999px;border:1.6px solid transparent;
  transition:background .18s ease,color .18s ease,border-color .18s ease,transform .18s ease;
  cursor:pointer;
}
.btn--primary{background:var(--teal);color:var(--cream)}
.btn--primary:hover{background:var(--teal-deep);transform:translateY(-1px)}
.btn--ghost{border-color:rgba(27,69,82,.28);color:var(--teal)}
.btn--ghost:hover{border-color:var(--teal);background:rgba(27,69,82,.05)}
.band-teal .btn--primary{background:var(--cream);color:var(--teal)}
.band-teal .btn--primary:hover{background:#fff}
.band-teal .btn--ghost{border-color:rgba(253,240,220,.4);color:var(--cream)}
.band-teal .btn--ghost:hover{border-color:var(--cream);background:rgba(253,240,220,.09)}
.btn-row{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.arrow{transition:transform .18s ease}
.btn:hover .arrow{transform:translateX(3px)}

/* ---------- header ---------- */
.masthead{
  position:sticky;top:0;z-index:60;background:rgba(251,246,236,.93);
  backdrop-filter:blur(9px);border-bottom:1px solid var(--rule);
}
.masthead__in{display:flex;align-items:center;justify-content:space-between;
  gap:24px;width:var(--shell);margin-inline:auto;padding-block:14px}
.lockup{display:block;height:auto}
.lockup--header{height:46px;width:auto}
.brandlink{display:inline-flex;text-decoration:none;border-radius:6px}
.nav{display:none;align-items:center;gap:30px}
.nav a{
  font-family:var(--display);font-weight:500;font-size:15px;text-decoration:none;
  padding:6px 0;position:relative;letter-spacing:.005em;
}
.nav a::after{
  content:"";position:absolute;left:0;right:0;bottom:0;height:2px;
  background:var(--teal);transform:scaleX(0);transform-origin:left;
  transition:transform .2s ease;
}
.nav a:hover::after{transform:scaleX(1)}
.nav a[aria-current="page"]::after{transform:scaleX(1);background:var(--coral)}
.masthead .btn{padding:12px 22px;font-size:12.5px;display:none}
@media(min-width:900px){.masthead .btn{display:inline-flex}}
.navtoggle{
  display:inline-flex;flex-direction:column;justify-content:center;gap:5px;
  width:44px;height:44px;padding:0 10px;background:none;border:1px solid var(--rule);
  border-radius:10px;cursor:pointer;
}
.navtoggle span{display:block;height:1.8px;background:var(--teal);border-radius:2px;
  transition:transform .2s ease,opacity .2s ease}
.navtoggle[aria-expanded="true"] span:nth-child(1){transform:translateY(6.8px) rotate(45deg)}
.navtoggle[aria-expanded="true"] span:nth-child(2){opacity:0}
.navtoggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-6.8px) rotate(-45deg)}
.mobilenav{display:none;border-top:1px solid var(--rule);background:var(--paper)}
.mobilenav.open{display:block}
.mobilenav ul{list-style:none;margin:0;padding:8px 0 20px;width:var(--shell);margin-inline:auto}
.mobilenav a{
  display:block;padding:14px 2px;text-decoration:none;font-family:var(--display);
  font-weight:500;font-size:17px;border-bottom:1px solid var(--rule);
}
.mobilenav li:last-child a{border-bottom:none;padding-top:20px}
@media(min-width:900px){
  .nav{display:flex}
  .navtoggle{display:none}
  .mobilenav,.mobilenav.open{display:none}
}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;background:var(--paper);
  padding-block:clamp(52px,7vw,86px) 0;text-align:center}
.hero__glow{
  position:absolute;left:50%;top:-14%;width:min(760px,120%);aspect-ratio:1;
  transform:translateX(-50%);border-radius:50%;pointer-events:none;
  background:radial-gradient(circle,rgba(232,111,81,.19) 0%,rgba(232,111,81,.07) 42%,rgba(232,111,81,0) 68%);
}
.hero__in{position:relative;width:var(--shell);margin-inline:auto}
.badge{width:104px;height:104px;display:block;margin:0 auto 26px}
.hero h1{max-width:16ch;margin-inline:auto}
.hero .lede{margin:22px auto 0;text-align:center}
.hero .btn-row{justify-content:center;margin-top:34px}
.hero__foot{margin-top:clamp(44px,5vw,66px);padding-bottom:6px}

/* ---------- dividers ---------- */
.divider{line-height:0}
.divider svg{display:block;width:100%}
.divider--ridge{background:var(--paper)}
.divider--ridge svg{height:clamp(84px,10vw,132px)}
.ridge-far{fill:var(--teal-mid);opacity:.45}
.ridge-back{fill:var(--teal-mid)}
.ridge-front{fill:var(--teal)}
.divider--wave{background:var(--paper)}
.divider--wave.to-cream{background:var(--cream)}
.divider--wave svg{height:clamp(50px,5.5vw,82px)}
.wave{fill:var(--teal)}
.divider--ridge.from-cream{background:var(--cream)}

/* ---------- cards ---------- */
.card{
  background:var(--cream);border:1px solid var(--rule);border-radius:var(--r);
  padding:clamp(24px,3vw,32px);
}
.band-cream .card{background:var(--paper)}
.band-teal .card{background:var(--cream);border-color:transparent;color:var(--teal)}
.band-teal .card .small{color:var(--teal-mid)}
.card h3{margin-bottom:10px}
.card p{font-size:16.5px;line-height:1.6;color:var(--teal-mid)}
.band-teal .card p{color:var(--teal-mid)}
.card__tag{
  font-family:var(--display);font-size:11.5px;font-weight:600;letter-spacing:.16em;
  text-transform:uppercase;color:var(--teal-mid);display:block;margin-bottom:12px;
}
.sun{width:9px;height:9px;border-radius:50%;background:var(--coral);flex:none;margin-top:11px}

/* ---------- lists ---------- */
.checks{list-style:none;margin:0;padding:0;display:grid;gap:15px}
.checks li{display:flex;gap:14px;align-items:flex-start;font-size:17px;line-height:1.55}
.facts{
  list-style:none;margin:0;padding:0;display:grid;gap:14px 34px;
  grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
}
.facts li{display:flex;gap:12px;align-items:flex-start;font-family:var(--display);
  font-size:14.5px;font-weight:500;line-height:1.45}

/* ---------- steps ---------- */
.steps{display:grid;gap:2px;margin-top:8px;border-top:1px solid rgba(253,240,220,.22)}
.step{display:grid;gap:6px 28px;padding:26px 0;border-bottom:1px solid rgba(253,240,220,.22)}
@media(min-width:760px){.step{grid-template-columns:74px 1fr}}
.step__n{
  font-family:var(--display);font-weight:600;font-size:15px;letter-spacing:.12em;
  color:rgba(253,240,220,.6);padding-top:5px;
}
.step h3{margin-bottom:6px}
.step p{color:rgba(253,240,220,.8);font-size:16.5px;margin:0}

/* ---------- browser mockups ---------- */
.mock{border-radius:12px;overflow:hidden;border:1px solid var(--rule);background:#fff}
.mock__bar{display:flex;align-items:center;gap:6px;padding:9px 12px;background:#EDE6DA;
  border-bottom:1px solid var(--rule)}
.mock__dot{width:8px;height:8px;border-radius:50%;background:#C6BCAB}
.mock__url{flex:1;margin-left:8px;height:16px;border-radius:8px;background:#FBF6EC;
  font-family:var(--display);font-size:9.5px;letter-spacing:.04em;color:#8C9BA1;
  display:flex;align-items:center;padding:0 9px}
.mock__body{padding:0}
.mock__hero{padding:26px 22px 24px;color:#fff}
.mock__eyebrow{font-family:var(--display);font-size:8.5px;letter-spacing:.2em;
  text-transform:uppercase;opacity:.82;margin-bottom:8px}
.mock__h{font-family:var(--display);font-weight:600;font-size:21px;line-height:1.1;margin:0 0 10px}
.mock__p{font-size:11.5px;line-height:1.5;opacity:.85;margin:0 0 14px;max-width:34ch}
.mock__btn{display:inline-block;font-family:var(--display);font-size:9px;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;padding:8px 14px;border-radius:999px}
.mock__row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:16px 22px 22px;background:#fff}
.mock__tile{border-radius:7px;padding:11px 10px;font-family:var(--display);font-size:9.5px;
  font-weight:600;line-height:1.35;min-height:58px;display:flex;align-items:flex-end}

/* ---------- faq ---------- */
.faq{border-top:1px solid var(--rule)}
.faq details{border-bottom:1px solid var(--rule)}
.faq summary{
  list-style:none;cursor:pointer;padding:22px 40px 22px 0;position:relative;
  font-family:var(--display);font-weight:600;font-size:18px;line-height:1.35;
}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{
  content:"";position:absolute;right:6px;top:31px;width:11px;height:11px;
  border-right:2px solid var(--teal);border-bottom:2px solid var(--teal);
  transform:rotate(45deg);transition:transform .2s ease;
}
.faq details[open] summary::after{transform:rotate(225deg)}
.faq p{padding:0 40px 22px 0;color:var(--teal-mid);font-size:17px;margin:0}

/* ---------- form ---------- */
.form{display:grid;gap:20px}
.field{display:grid;gap:8px}
.field label{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--teal-mid)}
.field input,.field select,.field textarea{
  font-family:var(--body);font-size:17px;color:var(--teal);background:var(--paper);
  border:1.5px solid var(--rule);border-radius:10px;padding:14px 15px;width:100%;
  transition:border-color .16s ease;
}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--teal)}
.field textarea{min-height:150px;resize:vertical}
.field--pair{display:grid;gap:20px;grid-template-columns:1fr}
@media(min-width:680px){.field--pair{grid-template-columns:1fr 1fr}}
.formnote{font-size:14.5px;color:var(--teal-mid);margin:0}
.formstatus{display:none;border-radius:var(--r);border:1.5px solid var(--teal);
  background:var(--paper);padding:22px 24px}
.formstatus.show{display:block}
.formstatus h3{margin-bottom:8px}

/* ---------- contact rail ---------- */
.rail{display:grid;gap:26px}
.rail__item{border-top:1px solid var(--rule);padding-top:18px}
.rail__item h3{font-size:16px;margin-bottom:6px}
.rail__item a{font-family:var(--display);font-weight:500;text-decoration:none;
  border-bottom:1.5px solid var(--coral);padding-bottom:1px}

/* ---------- footer ---------- */
.foot{background:var(--teal);color:var(--cream);padding-block:clamp(52px,6vw,72px) 30px}
.lockup--footer{height:88px;width:auto}
.foot__top{display:grid;gap:40px;grid-template-columns:1fr}
@media(min-width:820px){.foot__top{grid-template-columns:1.2fr .8fr .8fr}}
.foot h4{font-family:var(--display);font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;
  font-weight:600;color:rgba(253,240,220,.62);margin:0 0 16px}
.foot ul{list-style:none;margin:0;padding:0;display:grid;gap:11px}
.foot a{text-decoration:none;font-family:var(--display);font-size:15px;font-weight:400;
  color:rgba(253,240,220,.92)}
.foot a:hover{color:#fff;text-decoration:underline;text-underline-offset:4px}
.foot__blurb{margin:22px 0 0;font-size:16px;color:rgba(253,240,220,.78);max-width:38ch}
.foot__base{margin-top:46px;padding-top:22px;border-top:1px solid rgba(253,240,220,.2);
  display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:space-between;
  font-size:13.5px;color:rgba(253,240,220,.62);font-family:var(--display)}

/* ---------- a11y + motion ---------- */
.skip{position:absolute;left:-9999px;top:0;background:var(--teal);color:var(--cream);
  padding:12px 18px;border-radius:0 0 8px 0;z-index:100;font-family:var(--display);font-size:14px}
.skip:focus{left:0}
:focus-visible{outline:3px solid var(--coral);outline-offset:3px;border-radius:4px}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
.hero .badge{animation:rise .9s cubic-bezier(.2,.7,.3,1) both}
.hero h1{animation:rise .9s .1s cubic-bezier(.2,.7,.3,1) both}
.hero .lede,.hero .btn-row{animation:rise .9s .18s cubic-bezier(.2,.7,.3,1) both}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation:none!important;transition:none!important}
  .reveal{opacity:1;transform:none}
}
"""

JS = r"""
(function(){
  var t=document.querySelector('.navtoggle'), m=document.getElementById('mobilenav');
  if(t&&m){t.addEventListener('click',function(){
    var open=t.getAttribute('aria-expanded')==='true';
    t.setAttribute('aria-expanded',String(!open));
    m.classList.toggle('open',!open);
  });}
  var els=document.querySelectorAll('.reveal');
  if(!window.IntersectionObserver||window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    els.forEach(function(e){e.classList.add('in');});
  }else{
    var io=new IntersectionObserver(function(en){
      en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});
    },{rootMargin:'0px 0px -8% 0px',threshold:.08});
    els.forEach(function(e){io.observe(e);});
  }
  var f=document.getElementById('projectform');
  if(f){f.addEventListener('submit',function(ev){
    var action=f.getAttribute('action')||'';
    if(action.indexOf('YOUR_FORM_ID')>-1){
      ev.preventDefault();
      if(!f.checkValidity()){f.reportValidity();return;}
      document.getElementById('formstatus').classList.add('show');
      f.style.display='none';
      window.scrollTo({top:f.parentNode.offsetTop-90,behavior:'smooth'});
    }
  });}
})();
"""

# ------------------------------------------------------------------- chrome
NAV = [("index.html","Home"),("services.html","Services"),("work.html","Work"),
       ("about.html","About"),("contact.html","Contact")]

def nav_links(current, cls=""):
    out=[]
    for href,label in NAV:
        if label=="Contact": continue
        cur=' aria-current="page"' if href==current else ''
        out.append('<a href="%s"%s>%s</a>'%(href,cur,label))
    return "\n        ".join(out)

def mobile_links(current):
    out=[]
    for href,label in NAV:
        cur=' aria-current="page"' if href==current else ''
        out.append('<li><a href="%s"%s>%s</a></li>'%(href,cur,label))
    return "\n      ".join(out)

def masthead(current):
    return """<header class="masthead">
  <div class="masthead__in">
    <a class="brandlink" href="index.html" aria-label="Beaumont West Solutions — home">%s</a>
    <nav class="nav" aria-label="Primary">
        %s
    </nav>
    <a class="btn btn--primary" href="contact.html">Start a project</a>
    <button class="navtoggle" type="button" aria-expanded="false" aria-controls="mobilenav" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="mobilenav" id="mobilenav">
    <ul>
      %s
    </ul>
  </div>
</header>""" % (header_lockup("hd"), nav_links(current), mobile_links(current))

FOOTER = """<footer class="foot">
  <div class="wrap">
    <div class="foot__top">
      <div>
        %s
        <p class="foot__blurb">Websites for service businesses on the coast and everywhere
        else. Designed, built, and handed over — keys included.</p>
      </div>
      <div>
        <h4>Pages</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="services.html">Services</a></li>
          <li><a href="work.html">Work</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Get in touch</h4>
        <ul>
          <li><a href="mailto:hello@beaumontwest.com">hello@beaumontwest.com</a></li>
          <li><a href="tel:+15550142200">(555) 014-2200</a></li>
          <li><a href="contact.html">Start a project</a></li>
        </ul>
      </div>
    </div>
    <div class="foot__base">
      <span>© 2026 Beaumont West Solutions</span>
      <span>Replies within one business day</span>
    </div>
  </div>
</footer>""" % footer_lockup("ft")

def page(slug, title, desc, body):
    out = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:image" content="%s/assets/bws-social-1200x630.png">
<meta name="theme-color" content="#1B4552">
<link rel="icon" href="assets/bws-favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="assets/bws-favicon-32.png">
<link rel="apple-touch-icon" href="assets/bws-logo-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
%s
<main id="main">
%s
</main>
%s
<script>%s</script>
</body>
</html>
""" % (html.escape(title), html.escape(desc), html.escape(title), html.escape(desc),
       SITE_URL, CSS, masthead(slug), body, FOOTER, JS)
    out = out.replace("Beaumont West Solutions", BRAND)
    out = out.replace("hello@beaumontwest.com", EMAIL)
    out = out.replace("(555) 014-2200", PHONE_DISPLAY)
    out = out.replace("+15550142200", PHONE_LINK)
    out = out.replace("\u00a9 2026", "\u00a9 " + YEAR)
    return out

# ==========================================================================
#  HOME
# ==========================================================================
home = """
<section class="hero">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    %s
    <span class="eyebrow">Websites for service businesses</span>
    <h1>Do great work. Be easy to find.</h1>
    <p class="lede">We design and build websites for salons, studios, landscapers, trainers and
    trades — the businesses that run on word of mouth and deserve to be found by everyone else too.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">→</span></a>
      <a class="btn btn--ghost" href="work.html">See the work</a>
    </div>
    <div class="hero__foot"></div>
  </div>
</section>

%s

<section class="section section--tight band-teal">
  <div class="wrap">
    <ul class="facts reveal">
      <li><span class="sun" aria-hidden="true"></span><span>Live in three to four weeks</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Built for phones first</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>You own the domain and the files</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Set up to show in local search</span></li>
    </ul>
  </div>
</section>

<section class="section band-teal" style="padding-top:0">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Who we build for</span>
      <h2>Three versions of the same problem</h2>
    </div>
    <div class="grid g3 reveal">
      <article class="card">
        <span class="card__tag">No site at all</span>
        <h3>You've run on referrals</h3>
        <p>A phone number and a Facebook page got you here. It works right up until
        someone searches your name at 9pm and finds nothing they can trust.</p>
      </article>
      <article class="card">
        <span class="card__tag">A site you're stuck with</span>
        <h3>Someone built it in 2016</h3>
        <p>You can't change the hours, the photos are of a truck you sold, and nobody
        remembers who has the login. Updating it costs a favour every time.</p>
      </article>
      <article class="card">
        <span class="card__tag">Outgrowing word of mouth</span>
        <h3>The admin is eating your evenings</h3>
        <p>Quotes, bookings and the same five questions, all by text, all after hours.
        A site should take the first pass at every one of them.</p>
      </article>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">What's included</span>
      <h2>Every build ships with these</h2>
      <p class="lede" style="margin-top:20px">No tiers, no upsell menu. This is the floor,
      and most projects need nothing beyond it.</p>
    </div>
    <ul class="checks reveal">
      <li><span class="sun" aria-hidden="true"></span><span>A homepage that says what you do, where you do it, and how to start</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Service pages written the way people actually search</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Click-to-call and click-to-text within thumb's reach on every screen</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>A quote or booking form that lands in your inbox and your phone</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Your Google Business Profile claimed, filled in, and pointed at the site</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Photos edited and placed — or a shot list if you'd rather take them yourself</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Pages that load fast on a bad signal in a parking lot</span></li>
    </ul>
  </div>
</section>

<section class="section band-cream">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Plain terms</span>
      <h2>What it costs, and how we talk about it</h2>
      <p class="lede" style="margin-top:20px">Every project is quoted after one short call,
      because a five-page site for a barber and a twenty-page site for a roofing company
      are not the same job. You'll have the number in writing before anything starts,
      and it won't move unless you ask for something new.</p>
    </div>
    <div class="grid g3 reveal">
      <article class="card">
        <h3>No long contracts</h3>
        <p class="small" style="margin-top:8px">The agreement covers the build. Care plans are
        month to month and you can stop them whenever.</p>
      </article>
      <article class="card">
        <h3>No rented pages</h3>
        <p class="small" style="margin-top:8px">You get the domain, the hosting account and the
        files. If you ever leave, you leave with everything.</p>
      </article>
      <article class="card">
        <h3>No mystery line items</h3>
        <p class="small" style="margin-top:8px">One number for the build, one number a month if
        you want us to keep looking after it. That's the whole invoice.</p>
      </article>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How it goes</span>
      <h2>Four steps, about a month</h2>
    </div>
    <div class="steps reveal">
      <div class="step">
        <div class="step__n">01</div>
        <div><h3>Call</h3><p>Thirty minutes. What you do, who you'd like more of, and what's
        getting in the way. You get the quote within two days.</p></div>
      </div>
      <div class="step">
        <div class="step__n">02</div>
        <div><h3>Draft</h3><p>A designed homepage inside a week, so you're reacting to something
        real instead of a description. Changes are expected, not charged for.</p></div>
      </div>
      <div class="step">
        <div class="step__n">03</div>
        <div><h3>Build</h3><p>The rest of the pages, the words, the photos, the forms and the
        search setup. You review it on a private link before anyone else sees it.</p></div>
      </div>
      <div class="step">
        <div class="step__n">04</div>
        <div><h3>Launch</h3><p>We point the domain, test it on real phones, and hand you every
        login. Then we stay reachable — most questions come in week two.</p></div>
      </div>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head head--center reveal">
      <span class="eyebrow">Recent concepts</span>
      <h2>How we'd approach three real businesses</h2>
      <p class="lede" style="margin:20px auto 0">Beaumont West is new. Rather than pad a
      portfolio, we built full concepts for the kinds of businesses we want to work with.</p>
    </div>
    <div class="grid g2 reveal">
      %s
      %s
    </div>
    <div class="btn-row" style="justify-content:center;margin-top:40px">
      <a class="btn btn--ghost" href="work.html">See all three concepts <span class="arrow">→</span></a>
    </div>
  </div>
</section>

<section class="section band-cream">
  <div class="wrap head--center reveal" style="max-width:none">
    <span class="eyebrow">Start here</span>
    <h2 style="max-width:20ch;margin-inline:auto">Tell us about the business</h2>
    <p class="lede" style="margin:20px auto 0">One call, no deck, no pressure. If we're not the
    right fit we'll say so and point you somewhere better.</p>
    <div class="btn-row" style="justify-content:center;margin-top:32px">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">→</span></a>
      <a class="btn btn--ghost" href="services.html">What we do</a>
    </div>
  </div>
</section>
"""

# ---- concept mockups ------------------------------------------------------
def mock(brand, url, eyebrow, headline, blurb, cta, bg, accent, btn_bg, btn_fg, tiles, tile_bg, tile_fg):
    ts = "".join(
        '<div class="mock__tile" style="background:%s;color:%s">%s</div>' % (tile_bg, tile_fg, t)
        for t in tiles)
    return """<div class="mock" role="img" aria-label="Concept homepage design for %s">
  <div class="mock__bar"><span class="mock__dot"></span><span class="mock__dot"></span><span class="mock__dot"></span>
    <span class="mock__url">%s</span></div>
  <div class="mock__body">
    <div class="mock__hero" style="background:%s">
      <div class="mock__eyebrow" style="color:%s">%s</div>
      <div class="mock__h">%s</div>
      <p class="mock__p">%s</p>
      <span class="mock__btn" style="background:%s;color:%s">%s</span>
    </div>
    <div class="mock__row">%s</div>
  </div>
</div>""" % (brand, url, bg, accent, eyebrow, headline, blurb, btn_bg, btn_fg, cta, ts)

MOCK_SALON = mock(
    "Tidewater Salon &amp; Spa", "tidewatersalon.com", "Salon &amp; spa · Point Reyes",
    "Book your chair in<br>under a minute.",
    "Colour, cuts and facials by appointment, seven days a week.",
    "Book now", "#2E4A45", "#C9D9CF", "#E7C9A9", "#243A36",
    ["Book online", "Meet the stylists", "Gift cards"], "#F2EDE4", "#2E4A45")

MOCK_LAND = mock(
    "Harbor &amp; Pine Landscape", "harborandpine.com", "Landscape &amp; hardscape · Sonoma County",
    "Yards that hold up<br>to real weather.",
    "Design, build and maintenance for coastal properties. Free site visit.",
    "Get a quote", "#3A4A3C", "#CFDCC6", "#D9A441", "#2B3A2D",
    ["Recent yards", "Service areas", "Request a visit"], "#F1EEE6", "#3A4A3C")

MOCK_GYM = mock(
    "Cape Line Strength", "capelinestrength.com", "Strength &amp; conditioning · Half Moon Bay",
    "Small classes.<br>Serious coaching.",
    "Six people to a session. First week is free, no card needed.",
    "Claim first week", "#33404F", "#C8D3E0", "#E07A5A", "#26313D",
    ["Class schedule", "Coaches", "Free trial"], "#EFEDE8", "#33404F")

home = home % (badge("hero"), RIDGE, WAVE, RIDGE_CREAM, WAVE, MOCK_SALON, MOCK_LAND)

# ==========================================================================
#  SERVICES
# ==========================================================================
def svc(tag, title, body, points):
    lis = "".join('<li><span class="sun" aria-hidden="true"></span><span>%s</span></li>' % p
                  for p in points)
    return """<article class="card reveal">
  <span class="card__tag">%s</span>
  <h3>%s</h3>
  <p style="margin-top:10px">%s</p>
  <ul class="checks" style="margin-top:20px">%s</ul>
</article>""" % (tag, title, body, lis)

services = """
<section class="section band-paper" style="padding-bottom:clamp(40px,5vw,60px)">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">Services</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">One thing done properly, plus the pieces that make it work.</h1>
      <p class="lede" style="margin-top:22px">The website is the job. Everything else on this page
      exists because a website on its own doesn't get found, doesn't get answered, and doesn't stay
      current. Take all of it or take the first one.</p>
    </div>
  </div>
</section>

<section class="section band-paper" style="padding-top:0">
  <div class="wrap grid g2">
    %s
    %s
    %s
    %s
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Care plan</span>
      <h2>After launch, if you want it</h2>
    </div>
    <div class="reveal">
      <p class="lede">A site goes stale quietly. The care plan covers hosting, backups, security
      updates and a monthly window for small changes — new photos, changed hours, a service you've
      added, a seasonal promotion. It's month to month, and plenty of clients don't take it.
      Nothing about the site depends on it.</p>
      <ul class="checks" style="margin-top:26px">
        <li><span class="sun" aria-hidden="true"></span><span>Hosting, SSL, daily backups</span></li>
        <li><span class="sun" aria-hidden="true"></span><span>Small edits each month, sent by text or email</span></li>
        <li><span class="sun" aria-hidden="true"></span><span>A short report on what people searched to reach you</span></li>
        <li><span class="sun" aria-hidden="true"></span><span>Cancel whenever; the site and files stay yours</span></li>
      </ul>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Later</span>
      <h2>Things we'll build once the site is earning</h2>
      <p class="lede" style="margin-top:20px">Beaumont West is a web design studio first.
      These come next, and only for businesses where they'd actually pay off.</p>
    </div>
    <div class="grid g3 reveal">
      <article class="card"><h3>Email lists</h3><p class="small" style="margin-top:8px">Seasonal
      notes to past customers. The cheapest repeat business there is.</p></article>
      <article class="card"><h3>Review generation</h3><p class="small" style="margin-top:8px">A
      polite, automatic ask after every finished job, pointed at Google.</p></article>
      <article class="card"><h3>Paid search</h3><p class="small" style="margin-top:8px">For the
      handful of searches worth paying for, once the free ones are working.</p></article>
    </div>
  </div>
</section>

<section class="section band-cream">
  <div class="wrap">
    <div class="head reveal" style="max-width:52ch">
      <span class="eyebrow">Common questions</span>
      <h2>Before you call</h2>
    </div>
    <div class="faq reveal">
      <details>
        <summary>What does a site cost?</summary>
        <p>It depends on how many pages you need, whether we're writing the words, and whether
        booking or payments are involved. We quote after one call, in writing, and the number
        doesn't move unless the job does. If you want a range before you call, say so in the form
        and we'll send one.</p>
      </details>
      <details>
        <summary>How long does it take?</summary>
        <p>Three to four weeks from the call for most projects. The part that slows it down is
        almost always photos and content from your side — we'll tell you exactly what we need on
        day one so it doesn't sit.</p>
      </details>
      <details>
        <summary>I don't have any good photos.</summary>
        <p>Common, and fixable. We'll either direct a shoot, work with what's on your phone, or
        build the design around type and colour so it doesn't lean on photography. What we won't do
        is fill your site with stock images of someone else's business.</p>
      </details>
      <details>
        <summary>Can I update it myself?</summary>
        <p>Yes. We hand over a site you can edit — hours, prices, photos, new services — and we walk
        you through it on a recorded call you can keep. If you'd rather never touch it, that's what
        the care plan is for.</p>
      </details>
      <details>
        <summary>Do you work outside the coast?</summary>
        <p>Yes. Most of the work happens over calls and shared links regardless of where you are.
        Local businesses get an in-person kickoff if they want one.</p>
      </details>
      <details>
        <summary>What if I already have a site?</summary>
        <p>Then the first question is whether it needs rebuilding or just fixing. Sometimes the
        honest answer is that a day of cleanup beats a new site, and we'll tell you that even
        though it's the smaller invoice.</p>
      </details>
    </div>
  </div>
</section>

<section class="section band-cream" style="padding-top:0">
  <div class="wrap head--center reveal">
    <h2 style="max-width:22ch;margin-inline:auto">Not sure which of these you need?</h2>
    <p class="lede" style="margin:20px auto 0">That's the call. Bring the business, we'll bring
    the recommendation.</p>
    <div class="btn-row" style="justify-content:center;margin-top:30px">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">→</span></a>
    </div>
  </div>
</section>
""" % (
  svc("The core", "Website design &amp; build",
      "A complete site, designed for your business rather than dropped into a template, and built "
      "to load fast on a phone in a parking lot.",
      ["Homepage, services, about, contact, and anything else the business needs",
       "Written from a call with you, not filled with filler",
       "Mobile-first, tested on real devices",
       "Accessible contrast, real text, keyboard navigation",
       "Domain, hosting and email set up and handed over"]),
  svc("Getting found", "Local search &amp; Google Business Profile",
      "Most service businesses are chosen from a map, not a search page. That listing gets the same "
      "attention as the site.",
      ["Google Business Profile claimed, filled in and verified",
       "Service-area pages for the towns you actually cover",
       "Consistent name, address and phone everywhere it appears",
       "A simple, non-annoying way to ask for reviews"]),
  svc("Getting answered", "Booking &amp; lead capture",
      "The point of the site is the next conversation. We make that the easiest thing on the page.",
      ["Quote or booking forms that reach your inbox and your phone",
       "Scheduling connected to the calendar you already use",
       "Click-to-call and click-to-text on every screen",
       "Deposits or payments taken online where it makes sense"]),
  svc("Words &amp; pictures", "Copy and photo direction",
      "The reason most small-business sites read the same is that nobody asked the owner anything. "
      "We start with the call and write from it.",
      ["Copy drafted from a recorded conversation, in your voice",
       "A shot list if you're taking photos yourself",
       "Editing and cropping for what you already have",
       "Direction for a photographer if you'd rather hire one"]),
  RIDGE, WAVE)

# ==========================================================================
#  WORK
# ==========================================================================
def concept(mockup, tag, name, problem, moves, band="paper"):
    lis = "".join('<li><span class="sun" aria-hidden="true"></span><span>%s</span></li>' % m
                  for m in moves)
    return """<section class="section band-%s">
  <div class="wrap split reveal">
    <div>
      <span class="eyebrow">%s</span>
      <h2 style="font-size:clamp(26px,3.2vw,36px)">%s</h2>
      <p style="margin-top:18px;color:var(--teal-mid)">%s</p>
      <ul class="checks" style="margin-top:22px">%s</ul>
    </div>
    <div>%s</div>
  </div>
</section>""" % (band, tag, name, problem, lis, mockup)

work = """
<section class="section band-paper" style="padding-bottom:clamp(36px,4vw,52px)">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">Work</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Three concepts, built the way we'd build yours.</h1>
      <p class="lede" style="margin-top:22px">Beaumont West is new, so this isn't a client list.
      These are complete concepts for three businesses we'd like to work with — the same thinking,
      the same research, the same standard of finish, minus the invoice. Names and details are
      invented.</p>
    </div>
  </div>
</section>

%s
%s
%s

%s

<section class="section band-teal">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">The pattern</span>
      <h2>Same three questions, every time</h2>
    </div>
    <div class="reveal">
      <p class="lede">Every concept above answers the same short list before a single colour gets
      picked. What does this business want a visitor to do in the first ten seconds? What's the one
      objection stopping them? And what does this business have that the competitor down the road
      doesn't? Design is how those answers get built — not decoration laid on afterwards.</p>
      <div class="btn-row" style="margin-top:30px">
        <a class="btn btn--primary" href="contact.html">Talk about yours <span class="arrow">→</span></a>
        <a class="btn btn--ghost" href="services.html">What's included</a>
      </div>
    </div>
  </div>
</section>
""" % (
  concept(MOCK_SALON, "Concept · Salon &amp; spa", "Tidewater Salon &amp; Spa",
    "A busy salon losing evenings to booking texts, with a Facebook page as its only home online. "
    "The whole design leads to one button.",
    ["Booking above the fold on every screen, in every colour scheme we tried",
     "Stylist pages, because people book a person and not a salon",
     "Prices published — it removes the most common first text",
     "Gift cards given their own page for the two months a year they matter"]),
  concept(MOCK_LAND, "Concept · Landscape &amp; hardscape", "Harbor &amp; Pine Landscape",
    "A contractor whose work is genuinely excellent and completely invisible. The job of the site "
    "is proof, then a quote request.",
    ["Finished yards shown large, seasons labelled, no stock photography",
     "Service-area pages for each town, so the map listing has somewhere to point",
     "A quote form that asks four questions instead of fourteen",
     "Straight talk about lead times, which filters out the wrong callers"], band="cream"),
  concept(MOCK_GYM, "Concept · Strength &amp; conditioning", "Cape Line Strength",
    "A small gym competing with a chain two blocks away. It wins on coaching, so the site sells the "
    "coaches and the first free week.",
    ["Class schedule as the second thing you see, always current",
     "Coach bios with real credentials, not motivational copy",
     "Free trial claimable in two taps with no card",
     "Membership terms in plain language, on the page, before anyone asks"]),
  RIDGE)

# ==========================================================================
#  ABOUT
# ==========================================================================
about = """
<section class="section band-paper" style="padding-bottom:clamp(40px,5vw,64px)">
  <div class="wrap">
    <div class="head head--center" style="margin-inline:auto">
      %s
      <span class="eyebrow">About</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px);max-width:18ch;margin-inline:auto">A small studio with a narrow specialty.</h1>
      <p class="lede" style="margin:22px auto 0">Beaumont West Solutions designs and builds websites
      for service businesses — the ones people find by asking a neighbour, and should be able to find
      by opening their phone.</p>
    </div>
  </div>
</section>

<section class="section band-cream" style="padding-block:clamp(48px,6vw,80px)">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">The name</span>
      <h2>Beaumont means beautiful mountain.</h2>
    </div>
    <div class="reveal">
      <p class="lede">West is where the water is. That's the whole idea, and it's in the mark: a
      ridge line, a setting sun, and a horizon. The businesses we build for tend to live in that
      same landscape — the ones that work outdoors, or on people, or on houses, in towns where the
      mountains meet the coast.</p>
      <p class="lede" style="margin-top:18px">It also describes the work. Something solid, made to
      last, with a bit of warmth in it.</p>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How we work</span>
      <h2>Three commitments</h2>
    </div>
    <div class="grid g3 reveal">
      <article class="card">
        <h3>Plain language, always</h3>
        <p style="margin-top:10px">No jargon in the proposal, no jargon on the call, and none on
        your site either. If a sentence needs explaining, it gets rewritten. You should be able to
        repeat back exactly what you're buying.</p>
      </article>
      <article class="card">
        <h3>You own everything</h3>
        <p style="margin-top:10px">The domain is registered in your name. The hosting account is
        yours. The files are yours. Nothing is held hostage, and leaving is never a negotiation —
        it's a password handover.</p>
      </article>
      <article class="card">
        <h3>Finish, then improve</h3>
        <p style="margin-top:10px">A live site earning calls beats a perfect one still in review.
        We ship a complete, careful first version on schedule, then improve it with what real
        visitors actually do.</p>
      </article>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Who you'll work with</span>
      <h2>Small on purpose</h2>
    </div>
    <div class="reveal">
      <p class="lede">You'll deal with the person doing the work, start to finish. No account
      manager relaying messages, no handoff to a team you've never met, no ticket number. That's
      the advantage of a studio this size, and it's why we take a limited number of builds at once.</p>
      <p class="lede" style="margin-top:18px">It also means we sometimes say no. If a project needs
      a twenty-person agency, or if what you actually need is a better booking system rather than a
      new website, you'll hear that on the first call.</p>
      <div class="btn-row" style="margin-top:30px">
        <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">→</span></a>
        <a class="btn btn--ghost" href="work.html">See the concepts</a>
      </div>
    </div>
  </div>
</section>
""" % (badge("ab", "badge"), RIDGE_CREAM, WAVE)

# ==========================================================================
#  CONTACT
# ==========================================================================
contact = """
<section class="section band-paper" style="padding-bottom:clamp(36px,4vw,56px)">
  <div class="wrap">
    <div class="head">
      <span class="eyebrow">Contact</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Tell us about the business.</h1>
      <p class="lede" style="margin-top:22px">Fill this in and you'll hear back within one business
      day, from a person, with either a question or a time to talk. If you'd rather just call, the
      number's below.</p>
    </div>
  </div>
</section>

<section class="section band-paper" style="padding-top:0">
  <div class="wrap split">
    <div class="reveal">
      <div class="formstatus" id="formstatus" role="status">
        <h3>Form isn't connected yet</h3>
        <p class="small" style="margin-top:10px">Your details look complete, but this demo site has
        no form handler wired up. Point the form's <code>action</code> at a service like Formspree,
        Netlify Forms or your own endpoint before launch — the note under the button explains where.</p>
      </div>
      <form class="form" id="projectform" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
        <div class="field--pair">
          <div class="field">
            <label for="name">Your name</label>
            <input id="name" name="name" type="text" autocomplete="name" required>
          </div>
          <div class="field">
            <label for="business">Business name</label>
            <input id="business" name="business" type="text" autocomplete="organization" required>
          </div>
        </div>
        <div class="field--pair">
          <div class="field">
            <label for="email">Email</label>
            <input id="email" name="email" type="email" autocomplete="email" required>
          </div>
          <div class="field">
            <label for="phone">Phone</label>
            <input id="phone" name="phone" type="tel" autocomplete="tel">
          </div>
        </div>
        <div class="field">
          <label for="kind">What kind of business is it?</label>
          <select id="kind" name="kind" required>
            <option value="">Choose one</option>
            <option>Salon, spa or personal care</option>
            <option>Gym, studio or coaching</option>
            <option>Landscaping, outdoor or property</option>
            <option>Trades and home services</option>
            <option>Food, drink or hospitality</option>
            <option>Professional services</option>
            <option>Something else</option>
          </select>
        </div>
        <div class="field">
          <label for="current">Do you have a website now?</label>
          <select id="current" name="current" required>
            <option value="">Choose one</option>
            <option>No website at all</option>
            <option>Only a social media page</option>
            <option>An old site that needs replacing</option>
            <option>A site that mostly works but needs help</option>
          </select>
        </div>
        <div class="field">
          <label for="notes">What do you need?</label>
          <textarea id="notes" name="notes" placeholder="What you do, where you work, and what's not working right now. A few sentences is plenty." required></textarea>
        </div>
        <div class="field">
          <label for="when">When would you like it live?</label>
          <select id="when" name="when">
            <option value="">No particular deadline</option>
            <option>As soon as possible</option>
            <option>Within a month or two</option>
            <option>Before a specific season or event</option>
          </select>
        </div>
        <div class="btn-row" style="margin-top:6px">
          <button class="btn btn--primary" type="submit">Send it over <span class="arrow">→</span></button>
        </div>
        <p class="formnote">We'll only use this to reply to you. No list, no newsletter, no sharing.</p>
      </form>
    </div>

    <div class="reveal">
      <div class="rail">
        <div class="rail__item">
          <h3>Email</h3>
          <p class="small" style="margin-bottom:8px">Best for details, photos and existing site links.</p>
          <a href="mailto:hello@beaumontwest.com">hello@beaumontwest.com</a>
        </div>
        <div class="rail__item">
          <h3>Phone</h3>
          <p class="small" style="margin-bottom:8px">Weekdays, 8am to 6pm Pacific. Text is fine.</p>
          <a href="tel:+15550142200">(555) 014-2200</a>
        </div>
        <div class="rail__item">
          <h3>Where we work</h3>
          <p class="small">Based on the Northern California coast, working with service businesses
          anywhere in the United States. Local projects get an in-person kickoff.</p>
        </div>
        <div class="rail__item">
          <h3>What happens next</h3>
          <p class="small">A reply within one business day, then a thirty-minute call. You get a
          written quote within two days of that call. Nothing is charged until you say yes.</p>
        </div>
      </div>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap head--center reveal" style="max-width:none">
    <span class="eyebrow">Not ready yet?</span>
    <h2 style="max-width:24ch;margin-inline:auto">Have a look at how we'd build it first.</h2>
    <div class="btn-row" style="justify-content:center;margin-top:30px">
      <a class="btn btn--primary" href="work.html">See the concepts <span class="arrow">→</span></a>
      <a class="btn btn--ghost" href="services.html">Read the services</a>
    </div>
  </div>
</section>
""" % RIDGE

# ==========================================================================
PAGES = [
 ("index.html","Beaumont West Solutions — Websites for service businesses",
  "We design and build websites for salons, studios, landscapers, trainers and trades. Live in three to four weeks, built for phones, and yours to keep.", home),
 ("services.html","Services — Beaumont West Solutions",
  "Website design and build, local search and Google Business Profile, booking and lead capture, copy and photo direction, and an optional monthly care plan.", services),
 ("work.html","Work — Beaumont West Solutions",
  "Three complete website concepts for a salon and spa, a landscape contractor, and a strength gym — built the way we'd build yours.", work),
 ("about.html","About — Beaumont West Solutions",
  "A small studio with a narrow specialty: websites for service businesses. Plain language, full ownership, and a finished site on schedule.", about),
 ("contact.html","Contact — Beaumont West Solutions",
  "Tell us about your business. A reply within one business day, a thirty-minute call, and a written quote two days after that.", contact),
]

os.makedirs(OUT, exist_ok=True)
adir = os.path.join(OUT, "assets")
if os.path.abspath(SRC) != os.path.abspath(adir):
    os.makedirs(adir, exist_ok=True)
    for f in os.listdir(SRC):
        shutil.copy(os.path.join(SRC, f), os.path.join(adir, f))

for slug, title, desc, body in PAGES:
    with open(os.path.join(OUT, slug), "w") as fh:
        fh.write(page(slug, title, desc, body))
    print("wrote", slug, os.path.getsize(os.path.join(OUT, slug)), "bytes")
print("assets:", len(os.listdir(adir)))
