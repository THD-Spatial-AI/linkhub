# THD Spatial AI — Link Hub

This repository lets anyone in the group publish a **permanent landing page** for a conference poster, workshop, or project — directly from GitHub, with no coding required.

Each page is a clean card-based link list (navy and amber, mobile-friendly, dark-mode-aware) that lives at a stable URL. Once you create it, the URL never changes, so it is safe to print as a QR code on a poster or include in a paper.

---

## What you can publish

| Use case | Example |
|---|---|
| Conference poster | EGU 2026, AGU 2025, IGARSS |
| Workshop or tutorial | Links to notebooks, slides, data |
| Project page | GitHub repos, app, dataset, preprint |

---

## How it works

You fill in a small text file called `page.json` with your event name, links, and descriptions. GitHub takes care of everything else automatically.

```
You edit page.json  →  push to GitHub  →  page is live within ~60 seconds
```

Your page appears at:

```
https://thd-spatial-ai.github.io/<repo-name>/<your-slug>/
```

For example, the EGU 2026 page lives at `.../egu-2026/` (its `page.json` source lives in `events/egu-2026/`).

The hub page at the repo root lists all published pages automatically.

---

## Next steps

- **[Add a page →](add-a-page.md)** — step-by-step walkthrough (no coding, no installs)
- **[Config reference →](config-reference.md)** — every field in `page.json` explained
