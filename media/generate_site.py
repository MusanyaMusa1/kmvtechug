#!/usr/bin/env python3
"""
King Musah Media — static site generator.

Run this any time articles.json changes (i.e. whenever a new story is added).
It regenerates:
  - index.html                (homepage: breaking ticker + hero + latest stories)
  - stories/<slug>.html       (one permanent page per story)
  - stories/index.html        (full archive of every story, filterable)
  - category/<slug>.html      (one page per category)
  - sitemap.xml
  - robots.txt

Usage:
    python3 generate_site.py
"""
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, "data", "articles.json")

# ---- CONFIG: update BASE_URL to your real published URL before going live ----
BASE_URL = "https://kmvtechug.app/media"
SITE_NAME = "King Musah Media"
CONTACT_EMAIL = "kingmusahmedia@gmail.com"

CATEGORIES = {
    "news": "News",
    "politics": "Politics",
    "entertainment": "Entertainment",
    "sports": "Sports",
    "business": "Business",
}

LANG_LABEL = {"en": "English", "lg": "Luganda"}

# Cache-busting: changes every time the site is rebuilt, so browsers and
# GitHub Pages' CDN pick up the new CSS/JS immediately instead of serving a
# stale cached copy for hours.
ASSET_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")

# ---- Google Analytics: paste your Measurement ID (looks like "G-XXXXXXXXXX")
# here once you've created a property at analytics.google.com. Leave as None
# to skip analytics entirely.
GA_MEASUREMENT_ID = "G-GEN75BG21K"

# ---- Google AdSense: paste your Publisher ID here once approved (looks like
# "ca-pub-1234567890123456"). Leave as None until then — ads won't render.
ADSENSE_PUBLISHER_ID = "ca-pub-2106771751457148"


def load_articles():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def fmt_date(iso_date):
    d = datetime.strptime(iso_date, "%Y-%m-%d")
    return d.strftime("%d %B %Y")


def initials(name):
    parts = name.split()
    return "".join(p[0] for p in parts[:2]).upper()


def nav_html(depth="", active=""):
    def link(href, label, key):
        cls = ' class="active"' if key == active else ""
        aria = ' aria-current="page"' if key == active else ""
        return f'<li><a href="{depth}{href}"{cls}{aria}>{label}</a></li>'

    links = [
        link("index.html", "Home", "home"),
        link("stories/index.html", "All Stories", "stories"),
        link("category/news.html", "News", "news"),
        link("category/politics.html", "Politics", "politics"),
        link("category/entertainment.html", "Entertainment", "entertainment"),
        link("category/sports.html", "Sports", "sports"),
        link("category/business.html", "Business", "business"),
    ]
    links.append(f'<li><a href="{depth}support.html" class="nav-cta">Support Us</a></li>')
    return "".join(links)


def mobile_nav_html(depth=""):
    items = [
        ("index.html", "Home"),
        ("stories/index.html", "All Stories"),
        ("category/news.html", "News"),
        ("category/politics.html", "Politics"),
        ("category/entertainment.html", "Entertainment"),
        ("category/sports.html", "Sports"),
        ("category/business.html", "Business"),
    ]
    return "".join(
        f'<a href="{depth}{href}" onclick="document.getElementById(\'mob\').classList.remove(\'open\')">{label}</a>'
        for href, label in items
    ) + f'<a href="{depth}support.html" style="color:var(--red);font-weight:700" onclick="document.getElementById(\'mob\').classList.remove(\'open\')">Support Us</a>'


def adsense_snippet():
    if not ADSENSE_PUBLISHER_ID:
        return ""
    return f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUBLISHER_ID}" crossorigin="anonymous"></script>'


def ga_snippet():
    if not GA_MEASUREMENT_ID:
        return ""
    return f'''<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>'''


