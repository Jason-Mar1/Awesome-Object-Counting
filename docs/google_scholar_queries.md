# Manual Google Scholar Search Strings

The automation does not scrape Google Scholar. Use these strings manually in Google Scholar when you want to check whether API search missed something.

```text
"few-shot object counting" OR "class-agnostic counting" OR "FSC-147"
```

```text
"zero-shot object counting" OR "text-guided object counting" OR "CLIP-Count"
```

```text
"open-vocabulary object counting" OR "multimodal object counting" OR "CountGD"
```

```text
"referring expression counting" OR "generic visual counting" OR "visual counting benchmark"
```

Suggested workflow:

1. Search one string at a time.
2. Sort by date.
3. Open papers that look directly related to object counting.
4. Add missing important papers manually to the relevant README section or extend `config/search_config.json` so the automation can find similar papers later.
