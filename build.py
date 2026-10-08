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
LOCKUP_P   = read("bws-lockup-primary.svg")
LOCKUP_REV = read("bws-lockup-primary-reversed.svg")
BADGE_FULL = read("bws-logo-primary.svg")

def stacked_lockup(idpfx):
    """Two-line lockup for narrow screens. Same simplified badge as the wide
    header; cropped to an even 8-unit margin (artwork spans x14-396, y14-114)."""
    svg = LOCKUP_P
    for p in re.findall(r'<path d="[^"]+" fill="#FDF0DC"/>', svg):
        svg = svg.replace(p, '')
    return ('<svg class="lockup lockup--header lockup--stacked" viewBox="6 6 398 116" '
            'role="img" aria-label="Beaumont West Solutions">%s</svg>'
            % strip_shell(svg, idpfx))


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
    # crop the file's own padding (artwork spans 14..94 of 108) to an even
    # 8-unit margin, so the logo reads larger at the same header height
    return ('<svg class="lockup lockup--header lockup--wide" viewBox="6 6 478 96" role="img" '
            'aria-label="Beaumont West Solutions">%s</svg>'
            % strip_shell(svg, idpfx))

def footer_lockup(idpfx):
    # the badge's own ring is #1B4552, which disappears against a teal footer,
    # so a coral ring is added just outside it to hold the mark off the ground
    ring = ('<circle cx="100" cy="100" r="92" fill="none" stroke="#E86F51" '
            'stroke-width="6"/>')
    global LOCKUP_REV
    anchor = '<circle cx="100" cy="100" r="88" fill="none" stroke="#1B4552" stroke-width="5"/>'
    if anchor in LOCKUP_REV and 'E86F51" stroke-width="6"' not in LOCKUP_REV:
        LOCKUP_REV = LOCKUP_REV.replace(anchor, anchor + ring)
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
    """Teal above, light below: a three-layer tide, matching the ridge's depth."""
    return """<div class="divider divider--wave to-%s" aria-hidden="true">
<svg viewBox="0 0 1440 100" preserveAspectRatio="none" focusable="false">
<path class="tide-far" d="M0,0 L1440,0 L1440,66 C1186,88 995,60 720,74 C445,88 254,64 0,80 Z"/>
<path class="tide-mid" d="M0,0 L1440,0 L1440,52 C1228,70 1016,44 762,58 C508,72 275,48 0,62 Z"/>
<path class="tide-front" d="M0,0 L1440,0 L1440,36 C1249,54 995,26 720,42 C445,58 233,32 0,46 Z"/>
</svg></div>""" % to

RIDGE_CREAM = RIDGE.replace('divider--ridge"', 'divider--ridge from-cream"')
SUN_ARC = """<div class="divider divider--arc" aria-hidden="true">
<svg viewBox="0 0 1440 110" preserveAspectRatio="none" focusable="false">
<path class="arc-fill" d="M0,110 L0,66 Q720,2 1440,66 L1440,110 Z"/>
<path class="arc-line" d="M0,66 Q720,2 1440,66"/>
</svg></div>"""

SUN_ARC_INVERSE = SUN_ARC.replace('divider--arc"', 'divider--arc arc--inverse"')

ANGLE = """<div class="divider divider--angle" aria-hidden="true">
<svg viewBox="0 0 1440 110" preserveAspectRatio="none" focusable="false">
<path class="angle-fill" d="M0,110 L0,88 L1440,26 L1440,110 Z"/>
</svg></div>"""

RIDGE_SAND = RIDGE.replace('divider--ridge"', 'divider--ridge from-sand"')
SUN_ARC_TEAL = SUN_ARC.replace('divider--arc"', 'divider--arc arc--teal"')
SUN_HORIZON = """<div class="horizon sunrise" aria-hidden="true">
<svg viewBox="0 0 120 90" focusable="false">
<defs><clipPath id="bws-sky"><rect x="0" y="0" width="120" height="45"/></clipPath></defs>
<g clip-path="url(#bws-sky)"><g class="sun-up">
<circle cx="60" cy="45" r="40" fill="#E86F51" opacity=".13"/>
<circle cx="60" cy="45" r="29" fill="#E86F51" opacity=".14"/>
<circle cx="60" cy="45" r="18" fill="#E86F51"/>
</g></g>
<g class="sun-refl" stroke="#E86F51" stroke-width="2.6" stroke-linecap="round">
<line x1="37" y1="53" x2="83" y2="53" opacity=".55"/>
<line x1="44" y1="61" x2="76" y2="61" opacity=".42"/>
<line x1="51" y1="69" x2="69" y2="69" opacity=".3"/>
<line x1="57" y1="77" x2="63" y2="77" opacity=".2"/>
</g>
</svg></div>"""

