#!/usr/bin/env python3
import csv
import datetime as dt
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path('/Users/aipal/.openclaw/workspace/dashboard-paperclip-prototype')
METRICS = pathlib.Path('/Users/aipal/.openclaw/workspace/metrics/daily-brief-metrics.csv')
PROJECT = ROOT / 'project_status.json'
MISSION = ROOT / 'mission.json'
TODO = ROOT / 'todo.json'
OUT = ROOT / 'live.html'


def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except Exception as e:
        return f"ERROR: {e}"


def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


status = run(['openclaw', 'status', '--deep'])
ps_top = run(['/bin/zsh', '-lc', "ps -Ao pid,pcpu,pmem,comm | sort -k2 -nr | head -n 8"])

# Basic parses
version = re.search(r'OpenClaw\s+([0-9.]+)', status)
gateway_ms = re.search(r'Gateway\s+\|\s+reachable\s+\|\s+([0-9]+)ms', status)
discord_ms = re.search(r'Discord\s+\|\s+OK\s+\|\s+ok \([^:]+:([0-9]+)ms\)', status)
telegram_ms = re.search(r'Telegram\s+\|\s+OK\s+\|\s+ok \([^:]+:([0-9]+)ms\)', status)

ver = version.group(1) if version else 'unknown'
gw = gateway_ms.group(1) if gateway_ms else 'n/a'
dc = discord_ms.group(1) if discord_ms else 'n/a'
tg = telegram_ms.group(1) if telegram_ms else 'n/a'

# Metrics last row
last = {}
if METRICS.exists():
    with METRICS.open() as f:
        rows = list(csv.DictReader(f))
        if rows:
            last = rows[-1]


def v(k, d='NA'):
    return last.get(k, d)


def bar_width(val):
    try:
        x = float(val)
        if x < 0:
            x = 0
        if x > 100:
            x = 100
        return f"{x:.0f}%"
    except Exception:
        return "0%"


oauth5 = v('oauth_5h_used_pct')
oauth_day = v('oauth_day_used_pct')
ram = v('ram_used_pct')
disk = v('disk_used_pct')
backup = v('backup_health')
web_used = v('web_budget_used_usd')
web_left = v('web_budget_remaining_usd')

proj = load_json(PROJECT, {"backlog": [], "in_progress": [], "waiting_approval": [], "done": []})
mission = load_json(MISSION, {"mission": "Mission not set", "goals": []})
todos = load_json(TODO, {"items": []})


def render_tickets(items):
    out = []
    for it in items:
        title = html.escape(str(it.get('title', 'Untitled')))
        owner = html.escape(str(it.get('owner', 'Unassigned')))
        pri = html.escape(str(it.get('priority', 'P?')))
        due = html.escape(str(it.get('due', 'TBD')))
        out.append(f'<div class="ticket"><b>{title}</b><small>Owner: {owner} • {pri} • Due: {due}</small></div>')
    return "\n".join(out) if out else '<div class="ticket"><small>No items</small></div>'


def render_mission(goals):
    blocks = []
    idx = 2
    for g in goals:
        title = html.escape(str(g.get('title', 'Goal')))
        blocks.append(f'<div class="node n{idx}"><b>{title}</b></div>')
        for t in g.get('tasks', []):
            idx += 1
            if idx > 7:
                idx = 7
            blocks.append(f'<div class="node n{idx}">{html.escape(str(t))}</div>')
        idx += 1
    return "\n".join(blocks)


def render_todos(items):
    if not items:
        return '<li><label><input type="checkbox" disabled> <span>No todos</span></label></li>'
    out = []
    for item in items:
        tid = html.escape(str(item.get('id', 'todo')))
        txt = html.escape(str(item.get('text', 'Untitled task')))
        checked = 'checked' if item.get('done') else ''
        out.append(
            f'<li><label><input class="todo-check" type="checkbox" data-todo-id="{tid}" {checked}> '
            f'<span>{txt}</span></label></li>'
        )
    return "\n".join(out)


