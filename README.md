# Sync Markdown to Confluence

This GitHub Action syncs Markdown files from your repo to a Confluence space.

## Inputs

| Name                  | Description                                  | Required |
|-----------------------|----------------------------------------------|----------|
| `CONFLUENCE_BASE_URL` | Base URL for Confluence instance             | Yes      |
| `EMAIL`               | Email used for Confluence authentication     | Yes      |
| `API_TOKEN`           | API token for your Confluence account        | Yes      |
| `SPACE_KEY`           | Confluence space key                         | Yes      |
| `DOCS_DIR`            | Path to your markdown docs (default: `docs`) | No       |

## Example Usage

```yaml
name Sync Docs

on:
  push:
    paths:
      - docs/**

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      
      - uses: actions/checkout@v4
      
      - uses: injectops/sync-markdown-to-confluence@v1
        with:
          CONFLUENCE_BASE_URL: https://your-org-name.atlassian.net/wiki
          EMAIL: ${{ secrets.CONFLUENCE_EMAIL }}
          API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
          SPACE_KEY: ${{ vars.CONFLUENCE_SPACE_KEY }}
          DOCS_DIR: DevDocs
```

