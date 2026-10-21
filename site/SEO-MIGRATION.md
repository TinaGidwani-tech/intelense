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
| `/retail-analytics` | **No equivalent page yet** |
| `/video-analytics-retail` | **No equivalent page yet** |
| `/footfall-analytics` | **No equivalent page yet** |
| `/queue-analytics` | **No equivalent page yet** |
| `/heatmap-analytics` | **No equivalent page yet** |
| `/cctv-analytics-retail` | **No equivalent page yet** |
| `/casestudies` | **No equivalent page yet** |
| `/kensafety-construction` | **No equivalent page yet** |
| `/kenvision-retail` | **No equivalent page yet** |
| `/kenhome-safety` | **No equivalent page yet** |
| `/blog` | **No equivalent page yet** |
| `/blogs/generative-ai-rewriting-business` | **No equivalent page yet** |
| `/blogs/ai-video-surveillance` | **No equivalent page yet** |
| `/blogs/ai-changing-how-we-work` | **No equivalent page yet** |
| `/blogs/ai-across-every-sector` | **No equivalent page yet** |
| `/blogs/ai-digital-billboards` | **No equivalent page yet** |
| `/blogs/ai-construction-safety` | **No equivalent page yet** |
| `/blogs/ai-smart-buildings` | **No equivalent page yet** |
| `/about` | Same URL on the new site: About |
| `/contact` | Same URL on the new site: Contact |
| `/faq` | **No equivalent page yet** |
| `/privacy` | **No equivalent page yet** |
| `/terms` | **No equivalent page yet** |
| `/llms/index.md` | **No equivalent page yet** |
| `/llms/kenvision.md` | **No equivalent page yet** |
| `/llms/kensafety.md` | **No equivalent page yet** |
| `/llms/kenhome.md` | **No equivalent page yet** |
| `/llms/kenagri.md` | **No equivalent page yet** |
| `/llms/keniot.md` | **No equivalent page yet** |
| `/llms/kenrobotics.md` | **No equivalent page yet** |
| `/llms/ken360.md` | **No equivalent page yet** |
| `/llms/retail-analytics.md` | **No equivalent page yet** |
| `/llms/about.md` | **No equivalent page yet** |
| `/llms/casestudies.md` | **No equivalent page yet** |
| `/llms/faq.md` | **No equivalent page yet** |
| `/llms/contact.md` | **No equivalent page yet** |

New pages with no old equivalent: `/modules`, `/industries`, `/kenvoice`.

## Deployable build

```
python3 site/build.py --deploy dist
```

writes `dist/` with clean URLs (`/kenvision`, `/ken360` ...), root-relative assets, `sitemap.xml` and `robots.txt`.
Every page has a canonical tag to `https://www.intelense.com/<path>`, Open Graph and Twitter tags, and the home page has Organization data with the LinkedIn link.

## Before launch

1. Decide what happens to each old URL marked "No equivalent page yet" (rebuild the page, keep it running on the old host, or 301 to the closest new page).
2. Compare the old titles, meta descriptions, H1s and keywords with the new ones and carry over the ones that rank.
3. Connect the contact form (it is not connected to email yet).
4. After launch: submit `sitemap.xml` in Google Search Console, check the old URLs with the URL Inspection tool and watch Coverage and Performance for two to four weeks.
