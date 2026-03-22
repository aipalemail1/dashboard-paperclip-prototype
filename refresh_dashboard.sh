#!/usr/bin/env bash
set -euo pipefail
python3 /Users/aipal/.openclaw/workspace/dashboard-paperclip-prototype/generate_dashboard.py >> /tmp/openclaw/dashboard-refresh.log 2>&1
