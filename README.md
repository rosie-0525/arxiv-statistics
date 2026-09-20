# arXiv Math Pulse

Trend dashboard of new arXiv submissions in every mathematics subject (math.AC … math.ST),
counted per day / week / month / quarter / year, with the release dates of major AI models
marked on the same axis.

Published copy: https://claude.ai/artifact/EYJC9MESJXBt21Dv8ozZXC

## Files

| File | What it is |
|---|---|
| `arxiv_math_pulse.html` | The finished, self-contained page (open it directly in a browser). |
| `template.html` | Page source: HTML, CSS and the charting JavaScript, with `__DATA__` / `__EVENTS__` placeholders. |
| `build.py` | Injects `data.json` and `events.json` into the template → `arxiv_math_pulse.html`. |
| `aggregate.py` | Turns the raw harvest in `data/` into `data.json` (daily counts per subject, primary and any-listing). |
| `harvest.py` | Downloads arXiv metadata via OAI-PMH (`set=math`, `metadataPrefix=arXiv`). |
| `events.json` | AI model release dates and context milestones drawn on the charts (`t`: 1 = major, 2 = other; `k`: model / context). |
| `data.json` | Aggregated daily counts, 2018-01-01 → last fully announced day. |
| `data/` (git-ignored) | Raw harvest, one JSON line per record: id, created date, categories. |

## Refreshing the data

```bash
# 1. Harvest (three date windows in parallel, ~25 min total; windows are by OAI datestamp)
python3 harvest.py 2018-01-01 2020-12-31 data/w1.jsonl &
python3 harvest.py 2021-01-01 2023-12-31 data/w2.jsonl &
python3 harvest.py 2024-01-01 $(date +%F) data/w3.jsonl &
wait

# 2. Aggregate and build
python3 aggregate.py     # writes data.json, prints per-year totals and the last complete day
python3 build.py         # writes arxiv_math_pulse.html
```

`harvest.py` appends to its output file and logs to `<out>.log`; delete the old files (or use a fresh
`from` date and merge) before a re-run. The OAI `from`/`until` parameters filter on last-modified
date, so old papers that were updated recently are also returned; `aggregate.py` keeps only papers
first submitted on or after 2018-01-01 and dates each one by its first version (`<created>`).

To add or edit a release marker, edit `events.json` and re-run `build.py`.

## Method notes

- A paper is counted under its **primary** category (first listed) or under **any** listed math
  category (cross-lists included); the page toggles between the two.
- Aliases are merged: math.MP = math-ph, math.IT = cs.IT, math.ST = stat.TH.
- The last few days of the harvest are not yet fully announced by arXiv, so `aggregate.py` trims
  to the last day whose count is in line with the previous four weeks. The page drops incomplete
  weeks, months, quarters and years instead of plotting a false dip.
- Daily counts dip on weekends because papers are dated by submission day, not announcement day.