MOUNTAIN_HORIZON = """<div class="horizon horizon--close" aria-hidden="true">
<svg viewBox="0 0 120 90" focusable="false">
<path d="M21,45 L39,20 L50,37 L60,27 L70,37 L81,20 L99,45 Z" fill="#1B4552"/>
</svg></div>"""

PLAIN_HORIZON = """<div class="horizon horizon--plain" aria-hidden="true"></div>"""

WAVE = wave("paper")
WAVE_CREAM = wave("cream")

# ----------------------------------------------------------------------- CSS
CSS = r"""
:root{
  --teal:#1B4552; --teal-mid:#38606E; --teal-deep:#143641;
  --cream:#FDF0DC; --paper:#FBF6EC; --coral:#E86F51; --peach:#F4A261;
  --rule:#C9D3D6; --sand:#D4D1C3; --teal-sub:#33586A;
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
.section{padding-block:clamp(52px,6.5vw,88px)}
/* 1. a scenic divider already separates sections, so the padding beside it halves */
.divider + .section,.horizon + .section{padding-top:clamp(34px,4vw,56px)}
.section:has(+ .divider),.section:has(+ .horizon){padding-bottom:clamp(34px,4vw,56px)}
.section--tight{padding-block:clamp(48px,6vw,76px)}
.band-paper{background:var(--paper)}
.band-cream{background:var(--cream)}
.band-paper + .band-paper{border-top:1px solid var(--rule)}
.band-tint{background:linear-gradient(180deg,var(--sand) 0,var(--paper) 100%)}
.band-tint .card{border-color:rgba(27,69,82,.32)}
.band-tint .eyebrow,.band-tint .lede{color:var(--teal)}
.band-teal{background:var(--teal);color:var(--cream)}
.band-teal .eyebrow{color:rgba(253,240,220,.7)}
.band-teal .lede,.band-teal .small{color:rgba(253,240,220,.82)}
.head{max-width:62ch;margin-bottom:clamp(28px,3.2vw,40px)}
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
  gap:24px;width:var(--shell);margin-inline:auto;padding-block:9px}
.lockup{display:block;height:auto}
.lockup--header{height:56px;width:auto}
.lockup--stacked{display:none}
@media(max-width:899px){
  .lockup--wide{display:none}
  .lockup--stacked{display:block;height:66px}
  .masthead__in{padding-block:8px}
}
@media(max-width:400px){.lockup--stacked{height:56px}}
.brandlink{display:inline-flex;text-decoration:none;border-radius:6px}
.nav{display:none;align-items:center;gap:30px}
.nav a{
  font-family:var(--display);font-weight:500;font-size:17px;text-decoration:none;
  padding:6px 0;position:relative;letter-spacing:.005em;
}
.nav a::after{
  content:"";position:absolute;left:0;right:0;bottom:0;height:2px;
  background:var(--teal);transform:scaleX(0);transform-origin:left;
  transition:transform .2s ease;
}
.nav a:hover::after{transform:scaleX(1)}
.nav a[aria-current="page"]::after{transform:scaleX(1);background:var(--coral)}
.masthead .btn{padding:13px 24px;font-size:13px;display:none}
@media(min-width:900px){.masthead .btn{display:inline-flex}}
.navtoggle{
  display:inline-flex;align-items:center;justify-content:center;flex:none;
  width:46px;height:46px;padding:0;background:none;border:1px solid var(--rule);
  border-radius:10px;cursor:pointer;color:var(--teal);
  -webkit-appearance:none;appearance:none;
}
.navtoggle__icon{display:block;width:24px;height:24px}
.navtoggle__icon path{fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;
  transform-box:fill-box;transform-origin:center;transition:transform .2s ease,opacity .2s ease}
.navtoggle[aria-expanded="true"] .nt1{transform:translateY(5px) rotate(45deg)}
.navtoggle[aria-expanded="true"] .nt2{opacity:0}
.navtoggle[aria-expanded="true"] .nt3{transform:translateY(-5px) rotate(-45deg)}
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
  padding-block:clamp(40px,5vw,66px) 0;text-align:center}
.hero__glow{
  position:absolute;left:50%;top:-110px;width:min(760px,120%);aspect-ratio:1;
  transform:translateX(-50%);border-radius:50%;pointer-events:none;
  background:radial-gradient(circle,rgba(232,111,81,.32) 0%,rgba(232,111,81,.13) 44%,rgba(232,111,81,0) 70%);
}
.hero__in{position:relative;width:var(--shell);margin-inline:auto}
.badge{width:104px;height:104px;display:block;margin:0 auto 26px}
.hero h1{max-width:16ch;margin-inline:auto}
.hero .lede{margin:22px auto 0;text-align:center}
.hero .btn-row{justify-content:center;margin-top:34px}
.hero__foot{margin-top:clamp(28px,3vw,40px);padding-bottom:6px}
.hero__in{z-index:2}
.hero--lite{text-align:left;padding-block:clamp(40px,4.5vw,60px) clamp(26px,3vw,38px)}
.hero--lite h1{max-width:20ch;margin-inline:0}
.hero--lite .lede{margin:20px 0 0;text-align:left}
.hero--lite::after{content:"";position:absolute;left:0;right:0;bottom:0;height:45%;
  pointer-events:none;background:linear-gradient(to bottom,rgba(251,246,236,0),var(--paper))}

/* ---------- dividers ---------- */
.divider{line-height:0}
.divider svg{display:block;width:100%}
.divider--ridge{background:var(--paper)}
.divider--ridge svg{height:clamp(84px,10vw,132px)}
.divider--ridge,.divider--wave{position:relative}
.divider--ridge::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;background:var(--teal)}
.divider--wave::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--teal)}
.ridge-far{fill:var(--teal-mid);opacity:.45}
.ridge-back{fill:var(--teal-mid)}
.ridge-front{fill:var(--teal)}
.divider--arc{background:var(--paper)}
.divider--arc.arc--inverse .arc-fill{fill:var(--paper)}
.divider--arc.arc--teal .arc-fill{fill:var(--teal)}
.divider--arc.arc--teal .arc-line{display:none}
.band-tint--inverse{background:linear-gradient(180deg,var(--paper) 0,var(--sand) 180px)}
.divider--arc svg{height:clamp(58px,6.5vw,96px)}
.arc-fill{fill:var(--sand)}
.arc-line{fill:none;stroke:var(--coral);stroke-width:3;vector-effect:non-scaling-stroke}
.divider--angle{background:var(--sand)}
.divider--angle svg{height:clamp(38px,4vw,62px)}
.angle-fill{fill:var(--paper)}
.divider--wave{background:var(--paper)}
.divider--wave.to-cream{background:var(--cream)}
.divider--wave svg{height:clamp(66px,7.5vw,112px)}
.tide-far{fill:var(--teal-mid);opacity:.35}
.tide-mid{fill:var(--teal-mid)}
.tide-front{fill:var(--teal)}
.divider--ridge.from-cream{background:var(--cream)}
.divider--ridge.from-sand{background:var(--sand)}

/* ---------- cards ---------- */
.card{
  background:var(--cream);border:1px solid rgba(27,69,82,.13);border-radius:var(--r);
  padding:clamp(24px,3vw,32px);
}
.band-teal .card{background:var(--cream);border-color:transparent;color:var(--teal)}
.band-teal .card .small{color:var(--teal-mid)}
.card h3{margin-bottom:10px}
.card--dark{background:var(--teal);border-color:transparent;color:var(--cream)}
.card.card--dark h3{color:var(--cream)}
.card.card--dark p{color:rgba(253,240,220,.88)}
.card.card--dark .eyebrow{color:rgba(253,240,220,.7)}
.careplan{padding:clamp(30px,4.6vw,58px)}
.careplan .lede{font-size:clamp(19px,2.1vw,22px);line-height:1.55}
.careplan .small{font-size:15.5px}
.band-cream--framed{position:relative}
.horizon{position:relative;height:clamp(76px,8vw,96px);
  background:linear-gradient(to bottom,var(--paper) 50%,var(--cream) 50%)}
.horizon::before{content:"";position:absolute;left:0;right:0;top:50%;height:1.3px;
  transform:translateY(-50%);background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 calc(50% - 22px),transparent calc(50% - 22px),
  transparent calc(50% + 22px),#9FB0B5 calc(50% + 22px),#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon--close{background:linear-gradient(to bottom,var(--cream) 50%,var(--paper) 50%)}
.horizon--close::before{background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 calc(50% - 44px),transparent calc(50% - 44px),
  transparent calc(50% + 44px),#9FB0B5 calc(50% + 44px),#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon--plain::before{background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon svg{position:absolute;left:50%;top:50%;width:120px;height:90px;transform:translate(-50%,-50%)}
.horizon{--rise:1}
.sunrise .sun-up{transform:translateY(calc((1 - var(--rise)) * 42px));
  opacity:calc(.25 + var(--rise) * .75)}
.sunrise .sun-refl{opacity:clamp(0,calc((var(--rise) - .45) / .55),1)}
.card p{font-size:16.5px;line-height:1.6;color:var(--teal-mid)}
.band-teal .card p{color:var(--teal-mid)}
.srow{display:grid;gap:clamp(22px,3.5vw,54px);grid-template-columns:1fr;
  padding-block:clamp(30px,4vw,46px);border-top:1px solid rgba(27,69,82,.18)}
.srow:first-child{border-top:none;padding-top:0}
.band-teal .srow{border-top-color:rgba(253,240,220,.22)}
.band-teal .srow p,.band-teal .srow__tag{color:rgba(253,240,220,.78)}
.srow:last-child{padding-bottom:0}
.srow h3{font-size:clamp(23px,2.7vw,30px);margin-bottom:12px}
.srow p{font-size:17.5px;line-height:1.55;color:var(--teal-sub);margin:0}
.srow__tag{font-family:var(--display);font-size:11.5px;font-weight:600;letter-spacing:.17em;
  text-transform:uppercase;color:var(--teal-sub);display:block;margin-bottom:12px}
@media(min-width:860px){
  .srow{grid-template-columns:0.92fr 1.08fr;align-items:start}
  .srow:nth-child(even) .srow__intro{order:2}
  .srow:nth-child(even) .checks{order:1}
}
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
.facts .sun{margin-top:calc((1.45em - 9px) / 2 + 1px)}

/* ---------- steps ---------- */
.track{display:grid;grid-template-columns:repeat(5,1fr);margin-top:10px}
.track__step{text-align:center;padding:0 12px}
.track__n{display:block;font-family:var(--display);font-weight:600;font-size:12.5px;
  letter-spacing:.16em;color:var(--teal-mid);margin-bottom:14px}
.track__marker{position:relative;display:block;height:18px;margin-bottom:18px}
.track__marker::before{content:"";position:absolute;left:-12px;right:-12px;top:50%;
  height:2px;background:var(--rule);transform:translateY(-50%)}
.track__step:first-child .track__marker::before{left:50%}
.track__step:last-child .track__marker::before{right:50%}
.track__dot{position:absolute;left:50%;top:50%;width:16px;height:16px;border-radius:50%;
  background:var(--teal);transform:translate(-50%,-50%)}
.track__step:last-child .track__dot{background:var(--coral)}
.track h3{margin-bottom:9px}
.track p{font-size:15.5px;line-height:1.5;color:var(--teal-mid);margin:0}
@media(max-width:899px){
  .track{grid-template-columns:repeat(2,1fr);gap:34px 26px}
  .track__marker::before{display:none}
}
@media(max-width:559px){
  .track{grid-template-columns:1fr;gap:28px}
  .track__step{text-align:left;padding:0}
  .track__dot{left:8px;transform:translate(0,-50%)}
  .track__marker{height:14px;margin-bottom:12px}
}
.steps{display:grid;gap:2px;margin-top:8px;border-top:1px solid rgba(253,240,220,.22)}
.band-paper .steps{border-top-color:var(--rule)}
.band-paper .step{border-bottom-color:var(--rule)}
.band-paper .step__n{color:var(--teal-mid)}
.band-paper .step p{color:var(--teal-mid)}
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
.band-teal .faq,.band-teal .faq details{border-color:rgba(253,240,220,.24)}
.band-teal .faq summary::after{border-right-color:var(--cream);border-bottom-color:var(--cream)}
.band-teal .faq p{color:rgba(253,240,220,.82)}
.stepnum{display:inline-block;min-width:44px;font-size:13px;letter-spacing:.15em;
  font-weight:500;color:var(--teal-mid)}
.band-teal .stepnum{color:rgba(253,240,220,.55)}
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
  var hz=document.querySelector('.sunrise');
  if(hz){
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      hz.style.setProperty('--rise','1');
    }else{
      var ticking=false;
      var upd=function(){
        ticking=false;
        var r=hz.getBoundingClientRect();
        var vh=window.innerHeight||document.documentElement.clientHeight;
        var p=Math.max(0,Math.min(1,(vh-r.top)/(vh*0.55)));
        p=p*p*(3-2*p);
        hz.style.setProperty('--rise',p.toFixed(3));
      };
      var onScroll=function(){if(!ticking){ticking=true;requestAnimationFrame(upd);}};
      window.addEventListener('scroll',onScroll,{passive:true});
      window.addEventListener('resize',onScroll);
      upd();
    }
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
NAV = [("index.html","Home"),("services.html","Services"),("contact.html","Contact")]

def nav_links(current, cls=""):
    out=[]
    for href,label in NAV:
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
    <a class="brandlink" href="index.html" aria-label="Beaumont West Solutions — home">%s%s</a>
    <nav class="nav" aria-label="Primary">
        %s
    </nav>
    <a class="btn btn--primary" href="contact.html">Start a project</a>
    <button class="navtoggle" type="button" aria-expanded="false" aria-controls="mobilenav" aria-label="Menu">
      <svg class="navtoggle__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="nt1" d="M4 7h16"/><path class="nt2" d="M4 12h16"/><path class="nt3" d="M4 17h16"/></svg>
    </button>
  </div>
  <div class="mobilenav" id="mobilenav">
    <ul>
      %s
    </ul>
  </div>
</header>""" % (header_lockup("hd"), stacked_lockup("hs"), nav_links(current), mobile_links(current))

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
    <p class="lede">Sites for salons, studios, landscapers, trainers and trades.
    Live in three to four weeks, and yours to keep.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
      <a class="btn btn--ghost" href="services.html">What we do</a>
    </div>
    <div class="hero__foot"></div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <ul class="facts reveal">
      <li><span class="sun" aria-hidden="true"></span><span>Live in three to four weeks</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Built for phones first</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Hosted by us, or by you</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Set up to show in local search</span></li>
    </ul>
  </div>
  <div class="wrap" style="margin-top:clamp(40px,4.8vw,64px)">
    <div class="head reveal">
      <span class="eyebrow">Who we build for</span>
      <h2>Three versions of the same problem</h2>
    </div>
    <div class="grid g3 reveal">
      <article class="card">
        <span class="card__tag">No site at all</span>
        <h3>Running on referrals</h3>
        <p>Which works right up until someone searches your name at 9pm and finds nothing.</p>
      </article>
      <article class="card">
        <span class="card__tag">A site you're stuck with</span>
        <h3>Built in 2016</h3>
        <p>You can't change the hours, and nobody remembers who has the login.</p>
      </article>
      <article class="card">
        <span class="card__tag">Outgrowing word of mouth</span>
        <h3>Admin after hours</h3>
        <p>Quotes and bookings by text, every evening. The site should take the first pass.</p>
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
      <p class="lede" style="margin-top:18px">No tiers and no upsell menu. This is the floor.</p>
    </div>
    <ul class="checks reveal">
      <li><span class="sun" aria-hidden="true"></span><span>A homepage that says what you do, where, and how to start</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Service pages written the way people actually search</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Click-to-call and click-to-text on every screen</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>A quote or booking form that reaches your inbox</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Your Google Business Profile claimed and connected</span></li>
      <li><span class="sun" aria-hidden="true"></span><span>Pages that load fast on a weak signal</span></li>
    </ul>
  </div>