def header_block(depth="", active=""):
    theme_icon = "&#9728;"
    logo_base = f"{depth}assets/logo-kmm"
    return f'''<a href="#main" class="skip-link">Skip to main content</a>
<nav>
  <a class="nav-logo" href="{depth}index.html">
    <img src="{logo_base}.jpg" data-base="{logo_base}" data-ext-idx="0" alt="King Musah Media" onerror="handleImgError(this)"/>
    <span class="nav-logo-text">King Musah Media</span>
  </a>
  <ul class="nav-links">
    {nav_html(depth, active)}
  </ul>
  <div class="theme-toggle">
    <button class="theme-btn" id="themeBtn" onclick="toggleTheme()" aria-label="Toggle dark and light mode">{theme_icon}</button>
    <button class="hamburger" id="hamburgerBtn" aria-label="Menu" aria-expanded="false" aria-controls="mob">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>
<div class="mobile-menu" id="mob">
  {mobile_nav_html(depth)}
</div>'''


def ticker_block(articles, depth=""):
    breaking = [a for a in articles if a.get("breaking")]
    if not breaking:
        return ""
    items = "".join(
        f'<a href="{depth}stories/{a["slug"]}.html">{a["title"]}</a>' for a in breaking
    )
    return f'''<div class="ticker-wrap" role="marquee" aria-label="Breaking news">
  <span class="ticker-label">Breaking</span>
  <div class="ticker-track">{items}{items}</div>
</div>'''


def footer_block(depth=""):
    return f'''<div class="back-bar">
  <a href="https://kmvtechug.app" class="back-link">&larr; Back to KMVTECHUG</a>
  <div class="hub-links">
    <a href="https://kmvtechug.app/tech/">KMVTECH</a>
    <a href="https://kmvtechug.app/education/">KMVTECH Education</a>
    <a href="https://kmvtechug.app/musa/">Musanya Musa</a>
  </div>
</div>
<footer>
  <div class="footer-bottom">
    <span>&copy; {datetime.now().year} King Musah Media. All rights reserved.</span>
    <div class="hub-links">
      <a href="{depth}privacy.html">Privacy Policy</a>
      <a href="{depth}terms.html">Terms of Service</a>
      <a href="mailto:{CONTACT_EMAIL}">Contact us</a>
    </div>
  </div>
</footer>
<script src="{depth}assets/js/main.js?v={ASSET_VERSION}"></script>'''


def image_tag(a, depth="", css_class=""):
    """Fallback-chained <img>: tries jfif/jpg/jpeg/png/webp named after the slug,
    in assets/images/. If none exist, main.js hides it and the placeholder
    icon behind it shows instead. Uploading a photo is just: name it
    <slug>.jfif (or .jpg etc.) and drop it in assets/images/ — no code edits."""
    base = f"{depth}assets/images/{a['slug']}"
    alt = a.get("image_alt", a["title"])
    cls = f' class="{css_class}"' if css_class else ""
    return f'<img{cls} src="{base}.jfif" data-base="{base}" data-ext-idx="0" alt="{alt}" loading="lazy" onerror="handleImgError(this)"/>'


def story_card(a, depth=""):
    breaking_flag = ' <span class="breaking-flag">&bull; Breaking</span>' if a.get("breaking") else ""
    return f'''<a class="story-card" href="{depth}stories/{a["slug"]}.html">
  <div class="story-media" aria-hidden="true">
    {image_tag(a, depth)}
    <span class="story-cat-tag">{CATEGORIES.get(a["category"], a["category"])}</span>
    <span class="story-lang-tag">{LANG_LABEL.get(a["language"], a["language"])}</span>
    &#128240;
  </div>
  <div class="story-body">
    <h3>{a["title"]}</h3>
    <p>{a["excerpt"]}</p>
    <div class="story-meta">
      <span>{a["author"]}</span><span class="dot">&middot;</span>
      <time datetime="{a["date"]}">{fmt_date(a["date"])}</time>{breaking_flag}
    </div>
  </div>
</a>'''


