# BugSense — Intelligent Bug Diagnosis Platform (Frontend)

Frontend-only prototype for the internship project **"Creation of Intelligent
Bug Diagnosis Platform with Fix Recommendation Assistance."**

No backend, no build step — plain HTML5, CSS3, and vanilla JavaScript with
Bootstrap 5 and Bootstrap Icons via CDN.

## Folder structure

```
bug-diagnosis-platform/
├── index.html               # Login / Register page
├── dashboard.html            # Dashboard (main page after login)
├── bug-analyzer.html          # Bug Analyzer (submit a bug for diagnosis)
├── analysis-result.html        # Analysis Result (AI diagnosis + fix recommendation)
├── history.html                 # Bug History (search, filter, browse past bugs)
├── knowledge-base.html           # Knowledge Base (search historical defects & resolutions)
├── css/
│   ├── style.css                   # Shared design tokens + Login/Register styles
│   ├── dashboard.css                # Dashboard-only layout & components (reused by other pages' shell)
│   ├── bug-analyzer.css             # Bug Analyzer-only styles (form, upload, simulation overlay)
│   ├── analysis-result.css          # Analysis Result-only styles (summary grid, agent results, code blocks)
│   ├── history.css                  # Bug History-only styles (search, filters, pagination, modal)
│   └── knowledge-base.css           # Knowledge Base-only styles, scoped to kb-* classes only
├── js/
│   ├── login.js                     # Login/Register interactivity (dummy logic only)
│   ├── dashboard.js                  # Sidebar/topbar behavior, shared by every dashboard-shell page
│   ├── bug-analyzer.js               # Bug Analyzer interactivity (dummy logic only)
│   ├── analysis-result.js            # Analysis Result interactivity (dummy logic only)
│   ├── history.js                    # Bug History interactivity: local demo dataset, search, filters,
│   │                                    pagination, and details modal (dummy logic only)
│   └── knowledge-base.js             # Knowledge Base interactivity: local demo dataset, search, filters,
│                                        pagination, details modal, recently-added list (dummy logic only)
├── assets/                    # Reserved for images/icons used across the app
├── pages/                      # Reserved for future pages:
│                                  profile.html
└── README.md
```

## Running it

No server or build tools required. Just open `index.html` in a browser,
or serve the folder with any static server, e.g.:

```bash
python3 -m http.server 8000
```

then visit `http://localhost:8000`.

## What's implemented (Login/Register page)

- Split layout: branded diagnostic-console visual on the left, auth forms on the right
- Segmented **Log In / Create Account** switcher (no page reload)
- Login form: email, password, "remember me", "forgot password" link
- Register form: full name, email, password + confirm password, password
  strength indicator, terms checkbox
- Password visibility toggle (eye / eye-slash) on every password field
- Bootstrap 5 client-side validation (`novalidate` + custom checks), including
  password-match validation on register
- Toast notifications for simulated success states (no backend calls)
- Fully responsive: stacks to a single column below the `lg` breakpoint

## What's implemented (Dashboard page)

- Fixed sidebar nav (Dashboard, Bug Analyzer, Bug History, Knowledge Base,
  Profile, Logout) with an active state on the current page, collapsing into
  a slide-in mobile menu below `lg`
- Top header with page title, notification dropdown, and profile dropdown
  (both plain Bootstrap dropdowns, no backend)
- Welcome banner with "+ Analyze New Bug" CTA linking to `bug-analyzer.html`
- 4 summary stat cards (Total / Open / Resolved / Critical bugs) with trend indicators
- Recent Bug Analyses table with severity badges, status badges, and a
  "View" action linking to `analysis-result.html`
- Bug Severity Overview and Bug Category Overview using CSS bar visualizations
  (no chart library)
- 5-stage Analysis Pipeline preview (Triage → Log Analysis → Root Cause →
  Duplicate Detection → Remediation), all shown as "Ready"