</section>

%s

<section class="section band-cream band-cream--framed" style="padding-block:clamp(32px,3.8vw,52px)">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Plain terms</span>
      <h2>What it costs</h2>
      <p class="lede" style="margin-top:18px">Every project is quoted after one short call. You'll
      have the number in writing before anything starts, and it won't move unless you ask for
      something new.</p>
    </div>
    <div class="grid g3 reveal">
      <article class="card card--dark">
        <h3>No long contracts</h3>
        <p style="margin-top:8px">The agreement covers the build. Care plans are month to month.</p>
      </article>
      <article class="card card--dark">
        <h3>Hosting, your call</h3>
        <p style="margin-top:8px">Run it yourself, or we handle hosting, updates and backups for a monthly fee.</p>
      </article>
      <article class="card card--dark">
        <h3>One number</h3>
        <p style="margin-top:8px">One for the build, one a month if you want us to keep looking after it.</p>
      </article>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How it goes</span>
      <h2>Five steps, about a month</h2>
    </div>
    <div class="track reveal">
      <div class="track__step">
        <span class="track__n">01</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Call</h3>
        <p>Thirty minutes on the business.</p>
      </div>
      <div class="track__step">
        <span class="track__n">02</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Intake form</h3>
        <p>You choose what's included. Quote in two days.</p>
      </div>
      <div class="track__step">
        <span class="track__n">03</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Draft</h3>
        <p>A designed homepage within a week.</p>
      </div>
      <div class="track__step">
        <span class="track__n">04</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Build</h3>
        <p>Pages, copy, photos, forms, search.</p>
      </div>
      <div class="track__step">
        <span class="track__n">05</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Launch</h3>
        <p>Tested on real phones, then live.</p>
      </div>
    </div>
    <div class="btn-row" style="margin-top:40px">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
      <a class="btn btn--ghost" href="services.html">See the services</a>
    </div>
  </div>