def build_index(articles):
    featured = [a for a in articles if a.get("featured")]
    hero = featured[0] if featured else articles[0]
    rest = [a for a in articles if a["slug"] != hero["slug"]][:8]
    cards = "\n".join(story_card(a) for a in rest)
    top_pad = "150px" if any(a.get("breaking") for a in articles) else "130px"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{SITE_NAME} — Ugandan News, Current Affairs &amp; Entertainment</title>
  <meta name="description" content="King Musah Media delivers up-to-date Ugandan news, politics, sports, business and entertainment coverage in English and Luganda."/>
  <link rel="canonical" href="{BASE_URL}/index.html"/>
  <meta property="og:type" content="website"/>
  <meta property="og:title" content="{SITE_NAME} — Ugandan News, Current Affairs &amp; Entertainment"/>
  <meta property="og:description" content="Breaking news and stories from Uganda and beyond — politics, sports, business and entertainment, in English and Luganda."/>
  <meta property="og:url" content="{BASE_URL}/index.html"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
  <script type="application/ld+json">
  {{"@context": "https://schema.org", "@type": "NewsMediaOrganization", "name": "{SITE_NAME}", "url": "{BASE_URL}/index.html"}}
  </script>
</head>
<body>
{header_block(active="home")}
{ticker_block(articles)}

<section class="sec" id="top-story" aria-label="Top story" style="padding-top:{top_pad}">
  <div class="sec-header"><div class="sec-header-text"><span class="sec-tag">Top Story</span><h2 class="sec-title">{CATEGORIES.get(hero["category"], hero["category"])} Spotlight</h2></div></div>
  <a class="hero-story" href="stories/{hero["slug"]}.html">
    <div class="hero-story-media" aria-hidden="true">{image_tag(hero)}&#128240;</div>
    <div class="hero-story-body">
      <span class="story-cat-tag" style="position:static;display:inline-block">{CATEGORIES.get(hero["category"], hero["category"])}</span>
      <h2>{hero["title"]}</h2>
      <p>{hero["excerpt"]}</p>
      <div class="story-meta">
        <span>{hero["author"]}</span><span class="dot">&middot;</span>
        <time datetime="{hero["date"]}">{fmt_date(hero["date"])}</time>
      </div>
    </div>
  </a>
</section>

<main id="main">
<section class="sec" id="latest" aria-label="Latest stories">
  <div class="sec-header">
    <div class="sec-header-text"><span class="sec-tag">Just In</span><h2 class="sec-title">Latest Stories</h2><p class="sec-sub">Fresh reporting from across Uganda, updated as it happens &mdash; older stories stay right where you left them.</p></div>
    <a class="view-all" href="stories/index.html">View all stories &rarr;</a>
  </div>
  <div class="cat-pills">
    <a class="cat-pill" href="category/news.html">News</a>
    <a class="cat-pill" href="category/politics.html">Politics</a>
    <a class="cat-pill" href="category/entertainment.html">Entertainment</a>
    <a class="cat-pill" href="category/sports.html">Sports</a>
    <a class="cat-pill" href="category/business.html">Business</a>
  </div>
  <div class="story-grid">
{cards}
  </div>
</section>

<section class="sec" id="content">
  <div class="sec-header"><div class="sec-header-text"><span class="sec-tag">What We Cover</span><h2 class="sec-title">Content That Matters</h2><p class="sec-sub">Relevant, accessible, and engaging digital content built for today's online audience.</p></div></div>
  <div class="content-grid">
    <div class="content-card"><div class="content-card-icon">&#128240;</div><h3>News &amp; Current Affairs</h3><p>Timely reporting on local, national, and international news. Keeping audiences informed on what matters most.</p></div>
    <div class="content-card"><div class="content-card-icon">&#128172;</div><h3>Social Commentary</h3><p>Thoughtful analysis of social issues, policies, and trends shaping Uganda and Africa today.</p></div>
    <div class="content-card"><div class="content-card-icon">&#127917;</div><h3>Entertainment</h3><p>Engaging entertainment content that connects with youth, students, and the general online community.</p></div>
    <div class="content-card"><div class="content-card-icon">&#128214;</div><h3>Digital Storytelling</h3><p>Compelling narratives and stories told through video, social media, and written content.</p></div>
  </div>
</section>

