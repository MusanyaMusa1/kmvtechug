# King Musah Media — Website

## How this is organised

- `data/articles.json` — the master list of every story. This is the single source of truth.
- `generate_site.py` — reads `articles.json` and builds every page from it.
- `index.html` — the homepage (generated, don't hand-edit).
- `stories/<slug>.html` — one permanent page per story (generated).
- `stories/index.html` — full archive of every story ever published (generated).
- `category/news.html`, `category/politics.html`, `category/entertainment.html`, `category/sports.html`, `category/business.html` — category pages (generated).
- `sitemap.xml`, `robots.txt` — for Google/search engines (generated).
- `assets/css/style.css`, `assets/js/main.js` — shared design + dark/light toggle + mobile menu.

## Why stories never disappear

Every page is generated *from* `articles.json`, which is never overwritten — only added to. Each time a
new story is added and the site is rebuilt, the homepage refreshes to show it, but every previous story
keeps its own permanent URL and its original publish date. Nothing is deleted.

## Adding a new story (what happens each time you send me one)

Send me: **title, category (news/politics/entertainment/sports/business), author, date, language
(English or Luganda), a short 1–2 sentence summary, and the story body.** I will:

1. Add it to `data/articles.json`
2. Run `python3 generate_site.py`
3. Give you the updated files — homepage, the new story's own page, its category page, and the sitemap
   will all be current.

## Before going live

Open `generate_site.py` and set `BASE_URL` at the top to your real published domain (e.g.
`https://yourdomain.com` or `https://yourdomain.com/media` if it lives in a subfolder) — it's currently
set to `https://kmvtechug.app/media` as a placeholder based on your GitHub project's structure. Then run
`python3 generate_site.py` once more so the sitemap and canonical links are correct, and submit
`sitemap.xml` to Google Search Console.

## Publishing on GitHub Pages

Push the whole folder to your GitHub repo (keeping the same folder structure) and enable GitHub Pages in
the repo settings. No build step is required on GitHub's side — every file is already static HTML.
