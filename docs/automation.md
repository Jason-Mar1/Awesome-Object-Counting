# Paper Automation Guide

This repository uses a compliant scholarly-search workflow instead of scraping Google Scholar.

## What it does

- Queries arXiv and OpenAlex for recent object-counting papers.
- Focuses on few-shot, zero-shot, class-agnostic, open-vocabulary, text-guided and multimodal object counting.
- Deduplicates records by DOI, arXiv ID and normalized title.
- Writes machine-readable data to `data/papers.json` and `data/papers.csv`.
- Writes a readable digest to `data/paper_digest.md`.
- Updates the auto-generated README section between:

```md
<!-- AUTO_PAPERS:START -->
<!-- AUTO_PAPERS:END -->
```

## Local usage

```bash
python scripts/fetch_papers.py --dry-run
python scripts/fetch_papers.py
```

## GitHub Actions usage

The workflow file is located at:

```text
.github/workflows/update_papers.yml
```

It runs daily and can also be triggered manually from the Actions tab.

## OpenAlex API key

Do **not** commit the OpenAlex key into this public repository.

Add it as a repository secret named:

```text
OPENALEX_API_KEY
```

Path:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

The secret can be either the raw OpenAlex key or the full URL format returned by OpenAlex, for example `https://api.openalex.org/works?api_key=...`. The script extracts the `api_key` value and masks it in dry-run output.

## Change the search scope

Edit:

```text
config/search_config.json
```

Useful keywords for this repository:

- few-shot object counting
- zero-shot object counting
- class-agnostic object counting
- open-vocabulary object counting
- text-guided object counting
- multimodal object counting
- FSC-147
- CLIP-Count
- CountGD

## Why not Google Scholar scraping?

Google Scholar is useful for manual search, but automated scraping is unstable and commonly blocked by CAPTCHA/rate limits. This workflow uses arXiv and OpenAlex because they are designed for programmatic access.
