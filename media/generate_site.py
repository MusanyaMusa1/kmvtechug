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
    )


def header_block(depth="", active=""):
    theme_icon = "&#9728;"
    return f'''<a href="#main" class="skip-link">Skip to main content</a>
<nav>
  <a class="nav-logo" href="{depth}index.html">
    <img src="{depth}assets/logo-kmm.png" alt="King Musah Media" onerror="this.style.display='none'"/>
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
    <a href="mailto:info@kingmusahmedia.com">Contact us</a>
  </div>
</footer>
<script src="{depth}assets/js/main.js?v={ASSET_VERSION}"></script>'''


def image_tag(a, depth="", css_class=""):
    """Fallback-chained <img>: tries jpg/jpeg/png/webp named after the slug,
    in assets/images/. If none exist, main.js hides it and the placeholder
    icon behind it shows instead. Uploading a photo is just: name it
    <slug>.jpg (or .png etc.) and drop it in assets/images/ — no code edits."""
    base = f"{depth}assets/images/{a['slug']}"
    alt = a.get("image_alt", a["title"])
    cls = f' class="{css_class}"' if css_class else ""
    return f'<img{cls} src="{base}.jpg" data-base="{base}" data-ext-idx="0" alt="{alt}" loading="lazy" onerror="handleImgError(this)"/>'


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
    <a href="mailto:info@kingmusahmedia.com" class="contact-link">&#128231; Email us</a>
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


def build_robots():
    txt = f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n"
    write(os.path.join(ROOT, "robots.txt"), txt)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    articles = load_articles()
    build_index(articles)
    build_archive(articles)
    for cat_key, cat_label in CATEGORIES.items():
        build_category(cat_key, cat_label, articles)
    for a in articles:
        build_article(a, articles)
    build_sitemap(articles)
    build_robots()
    print(f"\nDone. {len(articles)} articles built.")


if __name__ == "__main__":
    main()