<section class="perf-section" id="performance">
  <span class="sec-tag">Our Numbers</span>
  <h2 class="sec-title">Growing Every Day</h2>
  <div class="perf-grid">
    <div class="perf-card"><h2>1.3<span>K</span></h2><p>YouTube Subscribers</p></div>
    <div class="perf-card"><h2>152<span>K</span></h2><p>Total Views</p></div>
    <div class="perf-card"><h2>2020</h2><p>Year Founded</p></div>
    <div class="perf-card"><h2>4<span>+</span></h2><p>Platforms Active</p></div>
  </div>
</section>

<section class="sec" id="platforms">
  <div class="sec-header"><div class="sec-header-text"><span class="sec-tag">Find Us Online</span><h2 class="sec-title">Our Platforms</h2><p class="sec-sub">Follow King Musah Media on all major platforms for daily updates.</p></div></div>
  <div class="platform-grid">
    <a href="https://www.youtube.com/@kingmusahmedia" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:#FF0000">&#9654;</div><div><h4>YouTube</h4><p>@kingmusahmedia &middot; 1.3K subscribers</p></div></a>
    <a href="https://x.com/KingMusahMedia" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:#000;border:1px solid #333">&#120143;</div><div><h4>X / Twitter</h4><p>@KingMusahMedia</p></div></a>
    <a href="https://www.facebook.com/profile.php?id=100082996675651" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:#1877F2">f</div><div><h4>Facebook</h4><p>King Musah Media</p></div></a>
    <a href="https://www.instagram.com/king_musah_media" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)">&#128247;</div><div><h4>Instagram</h4><p>@king_musah_media</p></div></a>
    <a href="https://linkedin.com/company/king-musah-media" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:#0A66C2">in</div><div><h4>LinkedIn</h4><p>King Musah Media</p></div></a>
    <a href="https://wa.me/message/XMUHKTZJ6633I1" target="_blank" rel="noopener" class="platform"><div class="platform-icon" style="background:#25D366">&#128172;</div><div><h4>WhatsApp</h4><p>Message King Musah Media</p></div></a>
  </div>
</section>

<section class="contact-sec" id="contact">
  <h2>Let's Work Together</h2>
  <p>For media partnerships, news tips, advertising, or collaborations &mdash; reach out directly. We're always open to good stories and great partners.</p>
  <div class="contact-links">
    <a href="mailto:{CONTACT_EMAIL}" class="contact-link">&#128231; Email us</a>
    <a href="tel:+256759405181" class="contact-link">&#128241; +256 759 405 181</a>
    <a href="https://wa.me/256759405181" target="_blank" rel="noopener" class="contact-link">&#128172; WhatsApp</a>
  </div>
</section>
</main>

{footer_block()}
</body>
</html>'''
    write(os.path.join(ROOT, "index.html"), html)


def build_article(a, articles):
    related = [x for x in articles if x["category"] == a["category"] and x["slug"] != a["slug"]][:3]
    related_html = "\n".join(story_card(r, depth="../") for r in related) or '<p class="empty-state" style="color:var(--text-faint)">More stories coming soon.</p>'

    tags_html = "".join(f'<span class="article-tag">{t}</span>' for t in a.get("tags", []))
    body_html = "\n".join(f"<p>{p}</p>" for p in a["content"])

    lang_note = ""
    if a["language"] == "lg":
        lang_note = '<div class="lang-note">&#127760; This story is published in <strong>Luganda</strong>.</div>'

    share_url = f'{BASE_URL}/stories/{a["slug"]}.html'
    json_ld = (
        '{"@context": "https://schema.org", "@type": "NewsArticle", '
        f'"headline": {json.dumps(a["title"])}, '
        f'"datePublished": "{a["date"]}", "dateModified": "{a["date"]}", '
        f'"author": {{"@type": "Person", "name": {json.dumps(a["author"])}}}, '
        f'"publisher": {{"@type": "Organization", "name": "{SITE_NAME}"}}, '
        f'"articleSection": {json.dumps(CATEGORIES.get(a["category"], a["category"]))}, '
        f'"inLanguage": "{a["language"]}", '
        f'"description": {json.dumps(a["excerpt"])}, '
        f'"mainEntityOfPage": {json.dumps(share_url)}}}'
    )

    html = f'''<!DOCTYPE html>