- Historical Knowledge Base summary stats
- Recent Activity timeline
- A visible disclaimer that all dashboard numbers are sample/demo data

All data on this page is hardcoded dummy data — no API calls, no backend, no
real authentication or session state.

## What's implemented (Bug Analyzer page)

- Same sidebar/topbar shell as the Dashboard (reuses `css/dashboard.css` and
  `js/dashboard.js` directly — no duplicated shell code), with "Bug Analyzer"
  marked active in the nav
- Bug Submission form: title, language dropdown, description, error message,
  stack trace and source code (monospace code-style textareas)
- File upload with click-to-browse, drag & drop, extension allow-list
  (`.log .txt .java .py .js .ts .cpp .c .cs .php`), a 10 MB size limit,
  filename/size preview, and a remove button — nothing is ever actually
  uploaded anywhere
- Client-side validation: title and language are required; at least one of
  description / error message / stack trace / source code / uploaded file
  must be present, otherwise a validation banner appears
- Analysis Options checkboxes (all checked by default)
- Analysis Pipeline preview (Triage → Log Analysis → Root Cause → Duplicate
  Detection → Remediation) with a one-line description per agent
- Clear button resets the entire form, including the uploaded file and
  validation state
- Analyze Bug button runs a timed frontend-only simulation (an overlay that
  steps each of the five agents from Waiting → Running → Ready), then
  redirects to `analysis-result.html` (not implemented yet — the link is
  wired up for the next phase)
- Fully responsive: sidebar collapses on mobile (shared behavior with the
  Dashboard), form fields and analysis options stack on small screens

All form data, the pipeline animation, and the "analysis" are dummy/frontend
only — nothing is sent to a server, and no real diagnosis takes place.

## What's implemented (Analysis Result page)

- Same sidebar/topbar shell as Dashboard and Bug Analyzer (reuses
  `css/dashboard.css` and `js/dashboard.js` — no duplicated shell code)
- Status strip with the bug ID and a clear "Analysis Complete" success badge,
  plus an Export Report button
- Bug Summary card: ID, title, language, category, severity/status badges,
  priority, submitted date
- Agent Analysis section showing all 5 agents as "Completed" with a short
  demo result each
- Severity Assessment and Failure Point cards side by side, including a
  monospace code snippet showing the failing line
- Probable Root Cause section with a confidence bar (91%)
- Similar Historical Bugs table (3 demo rows) with similarity bars, status
  badges, and View links, plus a collapsible "Why were these bugs considered
  similar?" explanation
- Recommended Fix section with Before/After code blocks, a working **Copy
  Fix** button (copies the "After" snippet to the clipboard via
  `navigator.clipboard`, with a textarea fallback), a View Details button,
  and a "Why this recommendation?" reasoning list
- Analysis Confidence summary with 3 progress bars (Root Cause, Duplicate
  Detection, Fix Recommendation)
- Resolution actions: **Mark as Resolved** (shows a toast and flips the
  status badge to "Resolved" client-side), **Re-analyze** and **Back to Bug
  Analyzer** (both return to `bug-analyzer.html`)
- A visible disclaimer that all results, confidence scores, and historical
  matches are sample/demo data
- Fully responsive: summary grid, severity/failure-point panels, and the
  before/after fix diff all stack on smaller screens; code blocks scroll
  horizontally instead of overflowing the page

All data on this page — the bug details, agent results, root cause,
confidence scores, and historical matches — is hardcoded demo data. No
backend call, database write, real AI processing, or semantic search is
performed anywhere on this page.

## What's implemented (Bug History page)

- Same sidebar/topbar shell as the rest of BugSense (reuses `css/dashboard.css`
  and `js/dashboard.js`), with "Bug History" marked active in the nav
- "+ Analyze New Bug" action linking to `bug-analyzer.html`
- 4 summary stat cards (Total / Open / Resolved / Critical), same style as
  the Dashboard
