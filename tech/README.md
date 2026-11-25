# Digital Independence Initiative website

## Project contents

This is a static, responsive, multi-page website for Digital Independence Initiative, a community impact initiative under KMVTECH.

Pages included:
- `index.html` — Home
- `about.html` — About the initiative
- `programmes.html` — Learn, Navigate, Create and Protect
- `our-journey.html` — Inclusive Digital Skills and the Millennium Fellowship Class of 2026 journey
- `team.html` — Volunteer team
- `get-involved.html` — Ways to contribute and an email-based enquiry form

## Preview locally

Open `index.html` in a browser, or serve this folder using any static web server. All page links are relative, so the site can be placed in a subdirectory without rewriting navigation.

## Deployment notes for the KMVTECH team

1. Upload the contents of this folder to the final approved route on the KMVTECH website. The final public URL/path has intentionally not been hard-coded because the KMVTECH rebuild team must confirm it.
2. Once the final route is known, add the canonical URL and matching Open Graph URL to each page. Update the JSON-LD `url` field with the same final site URL.
3. Generate `sitemap.xml` using the final absolute URLs for all six pages. Submit that sitemap in Google Search Console.
4. Add the sitemap location to the domain-root `robots.txt` managed by the KMVTECH/domain team. Do not replace the existing root robots.txt or use this project folder to override domain-wide crawl rules.
5. Verify the final URLs, HTTPS, redirects, page titles, metadata, image loading and mobile navigation after deployment. Request indexing in Google Search Console; indexing is controlled by search engines and is not guaranteed or immediate.
6. If the site is deployed under a path other than the current preview path, confirm that static asset paths remain relative (they are relative in this build).

## Enquiry form

The Get Involved form prepares an email addressed to `kmvtechug@gmail.com` using the visitor's default email application. It does not store form submissions on a server and does not process donations or payments. If the team later adds a secure form backend, update the privacy notice and form handling accordingly.

## Content and accuracy notes

- The initiative is described as a community impact initiative under KMVTECH. It is not described as a programme operated or endorsed by the Millennium Campus Network or United Nations Academic Impact.
- The Our Journey page distinguishes the 38 registered participants at the 17 October 2026 community engagement from broader reach or long-term outcomes.
- Further community training activities are described as requiring development and resources; the site does not claim they have already been delivered.
- The existing team photographs and initiative mark are retained from the supplied project ZIP. Unused sister-brand supporter logos have not been presented as sponsors or funders.

## Contact details carried over from the supplied website

- Email: `kmvtechug@gmail.com`
- Telephone: `+256 759 405 181`
- Additional telephone from supplied website: `+256 760 108 150`
- Location: Kampala, Uganda

Please confirm these contact details remain current before public deployment.