<html lang="{a["language"]}">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{a["title"]} — {SITE_NAME}</title>
  <meta name="description" content="{a["excerpt"]}"/>
  <link rel="canonical" href="{share_url}"/>
  <meta property="og:type" content="article"/>
  <meta property="og:title" content="{a["title"]}"/>
  <meta property="og:description" content="{a["excerpt"]}"/>
  <meta property="og:url" content="{share_url}"/>
  <meta property="article:published_time" content="{a["date"]}"/>
  <meta property="article:author" content="{a["author"]}"/>
  <meta property="article:section" content="{CATEGORIES.get(a["category"], a["category"])}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="../assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
  <script type="application/ld+json">
  {json_ld}
  </script>
</head>
<body>
{header_block(depth="../", active=a["category"])}

<main id="main">
<article class="article-wrap">
  <span class="article-cat">{CATEGORIES.get(a["category"], a["category"])}</span>
  <h1 class="article-title">{a["title"]}</h1>
  <div class="article-byline">
    <div class="author-avatar" aria-hidden="true">{initials(a["author"])}</div>
    <div>
      <div class="byline-name">{a["author"]}</div>
      <div>Published <time datetime="{a["date"]}">{fmt_date(a["date"])}</time> &middot; {LANG_LABEL.get(a["language"], a["language"])}</div>
    </div>
  </div>
  {lang_note}
  <div class="article-media" aria-hidden="true">{image_tag(a, depth="../")}&#128247; {a.get("image_alt", "")}</div>
  <div class="article-body">
{body_html}
  </div>
  <div class="article-tags">{tags_html}</div>
  <div class="share-row">
    <span>Share this story</span>
    <a class="share-btn" target="_blank" rel="noopener" aria-label="Share on WhatsApp" href="https://wa.me/?text={a["title"].replace(' ', '%20')}%20{share_url}">&#128172;</a>
    <a class="share-btn" target="_blank" rel="noopener" aria-label="Share on X" href="https://twitter.com/intent/tweet?url={share_url}&text={a["title"].replace(' ', '%20')}">&#120143;</a>
    <a class="share-btn" target="_blank" rel="noopener" aria-label="Share on Facebook" href="https://www.facebook.com/sharer/sharer.php?u={share_url}">f</a>
  </div>

  <h2 class="related-heading">More in {CATEGORIES.get(a["category"], a["category"])}</h2>
  <div class="story-grid">
{related_html}
  </div>
</article>
</main>

{footer_block(depth="../")}
</body>
</html>'''
    write(os.path.join(ROOT, "stories", f'{a["slug"]}.html'), html)


def build_category(cat_key, cat_label, articles):
    items = [a for a in articles if a["category"] == cat_key]
    cards = "\n".join(story_card(a, depth="../") for a in items) or '<p class="empty-state" style="color:var(--text-faint)">No stories in this category yet — check back soon.</p>'
    pills = "".join(
        f'<a class="cat-pill{" active" if k == cat_key else ""}" href="{k}.html">{v}</a>'
        for k, v in CATEGORIES.items()
    )
    top_pad = "150px" if any(a.get("breaking") for a in articles) else "130px"
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{cat_label} — {SITE_NAME}</title>
  <meta name="description" content="{cat_label} news and stories from {SITE_NAME}, covering Uganda and beyond."/>
  <link rel="canonical" href="{BASE_URL}/category/{cat_key}.html"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="../assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
</head>
<body>
{header_block(depth="../", active=cat_key)}
{ticker_block(articles, depth="../")}

<main id="main">
<section class="sec" style="padding-top:{top_pad}">
  <div class="sec-header"><div class="sec-header-text"><span class="sec-tag">Category</span><h2 class="sec-title">{cat_label}</h2><p class="sec-sub">All {cat_label.lower()} stories from {SITE_NAME}, newest first.</p></div></div>
  <div class="cat-pills">{pills}</div>
  <div class="story-grid">
{cards}
  </div>
</section>
</main>

{footer_block(depth="../")}
</body>
</html>'''
    write(os.path.join(ROOT, "category", f"{cat_key}.html"), html)