</section>

%s
"""
home = home % (badge("hero"), RIDGE, WAVE, SUN_HORIZON, MOUNTAIN_HORIZON, RIDGE)

# ==========================================================================
#  SERVICES
# ==========================================================================
def srow(tag, title, body, points):
    lis = "".join('<li><span class="sun" aria-hidden="true"></span><span>%s</span></li>' % p
                  for p in points)
    return """<article class="srow reveal">
  <div class="srow__intro">
    <span class="srow__tag">%s</span>
    <h3>%s</h3>
    <p>%s</p>
  </div>
  <ul class="checks">%s</ul>
</article>""" % (tag, title, body, lis)


def step(n, title, body, open_=False):
    return """      <details%s>
        <summary><span class="stepnum">%s</span>%s</summary>
        <p>%s</p>
      </details>""" % (" open" if open_ else "", n, title, body)


services = """
<section class="hero hero--lite">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    <div class="head" style="margin-bottom:0">
      <span class="eyebrow">Services</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">What we build, and what makes it work.</h1>
      <p class="lede" style="margin-top:20px">The website is the job. The rest exists because a
      site on its own doesn't get found, answered, or kept current.</p>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    %s
    %s
    %s
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How a project runs</span>
      <h2>Five steps, about a month</h2>
      <p class="lede" style="margin-top:18px">Open any step to see what happens and what we need
      from you to keep it moving.</p>
    </div>
    <div class="faq reveal">
