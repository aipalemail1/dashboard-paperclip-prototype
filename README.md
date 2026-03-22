# Command Deck (Paperclip-style)

## Quick start

Generate a live snapshot page:

```bash
python3 /Users/aipal/.openclaw/workspace/dashboard-paperclip-prototype/generate_dashboard.py
open /Users/aipal/.openclaw/workspace/dashboard-paperclip-prototype/live.html
```

## Optional: auto-refresh every 5 minutes

```bash
while true; do
  python3 /Users/aipal/.openclaw/workspace/dashboard-paperclip-prototype/generate_dashboard.py
  sleep 300
done
```

This creates a local-first dashboard snapshot that pulls from:
- `openclaw status --deep`
- `metrics/daily-brief-metrics.csv`