def build_archive(articles):
    cards = "\n".join(story_card(a, depth="../") for a in articles)
    pills = "".join(f'<a class="cat-pill" href="../category/{k}.html">{v}</a>' for k, v in CATEGORIES.items())
    top_pad = "150px" if any(a.get("breaking") for a in articles) else "130px"
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>All Stories — {SITE_NAME}</title>
  <meta name="description" content="Browse every story published by {SITE_NAME}, from breaking news to archived reporting."/>
  <link rel="canonical" href="{BASE_URL}/stories/index.html"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="../assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
</head>
<body>
{header_block(depth="../", active="stories")}
{ticker_block(articles, depth="../")}

<main id="main">
<section class="sec" style="padding-top:{top_pad}">
  <div class="sec-header"><div class="sec-header-text"><span class="sec-tag">Archive</span><h2 class="sec-title">All Stories</h2><p class="sec-sub">Every story we've published, newest first. Nothing gets deleted when the homepage updates.</p></div></div>
  <div class="cat-pills">{pills}</div>
  <div class="story-grid">
{cards}
  </div>
</section>
</main>

{footer_block(depth="../")}
</body>
</html>'''
    write(os.path.join(ROOT, "stories", "index.html"), html)


def build_sitemap(articles):
    urls = [f"{BASE_URL}/index.html", f"{BASE_URL}/stories/index.html"]
    urls += [f"{BASE_URL}/category/{k}.html" for k in CATEGORIES]
    urls += [f"{BASE_URL}/stories/{a['slug']}.html" for a in articles]
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    write(os.path.join(ROOT, "sitemap.xml"), xml)


def build_ads_txt():
    if not ADSENSE_PUBLISHER_ID:
        return
    pub_id = ADSENSE_PUBLISHER_ID.replace("ca-", "")
    txt = f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n"
    write(os.path.join(ROOT, "ads.txt"), txt)


def build_robots():
    txt = f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n"
    write(os.path.join(ROOT, "robots.txt"), txt)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(path, ROOT))


def build_privacy_policy():
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Privacy Policy — {SITE_NAME}</title>
  <meta name="description" content="How King Musah Media collects, uses, and protects information from visitors to this website."/>
  <link rel="canonical" href="{BASE_URL}/privacy.html"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
</head>
<body>
{header_block()}

<main id="main">
<article class="article-wrap" style="max-width:820px">
  <span class="article-cat">Legal</span>
  <h1 class="article-title">Privacy Policy</h1>
  <div class="article-byline"><div>Last updated: {datetime.now().strftime("%d %B %Y")}</div></div>
  <div class="article-body">
    <p>King Musah Media ("we", "us", "our") operates this website to publish news and current affairs coverage in Uganda. This policy explains what information we collect from visitors and how it is used.</p>

    <p><strong>Information we collect.</strong> We do not require you to create an account or provide personal information to read our content. If you choose to contact us by email, WhatsApp, or phone, we receive whatever information you share with us directly. If you send a donation via Mobile Money, we may see your name and phone number as provided by the mobile money network, but we do not store payment card details ourselves.</p>

    <p><strong>Analytics.</strong> We use Google Analytics to understand how visitors use this site &mdash; for example, which stories are most read and which countries our audience comes from. Google Analytics uses cookies and collects information such as your approximate location, device type, and browsing behaviour on this site. This data is aggregated and does not identify you personally. You can opt out of Google Analytics tracking using browser extensions such as Google's own Analytics Opt-out Browser Add-on.</p>

    <p><strong>Advertising.</strong> This site may display advertisements served by Google AdSense. Google and its partners may use cookies to serve ads based on your prior visits to this or other websites. You can learn more about how Google uses this information and manage your ad preferences at <a href="https://policies.google.com/technologies/ads" style="color:var(--red)">policies.google.com/technologies/ads</a>. You may opt out of personalised advertising by visiting <a href="https://adssettings.google.com" style="color:var(--red)">Google Ads Settings</a>.</p>

    <p><strong>Cookies.</strong> Cookies are small text files stored on your device. Aside from the analytics and advertising cookies described above, this site uses your browser's local storage only to remember your light/dark theme preference &mdash; this is not shared with anyone and stays on your own device.</p>

    <p><strong>Third-party links.</strong> Our stories and pages may link to external websites, including government sources, social media, and other news outlets. We are not responsible for the privacy practices of those external sites.</p>

    <p><strong>Children's privacy.</strong> This site is a general news publication not directed at children, and we do not knowingly collect personal information from children.</p>

    <p><strong>Changes to this policy.</strong> We may update this policy from time to time as our services evolve. Continued use of the site after changes are posted constitutes acceptance of the revised policy.</p>

    <p><strong>Contact us.</strong> If you have questions about this policy, reach us at <a href="mailto:{CONTACT_EMAIL}" style="color:var(--red)">{CONTACT_EMAIL}</a>.</p>
  </div>
</article>
</main>

{footer_block()}
</body>
</html>'''
    write(os.path.join(ROOT, "privacy.html"), html)