%s
%s
%s
%s
%s
    </div>
  </div>
</section>

%s

<section class="section band-cream" style="padding-block:clamp(32px,3.8vw,52px)">
  <div class="wrap">
    <div class="card card--dark careplan reveal">
      <div class="split" style="align-items:start">
        <div>
          <span class="eyebrow">After launch</span>
          <h2>Care plan, if you want it</h2>
          <p class="small" style="margin-top:18px">Email lists, review generation and paid search
          come later, and only where they'd actually pay off.</p>
        </div>
        <div>
          <p class="lede">Hosting, backups, security updates and a monthly window for small
          changes. Month to month, and plenty of clients don't take it &mdash; nothing about the site
          depends on it.</p>
          <ul class="checks" style="margin-top:22px">
            <li><span class="sun" aria-hidden="true"></span><span>Hosting, SSL and daily backups</span></li>
            <li><span class="sun" aria-hidden="true"></span><span>Small edits each month, sent by text or email</span></li>
            <li><span class="sun" aria-hidden="true"></span><span>A short note on what people searched to reach you</span></li>
            <li><span class="sun" aria-hidden="true"></span><span>Month to month, cancel whenever</span></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal" style="max-width:52ch">
      <span class="eyebrow">Common questions</span>
      <h2>Before you call</h2>
    </div>
    <div class="faq reveal">
      <details>
        <summary>What does a site cost?</summary>
        <p>It depends on how many pages you need, whether we're writing the words, and whether
        booking or payments are involved. The quote comes from your intake form, in writing, and it
        doesn't move unless the job does. If you want a rough range before filling anything in, say
        so in the contact form and we'll send one.</p>
      </details>
      <details>
        <summary>How long does it take?</summary>
        <p>Three to four weeks from the call for most projects. The part that slows it down is
        almost always photos and content from your side, so we tell you exactly what we need on day
        one and chase it rather than letting it sit.</p>
      </details>
      <details>
        <summary>I don't have any good photos.</summary>
        <p>Common, and fixable. We'll either direct a shoot, work with what's on your phone, or
        build the design around type and colour so it doesn't lean on photography at all. What we
        won't do is fill your site with stock images of someone else's business.</p>
      </details>
      <details>
        <summary>Can I update it myself?</summary>
        <p>Yes. You get a site you can edit &mdash; hours, prices, photos, new services &mdash; and we walk
        you through it on a recorded call you can keep. If you'd rather never touch it, that's what
        the care plan is for.</p>
      </details>
      <details>
        <summary>What if I already have a site?</summary>
        <p>Then the first question is whether it needs rebuilding or just fixing. Sometimes a day of
        cleanup beats a new site, and we'll tell you that even though it's the smaller invoice. If
        we do rebuild, your existing pages get redirected so you don't lose the search rankings
        you've built up.</p>
      </details>
      <details>
        <summary>Do you work outside the area?</summary>
        <p>Yes. Nearly all of it happens over calls and shared links, so where you are makes little
        difference. Local businesses get an in-person kickoff if they'd like one.</p>
      </details>
    </div>
    <div class="reveal" style="text-align:center;margin-top:clamp(48px,5.6vw,72px)">
      <h2 style="max-width:22ch;margin-inline:auto">Not sure which of these you need?</h2>
      <p class="lede" style="margin:18px auto 0;text-align:center">That's the call. Bring the
      business, we'll bring the recommendation.</p>
      <div class="btn-row" style="justify-content:center;margin-top:28px">
        <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
      </div>
    </div>
  </div>
