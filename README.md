# ESM Engineers website

A static website in plain HTML, CSS, and JavaScript, with English and Spanish pages. It needs no build step, framework, or package install.

## View it

Open `index.html` in a browser, or serve the folder with any static web server, for example:

```sh
python3 -m http.server 8000
```

Then visit http://localhost:8000. `404.html` uses root-relative links because a server can show it at any URL depth, so view it through a server, not by opening the file directly.

## How it is organized

```
index.html                 Home (English)
about/  contact/  blog/    English pages
services/                  Services overview and six service pages
blog/<article-slug>/       Five archived articles (English only)
es/                        Spanish versions of every page except the articles
404.html                   Not-found page
assets/css/site.css        All styles
assets/js/site.js          Mobile menu, hero photo switcher, services hover, email-draft forms, scroll reveal
assets/img/                Photos, logos, hero badge
assets/fonts/              Space Grotesk and Inter, with their OFL licences
redirects.csv              Old site URLs and where they should point
robots.txt                 Keeps the review site out of search engines
```

Every page is complete on its own and works without JavaScript; the script only adds enhancements.

## Editing

- The header and footer are repeated in every page. When you change a navigation link, contact detail, or service name, update it in all pages. Search across the project for the old text to find every copy.
- Each service appears in its own page, in the services overview, on the home page, in the footer, in the service sidebar, and in the contact form's service list, in both languages.
- Links between pages are relative (for example `../contact/index.html`) so the site also works when opened from disk.
- Colours, fonts, and spacing are defined once as custom properties at the top of `assets/css/site.css`.

## Before launch

- The contact and UPS forms open a draft in the visitor's email app. For production, connect them to a form service or backend, and test recipient routing, spam protection, and real submissions in both languages.
- Confirm that the public company number used for "Call UPS" reaches the intended support team.
- Review the archived photos for permissions and sensitive site details. Review staff, privacy notice, certification wording, and any projects before adding them.
- Set up the redirects in `redirects.csv` on the host, keep the existing article URLs, and check locale routing and analytics before switching the domain.
- The site is set to stay out of search indexes: every page has `<meta name="robots" content="noindex, nofollow">` and `robots.txt` blocks crawlers. Remove both, and add canonical URLs, after sign-off.

## Stock photo sources

- `office-facade.webp` by Çağrı Kanmaz, [Pexels image 20843180](https://www.pexels.com/photo/office-building-with-a-glass-facade-against-the-blue-sky-20843180/). [Pexels license](https://www.pexels.com/license/).
- `rooftop-cooling.webp` by Kayven, [Unsplash image XoU0NEvH7wU](https://unsplash.com/photos/industrial-cooling-towers-on-a-rooftop-XoU0NEvH7wU). [Unsplash license](https://unsplash.com/license).
- `houston-skyline.webp` by Christopher Politano, [Unsplash image NqNjVUbQGIc](https://unsplash.com/photos/modern-skyscrapers-rise-into-a-clear-blue-sky-NqNjVUbQGIc). [Unsplash license](https://unsplash.com/license).

Use the stock images as illustrative building and equipment photography. The ESM archive supplies `testing.webp` and `switchgear.webp`.