def build_terms_of_service():
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Terms of Service — {SITE_NAME}</title>
  <meta name="description" content="The terms governing use of the King Musah Media website and its content."/>
  <link rel="canonical" href="{BASE_URL}/terms.html"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
</head>
<body>
{header_block()}

<main id="main">
<article class="article-wrap" style="max-width:820px">
  <span class="article-cat">Legal</span>
  <h1 class="article-title">Terms of Service</h1>
  <div class="article-byline"><div>Last updated: {datetime.now().strftime("%d %B %Y")}</div></div>
  <div class="article-body">
    <p>By accessing or using the King Musah Media website ("the Site"), you agree to these Terms of Service. If you do not agree, please do not use the Site.</p>

    <p><strong>Our content.</strong> Articles, images, and other material published on this Site are provided for general informational purposes. While we make reasonable efforts to verify facts before publishing, news is often developing and details may be revised or corrected as more information becomes available. We are an independent Ugandan media outlet and our reporting reflects our own editorial judgment.</p>

    <p><strong>No professional advice.</strong> Nothing on this Site constitutes legal, financial, medical, or other professional advice. Readers should consult qualified professionals for advice specific to their circumstances.</p>

    <p><strong>Intellectual property.</strong> Unless otherwise stated, content on this Site is the property of King Musah Media. You may share links to our articles and quote brief excerpts with attribution, but you may not republish, redistribute, or reproduce substantial portions of our content without our prior written permission.</p>

    <p><strong>User conduct.</strong> If we introduce comments, forums, or submission features in the future, you agree not to post content that is defamatory, hateful, obscene, or unlawful, or that infringes on the rights of others.</p>

    <p><strong>External links.</strong> This Site may link to third-party websites for reference or source material. We do not control and are not responsible for the content or practices of those sites.</p>

    <p><strong>Donations.</strong> Contributions made through the Mobile Money numbers or payment methods listed on our Support page are voluntary and go toward supporting our journalism and operations. Donations are not refundable except where required by law or at our discretion in cases of clear error.</p>

    <p><strong>Advertising.</strong> This Site may display third-party advertisements, including through Google AdSense. We are not responsible for the content of advertisements or the products/services they promote.</p>

    <p><strong>Disclaimer of warranties.</strong> The Site is provided "as is" without warranties of any kind, express or implied. We do not guarantee the Site will be uninterrupted, error-free, or free of viruses or other harmful components.</p>

    <p><strong>Limitation of liability.</strong> To the fullest extent permitted by law, King Musah Media shall not be liable for any indirect, incidental, or consequential damages arising from your use of the Site.</p>

    <p><strong>Governing law.</strong> These Terms are governed by the laws of the Republic of Uganda.</p>

    <p><strong>Changes to these terms.</strong> We may update these Terms from time to time. Continued use of the Site after changes are posted constitutes acceptance of the revised Terms.</p>

    <p><strong>Contact us.</strong> Questions about these Terms can be sent to <a href="mailto:{CONTACT_EMAIL}" style="color:var(--red)">{CONTACT_EMAIL}</a>.</p>
  </div>
