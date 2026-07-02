# Add a page

This walkthrough takes about **5 minutes**. You only need a GitHub account — no software to install, no command line.

---

## Before you start

Decide on a **slug** for your page. This becomes the URL path and the folder name in the repository. Keep it short, lowercase, and use hyphens instead of spaces.

| Good slugs | Bad slugs |
|---|---|
| `egu-2026` | `EGU 2026` |
| `agu-2025-poster` | `my poster (AGU)` |
| `city2tabula-demo` | `City2Tabula_Demo` |

Your page will be live at:
```
https://thd-spatial-ai.github.io/<repo-name>/<your-slug>/
```

---

## Step 1 — Open the repository on GitHub

Go to the repository page on GitHub. Make sure you are signed in.

---

## Step 2 — Create a new folder and config file

1. Click **Add file** → **Create new file** (top-right area of the file list).
2. In the filename box, type `events/`, your slug, a forward slash, and `page.json`:

    ```
    events/egu-2027/page.json
    ```

    GitHub automatically creates the folder when you type the `/`.

3. In the large text area below, paste the template content from `events/_template/page.json`:

```json
{
  "event": "Conference Name Year",
  "title": "Project Title",
  "subtitle": "One sentence describing what this project is about.",
  "links": [
    {
      "category": "Category Label",
      "title": "Link Title",
      "url": "https://example.com",
      "description": "One sentence describing what this link leads to.",
      "icon": "globe"
    },
    {
      "category": "Source Code",
      "title": "Repository Name",
      "url": "https://github.com/example/repo",
      "description": "Source code and documentation.",
      "icon": "github"
    }
  ],
  "institutions": [
    {
      "name": "Department or Institute Name",
      "unit": "University or Organisation"
    }
  ]
}
```

---

## Step 3 — Fill in your details

Replace every placeholder value (the text in `"quotes"`) with your own content. Do **not** change the field names (the words to the left of the colon).

??? tip "What each field means"
    See the full [Config reference](config-reference.md) for a description of every field and the list of available icons.

A filled-in example:

```json
{
  "event": "EGU General Assembly 2027",
  "title": "My Project",
  "subtitle": "A short description of what this research is about.",
  "links": [
    {
      "category": "Web App",
      "title": "Open the tool",
      "url": "https://my-tool.th-deg.de/",
      "description": "Interactive tool for exploring the results.",
      "icon": "globe"
    },
    {
      "category": "Source Code",
      "title": "GitHub Repository",
      "url": "https://github.com/THD-Spatial-AI/my-project",
      "description": "All source code and documentation.",
      "icon": "github"
    }
  ],
  "institutions": [
    {
      "name": "Faculty of Applied Informatics",
      "unit": "Technische Hochschule Deggendorf (THD)"
    }
  ]
}
```

---

## Step 4 — Save the file

Scroll to the bottom of the page. You will see a **Commit changes** panel.

1. Leave the commit message as-is, or write a short description like `add egu-2027 page`.
2. Make sure **Commit directly to the `main` branch** is selected.
3. Click **Commit changes**.

---

## Step 5 — Wait for the build

GitHub now automatically builds and publishes your page. This takes about **60 seconds**.

To watch the progress:

1. Click the **Actions** tab at the top of the repository.
2. You will see a workflow run called **Build and Deploy** in progress (yellow circle).
3. Once it turns green (✓), your page is live.

---

## Step 6 — Check your page

Open your page in a browser:

```
https://thd-spatial-ai.github.io/<repo-name>/<your-slug>/
```

The hub page at the root also updates automatically and now includes a card for your new page.

---

## Updating a page later

To change text, add a link, or fix a typo:

1. Navigate to `events/<your-slug>/page.json` in the repository.
2. Click the pencil icon (✏️) to edit.
3. Make your changes.
4. Commit — the page rebuilds in about 60 seconds.

---

## One-time setup (repo owner only)

!!! warning "This step is required once before the first page goes live."

The repository owner must configure GitHub Pages to use the **GitHub Actions** deployment source:

1. Go to the repository → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Click **Save**.

This only needs to be done once. After that, every push to `main` triggers an automatic rebuild.