now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

html_out = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Command Deck — Live</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <header class="topbar">
    <div>
      <h1>Command Deck (Live)</h1>
      <p class="sub">Updated {now} • OpenClaw {ver}</p>
    </div>
    <div class="pill ok">Ship Status: GREEN</div>
  </header>

  <nav class="tabs" role="tablist" aria-label="Dashboard tabs">
    <button class="tab active" data-tab="current" role="tab" aria-selected="true">Current View</button>
    <button class="tab" data-tab="project" role="tab" aria-selected="false">Project Status</button>
    <button class="tab" data-tab="mission" role="tab" aria-selected="false">Mission</button>
  </nav>

  <main id="tab-current" class="grid tabpane active" role="tabpanel">
    <section class="card mission">
      <h2>Live Health</h2>
      <p>Gateway latency: <b>{gw}ms</b> • Discord latency: <b>{dc}ms</b> • Telegram latency: <b>{tg}ms</b></p>
      <div class="kpis">
        <div><span>Backup Health</span><strong>{html.escape(str(backup))}</strong></div>
        <div><span>RAM Used</span><strong>{html.escape(str(ram))}%</strong></div>
        <div><span>Disk Used</span><strong>{html.escape(str(disk))}%</strong></div>
      </div>
    </section>

    <section class="card budget">
      <h2>Budget Guardrails</h2>
      <div class="metric">
        <label>OAuth (5h used)</label>
        <div class="bar"><i style="width:{bar_width(oauth5)}"></i></div>
        <small>{html.escape(str(oauth5))}%</small>
      </div>
      <div class="metric">
        <label>OAuth (day used)</label>
        <div class="bar"><i style="width:{bar_width(oauth_day)}"></i></div>
        <small>{html.escape(str(oauth_day))}%</small>
      </div>
      <div class="metric">
        <label>Web budget ($5 cap)</label>
        <small>Used: ${html.escape(str(web_used))} • Left: ${html.escape(str(web_left))}</small>
      </div>
    </section>

    <section class="card tasks" style="grid-column:span 8">
      <h2>Top CPU Processes</h2>
      <pre style="white-space:pre-wrap;color:#b9c7ef;font-size:.8rem;max-height:240px;overflow:auto">{html.escape(ps_top)}</pre>
    </section>

    <section class="card todo" style="grid-column:span 4">
      <h2>To‑Do (For Kevin)</h2>
      <ul class="todo-list">
        {render_todos(todos.get('items', []))}
      </ul>
      <small>Checks are saved in your browser for this page.</small>
    </section>
  </main>

  <main id="tab-project" class="grid tabpane" role="tabpanel" aria-hidden="true">
    <section class="card" style="grid-column: span 12;">
      <h2>Project Status Board (Live JSON)</h2>
      <div class="kanban">
        <div class="lane"><h3>Backlog</h3>{render_tickets(proj.get('backlog', []))}</div>
        <div class="lane"><h3>In Progress</h3>{render_tickets(proj.get('in_progress', []))}</div>
        <div class="lane"><h3>Waiting Approval</h3>{render_tickets(proj.get('waiting_approval', []))}</div>
        <div class="lane"><h3>Done</h3>{render_tickets(proj.get('done', []))}</div>
      </div>
    </section>
  </main>

  <main id="tab-mission" class="grid tabpane" role="tabpanel" aria-hidden="true">
    <section class="card" style="grid-column: span 12;">
      <h2>Mission Alignment (Live JSON)</h2>
      <div class="mission-tree">
        <div class="node n1"><b>Mission:</b> {html.escape(str(mission.get('mission', 'Mission not set')))}</div>
        {render_mission(mission.get('goals', []))}
      </div>
    </section>
  </main>

  <script src="./app.js"></script>
</body>
</html>'''

OUT.write_text(html_out)
print(f'Wrote {OUT}')