</article>
</main>

{footer_block()}
</body>
</html>'''
    write(os.path.join(ROOT, "terms.html"), html)


def build_support():
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Support Independent Media — {SITE_NAME}</title>
  <meta name="description" content="Support King Musah Media's independent journalism in Uganda. Every contribution helps us keep reporting the stories that matter."/>
  <link rel="canonical" href="{BASE_URL}/support.html"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="assets/css/style.css?v={ASSET_VERSION}"/>
  {ga_snippet()}
  {adsense_snippet()}
</head>
<body>
{header_block(active="support")}

<main id="main">
<section class="support-hero">
  <span class="sec-tag">Independent Media Needs You</span>
  <h1>Support King Musah Media</h1>
  <p>We report Uganda's news as it happens &mdash; without fear or favour. Independent journalism takes real resources: reporters on the ground, fact-checking, and the time it takes to get a story right. If our coverage has informed or moved you, consider supporting the newsroom directly. Every contribution, big or small, helps.</p>
</section>

<div class="pay-grid">
  <div class="pay-card">
    <div class="pay-icon" style="background:#ED1C24">&#128241;</div>
    <h3>Airtel Money</h3>
    <div class="pay-number">+256 759 405 181</div>
    <p class="pay-note">Send directly via Airtel Money to this number. Please add "KMM Support" as the reason for reference.</p>
  </div>
  <div class="pay-card">
    <div class="pay-icon" style="background:#FFCB05;color:#000">&#128241;</div>
    <h3>MTN Mobile Money</h3>
    <div class="pay-number">+256 760 108 150</div>
    <p class="pay-note">Send directly via MTN MoMo to this number. Please add "KMM Support" as the reason for reference.</p>
  </div>
  <div class="pay-card soon">
    <span class="pay-badge">Coming Soon</span>
    <div class="pay-icon" style="background:#EB001B">&#128179;</div>
    <h3>Card Payment</h3>
    <div class="pay-number">Mastercard &bull;&bull;&bull;&bull; 4487</div>
    <p class="pay-note">Secure online card payments are being set up and will be available here shortly.</p>
  </div>
</div>

<p class="support-note">King Musah Media is an independent Ugandan media outlet. Contributions support reporting costs and are not tax-deductible. For partnership or advertising enquiries instead, visit our <a href="index.html#contact" style="color:var(--red)">contact section</a>.</p>
</main>

{footer_block()}
</body>
</html>'''
    write(os.path.join(ROOT, "support.html"), html)


def main():
    articles = load_articles()
    build_index(articles)
    build_archive(articles)
    for cat_key, cat_label in CATEGORIES.items():
        build_category(cat_key, cat_label, articles)
    for a in articles:
        build_article(a, articles)
    build_support()
    build_privacy_policy()
    build_terms_of_service()
    build_sitemap(articles)
    build_ads_txt()
    build_robots()
    print(f"\nDone. {len(articles)} articles built.")

    # Warn about story pages that exist on disk but are no longer in
    # articles.json — these are orphans left over from a removed/renamed
    # story and won't be linked from anywhere, but stay live if uploaded.
    current_slugs = {a["slug"] for a in articles}
    stories_dir = os.path.join(ROOT, "stories")
    if os.path.isdir(stories_dir):
        on_disk = {f[:-5] for f in os.listdir(stories_dir) if f.endswith(".html") and f != "index.html"}
        orphans = on_disk - current_slugs
        if orphans:
            print("\n\u26a0\ufe0f  ORPHANED STORY FILES (delete these from GitHub too):")
            for o in sorted(orphans):
                print(f"   stories/{o}.html")


if __name__ == "__main__":
    main()
