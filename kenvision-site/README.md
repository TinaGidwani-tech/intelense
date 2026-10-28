# kenvision.ai (revamp)

Same design language as www.intelense.com (shares `site/assets/site.css`, `site.js`, `cursor-grid.js`), Montserrat, brand blue #0A34ED, light and dark theme.

    python3 kenvision-site/tools/extract_old.py OLD_SITE_DIR   # old text -> content/pages.json (only needed again if the old site changes)
    python3 kenvision-site/build.py --deploy DIR               # site for the host (add --preview for relative links, --dark to build the light/dark toggle in)

Every demo button goes to the contact form, which emails enquiries@intelense.ca and dinesh@intelense.com (one email each). There is no booking-page link.
Backlinks to intelense.com: announcement bar, header, "Part of the Intelense platform" block, footer, contact and company pages, and JSON-LD (`publisher`, `parentOrganization`, `sameAs`).