</section>

%s
""" % (
  RIDGE,
  srow("The core", "Website design &amp; build",
      "A complete site designed for your business rather than dropped into a template.",
      ["Homepage, services, about and contact, plus whatever else the business needs",
       "Copy written from a recorded call with you, not filled with filler",
       "Photo direction, a shot list, or editing for what you already have",
       "Mobile-first, fast, and tested on real devices",
       "Domain, hosting and email set up and handed over"]),
  srow("Getting found", "Local search",
      "Most service businesses are chosen from a map, not a search page.",
      ["Google Business Profile claimed, filled in and verified",
       "Service-area pages for the towns you actually cover",
       "Consistent name, address and phone everywhere it appears",
       "A simple, non-annoying way to ask for reviews"]),
  srow("Getting answered", "Booking &amp; lead capture",
      "The point of the site is the next conversation, so that's the easiest thing on the page.",
      ["Quote or booking forms that reach your inbox and your phone",
       "Scheduling connected to the calendar you already use",
       "Click-to-call and click-to-text on every screen",
       "Deposits or payments taken online where it makes sense"]),
  WAVE,
  step("01", "Call",
       "Thirty minutes. What you do, who you'd like more of, and what's getting in the way right "
       "now. No deck and no pitch &mdash; if we're not the right fit, you'll hear that on this call "
       "rather than three weeks later.", open_=True),
  step("02", "Intake form",
       "A short form where you choose the pages you need, the features that matter, and the look "
       "you're after. It takes about ten minutes and it's what the quote gets built from, so the "
       "number reflects your project rather than an average. You'll have it in writing within two "
       "days."),
  step("03", "Draft",
       "A designed homepage inside a week, so you're reacting to something real instead of a "
       "description. Tell us what's wrong with it &mdash; changes at this stage are expected, not "
       "charged for, and it's far cheaper to move things now than after the build."),
  step("04", "Build",
       "The rest of the pages, the words, the photos, the forms and the search setup. You review "
       "all of it on a private link before anyone else sees it. This is the stage that slows down "
       "if photos or content are still outstanding on your side."),
  step("05", "Launch",
       "We point the domain, test on real phones and real connections, and walk you through "
       "editing the site on a recorded call you can keep. Then we stay reachable &mdash; most "
       "questions turn up in week two, once you've started sending people to it."),
  PLAIN_HORIZON, MOUNTAIN_HORIZON, RIDGE)

# ==========================================================================
#  CONTACT
# ==========================================================================
contact = """
<section class="hero hero--lite">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    <div class="head" style="margin-bottom:0">
      <span class="eyebrow">Contact</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Tell us about the business.</h1>
      <p class="lede" style="margin-top:20px">You'll hear back within one business day, from a
      person, with either a question or a time to talk.</p>
    </div>
  </div>
