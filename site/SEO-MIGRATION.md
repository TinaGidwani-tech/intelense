# SEO migration: www.intelense.com

The old site's sitemap lists 44 URLs. Search engines have ranked these addresses, so each one has to either keep working or redirect with a 301.

## Old URL status

| Old URL | New site |
|---|---|
| `/` | Same URL on the new site: Home |
| `/ken360` | Same URL on the new site: Platform (platform.html) |
| `/kenvision` | Same URL on the new site: KenVision |
| `/kensafety` | Same URL on the new site: KenSafety |
| `/kenhome` | Same URL on the new site: KenHome |
| `/kenagri` | Same URL on the new site: KenAgri |
| `/keniot` | Same URL on the new site: KenIoT |
| `/kenrobotics` | Same URL on the new site: KenRobotics |
| `/retail-analytics` | Same URL on the new site: rebuilt from the old text |
| `/video-analytics-retail` | 301 to `/retail-analytics` (the old page was only a redirect stub) |
| `/footfall-analytics` | 301 to `/retail-analytics` (the old page was only a redirect stub) |
| `/queue-analytics` | 301 to `/retail-analytics` (the old page was only a redirect stub) |
| `/heatmap-analytics` | 301 to `/retail-analytics` (the old page was only a redirect stub) |
| `/cctv-analytics-retail` | 301 to `/retail-analytics` (the old page was only a redirect stub) |
| `/casestudies` | Same URL on the new site: rebuilt from the old text |
| `/kensafety-construction` | Same URL on the new site: rebuilt from the old text |
| `/kenvision-retail` | Same URL on the new site: rebuilt from the old text |
| `/kenhome-safety` | Same URL on the new site: rebuilt from the old text |
| `/blog` | Same URL on the new site: rebuilt from the old text |
| `/blogs/generative-ai-rewriting-business` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-video-surveillance` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-changing-how-we-work` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-across-every-sector` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-digital-billboards` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-construction-safety` | Same URL on the new site: rebuilt from the old text |
| `/blogs/ai-smart-buildings` | Same URL on the new site: rebuilt from the old text |
| `/about` | Same URL on the new site: About |
| `/contact` | Same URL on the new site: Contact |
| `/faq` | Same URL on the new site: rebuilt from the old text |
| `/privacy` | Same URL on the new site: rebuilt from the old text |
| `/terms` | Same URL on the new site: rebuilt from the old text |
| `/llms/index.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/kenvision.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/kensafety.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/kenhome.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/kenagri.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/keniot.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/kenrobotics.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/ken360.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/retail-analytics.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/about.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/casestudies.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/faq.md` | Same file, copied from the old site (site/content/llms/) |
| `/llms/contact.md` | Same file, copied from the old site (site/content/llms/) |

New pages with no old equivalent: `/modules`, `/industries`. The old site also served `/kenvoice` and `/index` (neither in its sitemap): `/kenvoice` is a page on the new site and `/index` is a 301 to `/`. `/llms.txt` is copied too.

## Deployable build

```
python3 site/build.py --deploy dist
```

writes `dist/` with clean URLs (`/kenvision`, `/ken360` ...), root-relative assets, `sitemap.xml` and `robots.txt`.
Every page has a canonical tag to `https://www.intelense.com/<path>`, Open Graph and Twitter tags, and the home page has Organization data with the LinkedIn link.

## Before launch

1. The 5 redirect URLs need a real 301 on the host: `dist/.htaccess` (Apache) and `dist/_redirects` (Netlify / Cloudflare Pages) are generated; static fallback pages exist if the host cannot redirect.
2. Titles and meta keywords of the 10 existing pages come from `content/old-seo.json`; four descriptions are the old ones, the module-page descriptions are the new ones.
3. Connect the contact form (it is not connected to email yet).
4. After launch: submit `sitemap.xml` in Google Search Console, check the old URLs with the URL Inspection tool and watch Coverage and Performance for two to four weeks.
