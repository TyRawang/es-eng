# ESM Engineers website

Open `dist/index.html` in a browser to review the site offline. Navigation, English and Spanish pages, images, and typefaces are included. The five archived articles are available in their original English.

The editable source is `build.py`, `template_build.py`, `source/services.py`, `source/posts.json`, and `source/assets`. The selected Trends-Eng page layouts are in `source/template`, with their dependencies in `source/template-assets`. With Python and lxml installed, run `python3 build.py` to rebuild `dist`. The build replaces the whole `dist` folder, so edit the source files, not the output. `dist` is committed so the review site can be opened without building. `404.html` uses root-relative links because a server shows it at any URL depth, so view it through a web server, not by opening the file directly. The optional `prepare.py` records how the separate offline archive assets were prepared. A rebuild uses the included files and does not require the archives.

## Webflow handoff

- Apply the content and brand changes to an editable, licensed Trends-Eng Webflow project. This review uses the original template’s markup, styles, and selected interactions. Use the six service records and five article records for Webflow Collections. The static files are a working reference.
- Use the supplied Space Grotesk and Inter faces, ESM palette, and original wordmark treatment. Review the archived photos for permissions and sensitive site details before production.
- The review build uses click-to-call and email drafts. Configure two distinct Webflow forms and verify recipient routing, spam protection, and real submissions in both languages before cutover. The public company number is used for the review's call actions. Confirm it routes to the intended support team.
- Review the current staff roster, privacy notice, certification wording, and any projects before adding them to the public site.
- Apply the suggested redirects in `webflow-redirects.csv` after the corresponding pages are staged. Retain existing article slugs where Webflow accepts them. Confirm old URL redirects, locale routing, SEO, and analytics before the production domain switch.
- This build is configured to stay out of search indexes. Configure production indexing and canonical URLs in Webflow after sign-off.

## Stock photo sources

- `office-facade.webp` by Çağrı Kanmaz, [Pexels image 20843180](https://www.pexels.com/photo/office-building-with-a-glass-facade-against-the-blue-sky-20843180/). [Pexels license](https://www.pexels.com/license/).
- `rooftop-cooling.webp` by Kayven, [Unsplash image XoU0NEvH7wU](https://unsplash.com/photos/industrial-cooling-towers-on-a-rooftop-XoU0NEvH7wU). [Unsplash license](https://unsplash.com/license).
- `houston-skyline.webp` by Christopher Politano, [Unsplash image NqNjVUbQGIc](https://unsplash.com/photos/modern-skyscrapers-rise-into-a-clear-blue-sky-NqNjVUbQGIc). [Unsplash license](https://unsplash.com/license).

Use the stock images as illustrative building and equipment photography. The ESM archive supplies `testing.webp` and `switchgear.webp`.