</section>

<section class="section band-paper" style="padding-top:clamp(28px,3.5vw,44px)">
  <div class="wrap split">
    <div class="reveal">
      <div class="formstatus" id="formstatus" role="status">
        <h3>Form isn't connected yet</h3>
        <p class="small" style="margin-top:10px">Your details look complete, but this site has no
        form handler wired up. Point the form's <code>action</code> at Formspree, Netlify Forms or
        your own endpoint before launch.</p>
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
        <div class="btn-row" style="margin-top:4px">
          <button class="btn btn--primary" type="submit">Send it over <span class="arrow">&rarr;</span></button>
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
          <h3>What happens next</h3>
          <p class="small">A reply within one business day, then a thirty-minute call. A written
          quote within two days of that call. Nothing is charged until you say yes.</p>
        </div>
      </div>
    </div>
  </div>
</section>

%s
""" % RIDGE

# ==========================================================================
PAGES = [
 ("index.html","Beaumont West Solutions — Websites for service businesses",
  "We design and build websites for salons, studios, landscapers, trainers and trades. Live in three to four weeks, built for phones, and yours to keep.", home),
 ("services.html","Services — Beaumont West Solutions",
  "Website design and build, local search, booking and lead capture, copy and photo direction, and an optional monthly care plan.", services),
 ("contact.html","Contact — Beaumont West Solutions",
  "Tell us about your business. A reply within one business day, a thirty-minute call, and a written quote two days after that.", contact),
]

os.makedirs(OUT, exist_ok=True)
adir = os.path.join(OUT, "assets")
if os.path.abspath(SRC) != os.path.abspath(adir):
    os.makedirs(adir, exist_ok=True)
    for f in os.listdir(SRC):
        shutil.copy(os.path.join(SRC, f), os.path.join(adir, f))

# pages that no longer exist should not linger in the deploy folder
for gone in ("work.html", "about.html"):
    p = os.path.join(OUT, gone)
    if os.path.exists(p):
        os.remove(p)
        print("removed", gone)

for slug, title, desc, body in PAGES:
    with open(os.path.join(OUT, slug), "w") as fh:
        fh.write(page(slug, title, desc, body))
    print("wrote", slug, os.path.getsize(os.path.join(OUT, slug)), "bytes")
