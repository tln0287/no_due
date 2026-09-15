# LRIRMS — dashboard_template

A standalone, static HTML export of every page in the LRIRMS app, pre-filled with the
project's demo data. No Django, no build step, no CDN — everything it needs ships inside
this folder.

## Open it

Because the pages fetch local assets by relative path, open them through a static server
rather than double-clicking the file (double-clicking usually still works in modern
browsers, but a server avoids any `file://` quirks):

```bash
cd dashboard_template
python -m http.server 8099
# then open http://127.0.0.1:8099/login.html
```

Any static host (Netlify, Vercel, S3, GitHub Pages, nginx) works the same way — just
upload the whole `dashboard_template` folder.

## What's in here

- **17 pages**, one per app screen: `login`, `dashboard`, `tickets-list`, `ticket-detail`,
  `ticket-form`, `kanban`, `users-list`, `user-form`, `categories-list`, `category-form`,
  `routing-rules-list`, `routing-rule-form`, `sla-config-list`, `sla-config-form`,
  `notifications`, `reports`, `profile`.
- **`assets/`** — every CSS/JS library vendored locally: Bootstrap 5.3.3 (+ Icons),
  jQuery 3.7.1, jQuery UI 1.13.2, Select2, DataTables (+ Bootstrap 5 integration),
  ApexCharts, Quill, and the Inter font (all font files downloaded, no Google Fonts
  network request). Plus the project's own `theme.css` and `app.js`.
- Sidebar/topbar navigation between pages is fully wired — clicking "Tickets", "Kanban
  Board", a notification, a table row, etc. takes you to the matching local page.
- The dashboard's 4 ApexCharts (status/priority donuts, category bar, created-vs-resolved
  trend) render with real numbers — the JSON they'd normally fetch from the Django backend
  is baked directly into the page.
- Login redirects to the dashboard on submit, and "Logout" returns to the login page — a
  purely front-end simulation, no session behind it.

## What won't work (by design — there's no backend)

- Forms (create/edit ticket, user, category, routing rule, SLA rule, notes, attachments)
  don't submit anywhere real.
- Kanban drag-and-drop will visually move a card, but the change won't persist on reload.
- The two CSV report download links and any "mark as read" / assign / transition actions
  are inert.
- Every "view"/"edit" row link points at the *one* sample record captured at export time
  (ticket detail, user-form, category-form, etc.) — it's a template, not a live app.

This export was generated from a running instance of the full Django app in
`d:\ticketing2` — that app is where all the real functionality (auth, workflow engine,
SLA/escalation, notifications, the DRF API) actually lives.