- A local demo dataset of **15 bug records** (`js/history.js`) covering every
  severity, every status (Open / Analyzing / Resolved), and all listed
  categories and languages
- Live search across Bug ID, title, category, error message, and language
- Four filters (Severity, Status, Category, Language) plus **Clear Filters**,
  all working against the local dataset
- Dynamic result count ("Showing X-Y of N bugs") that updates as you search
  or filter
- A responsive table (Bug ID, Title, Category, Language, Severity, Status,
  Date, Action) with consistent severity/status badges
- Frontend pagination (8 records per page) with Previous / page numbers / Next
- A clean empty state ("No bugs found") with its own Clear Filters button
  when nothing matches
- A Bug Details modal — click a row or its Details button to see the bug's
  description and error message, with a "View Full Analysis" button to
  `analysis-result.html`
- "View Analysis" per row, linking to `analysis-result.html`
- Recently Resolved list (4 bugs) and a Historical Knowledge panel linking to
  `knowledge-base.html`
- Fully responsive: filters stack on tablet/mobile, table scrolls
  horizontally instead of overflowing, pagination wraps on narrow screens

All bug records, statistics, and the search/filter/pagination behavior run
entirely against the local `DEMO_BUGS` array in `js/history.js` — there is no
API call, database, or real search index anywhere on this page.

## What's implemented (Knowledge Base page)

- **Sidebar and topbar reused byte-for-byte** from the other pages — same
  flat nav list (no group headers, no extra items), "Knowledge Base" marked
  active. A "+ Analyze New Bug" button was added to the topbar per this
  page's spec, using the existing `.btn-accent` style with a small
  page-scoped sizing tweak (`.kb-topbar-cta`) so it fits the topbar row —
  the shared topbar CSS itself was not touched
- Intro panel ("Learn from previously resolved bugs") and 4 statistic cards
  (Knowledge Entries / Resolved Bugs / Root Causes / Fix Recommendations),
  using the same stat-card style as the Dashboard
- A local demo dataset of **15 knowledge records** (`js/knowledge-base.js`)
  spanning all listed categories, languages, severities, and sources
- Live search across Knowledge ID, Bug ID, title, root cause, resolution,
  and error message
- Four filters (Category, Language, Severity, Source) plus **Clear Filters**
- Dynamic result count, frontend pagination (8 per page), and a clean empty
  state, all matching the Bug History page's pattern
- Historical Knowledge table (dark themed, matching `.dash-table` used
  elsewhere) with a relevance bar per row
- A Knowledge Details modal — Knowledge ID, status, title, Bug ID, category,
  language, severity, source, error, root cause, resolution, and why it's
  relevant — with an **Analyze Similar Bug** button that shows a toast and
  redirects to `bug-analyzer.html`
- Recently Added Knowledge list (4 most recent entries)
- A RAG information panel explaining the future retrieval pipeline, with an
  "Analyze a Bug" call-to-action
- A visible disclaimer that all records and statistics are sample/demo data
- Fully responsive: filters and stat cards stack on tablet/mobile, the table
  scrolls horizontally, and the RAG panel stacks under its button

**A note on scope:** the request described a sidebar with grouped section
headers (OVERVIEW / DIAGNOSIS / ACCOUNT) and a separate "Settings" nav item.
The existing BugSense sidebar has neither — it's a flat list, and Settings
already lives inside the Profile dropdown. Since the same request also said
not to redesign the sidebar and to keep it identical to the other pages, the
existing flat sidebar was reused exactly as-is rather than introducing new
grouping or nav items that don't exist anywhere else in the app. Happy to
add section grouping across all pages together if you'd like that as a
deliberate design change.

All records, statistics, and the search/filter/pagination behavior run
entirely against the local `DEMO_KNOWLEDGE` array in `js/knowledge-base.js`
— there is no API call, database, or real RAG/semantic search anywhere on
this page.

## Next steps (future pages, not built yet)

1. Profile / Settings
