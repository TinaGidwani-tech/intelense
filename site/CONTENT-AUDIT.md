# Content audit of the new site (29 pages), 22 Oct 2026

Method: scripted pass over every built page (titles, descriptions, headings, images, links, word counts, spelling, contact details, numeric claims) plus a manual check of every flagged item. Items that turned out to be artefacts of text extraction (repeated "Industries Industries", " ," in lists, "Contact Contact") are not listed.

## Needs a decision
| # | Finding | Where | Suggested action |
|---|---|---|---|
| 1 | **No analytics on the new site.** The old site loaded Google Analytics 4 (`G-RT2SKBL5HE`) and the Apollo.io tracker. Neither is on the new pages, so visits and form leads are not measured after launch. | all pages | Add GA4 (and Apollo if still used). The privacy policy already mentions optional analytics cookies; consider a consent banner. |
| 2 | **"Six modules, one platform."** conflicts with "seven modules" everywhere else. (Old blog text, copied verbatim.) The `/llms/*.md` files also say six. | `/blogs/ai-across-every-sector`, `content/llms/` | Change to seven (needs approval because the blog text is verbatim old copy). |
| 3 | **Legal pages give a Toronto address** ("Intelense Inc., Toronto, Ontario") while the office is Markham. Old text copied exactly. Mailboxes `privacy@intelense.ca` and `legal@intelense.ca` should be confirmed to exist. | `/privacy`, `/terms` | Owner or counsel to confirm the address and mailboxes. |
| 4 | **Spelling is mixed.** Site is about 90% British (111 vs 14 US forms). US forms: "analyzing", "behavior" on `/faq` and `/retail-analytics`. | `/faq`, `/retail-analytics` | Pick one (British, or Canadian) and align. |
| 5 | **Marketing numbers need substantiation.** Old claims carried over: 95% footfall accuracy (4 pages), 40% (6 pages), 80% fewer incidents, 70% to 95% compliance, 28% conversion lift, 99.9% uptime (terms). Dashboard figures on module pages are example data and labelled as such. | product, case-study, blog pages | Owner to confirm each claim can be backed up. |

## Minor / optional
- **Long titles and descriptions** (Google truncates near 60 / 155 characters). Home description is 358 characters; blog and case-study titles 76 to 94. Kept as on the old site for ranking continuity. Tighten later, once rankings are stable.
- **Heading order** skips a level (h1 to h3) on `/blog`, `/casestudies`, `/modules`, `/kenIoT`, one blog post.
- **Thin pages** (under 350 words): five blog posts (about 300), `/contact` (253), `/casestudies` (229), `/faq` (318). Opportunity to add content.
- **Style:** 53 em dashes, mostly in the old blog posts.

## Checked and fine
Titles and descriptions unique; one H1 per page; every image has alt text; no empty links; phone numbers, emails and city spelling consistent (one "Bangalore" remains, quoted from the ISO certificate); no placeholder text or encoding errors.
