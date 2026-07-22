# Adding a story without Claude — backup method

Once the auto-build workflow (`.github/workflows/build-site.yml`) is installed and
enabled, you can add a story directly on GitHub, with no waiting on Claude and no
Python needed on your computer. GitHub itself rebuilds the whole site automatically
within about a minute of you saving.

## Steps

1. On GitHub, open `media/data/articles.json` and click the pencil (edit) icon.
2. Right near the very top, find the line that says `[` followed by the first `{`.
   Copy this whole template block and paste it as a **new entry directly under
   that opening `[`**, then fill in your real story:

```json
  {
    "slug": "a-short-url-friendly-title-no-spaces",
    "title": "Your Full Headline Here",
    "category": "news",
    "language": "en",
    "author": "Musanya Musa",
    "date": "2026-07-22",
    "breaking": true,
    "featured": false,
    "excerpt": "One or two sentence summary shown on story cards.",
    "image_alt": "Short description of the photo, for accessibility",
    "content": [
      "First paragraph of the story.",
      "Second paragraph of the story.",
      "Third paragraph, and so on."
    ],
    "tags": ["Tag One", "Tag Two"]
  },
```

3. **Rules that matter — breaking this will break the whole site:**
   - `category` must be exactly one of: `news`, `politics`, `entertainment`, `sports`, `business`
   - `language` must be exactly `en` or `lg`
   - `date` must be in the format `YYYY-MM-DD`
   - Every block needs a comma `,` after its closing `}` — **except the very
     last story in the whole file**, which must NOT have a trailing comma
   - `slug` should be all lowercase, words separated by hyphens, no spaces or
     punctuation
   - Straight double quotes only (`"`), never curly/smart quotes — if you typed
     your story in Word first, retype quote marks by hand after pasting, or
     Word's "smart quotes" will break the file
   - If your story text itself contains a `"` (a quote within a quote), put a
     backslash before it: `\"like this\"`

4. Scroll down, write a commit message like "Add story: [headline]", and commit
   directly to `main`.
5. Wait about a minute, then check the "Actions" tab in your repo — you should
   see a green checkmark once the auto-rebuild finishes. Your new story is now
   live on the homepage, its category page, and the archive automatically.

## If something breaks

If the site looks broken after an edit, the most common cause is a JSON typo
(a missing comma or an extra one, or a stray smart-quote). Open `articles.json`
again, find your new block, and check it carefully against the template above —
or just send Claude the story text again and mention "I tried adding this myself
and something broke" so it can find and fix the exact issue.

## Photos

Same as always: name the photo file to match your `slug`, save as `.jfif` or
`.jpg`, and upload it into `media/assets/images/`.
