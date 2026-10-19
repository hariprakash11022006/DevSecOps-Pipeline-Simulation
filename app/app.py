from flask import Flask, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)

BUILD_NUMBER = os.environ.get("BUILD_NUMBER", "1")
DEPLOY_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CONTAINER_ID = socket.gethostname()
ADMIN_INITIALS = os.environ.get("ADMIN_INITIALS", "AC")
CLUSTER_REGION = os.environ.get("CLUSTER_REGION", "us-east-1 / prod-cluster-01")
BUILD_HASH = os.environ.get("BUILD_HASH", "8c7e2f1")

# Release notes shown in the notification bell for each build version.
BUILD_RELEASE_NOTES = {
    "1": [
        ("Initial secure release", "Baseline deployment with ClamAV integration wired into the pipeline gate."),
    ],
    "2": [
        ("Automated layer caching", "Docker layer caching enabled, plus new health check endpoints."),
    ],
    "3": [
        ("Zero-day signature matching", "Real-time byte-level signature scanning with full audit logging."),
    ],
    "4": [
        ("Hardened deployment gates", "Malware scanning now blocks unsigned artifacts before production rollout."),
        ("Fine-grained admin permissions", "Scoped roles for Super Admins, DevOps Engineers and Auditors."),
        ("Enclave-backed execution", "Verified workloads with hardware-isolated secrets and remote attestation."),
    ],
}
current_notes = BUILD_RELEASE_NOTES.get(
    str(BUILD_NUMBER),
    [("Enterprise security patches", "General vulnerability mitigation updates applied to this build.")],
)

ADMIN_USERS = [
    {"name": "Hari Prakash", "email": "hari@annuniv.edu", "role": "Super Admin", "mfa": True, "last_active": "Now", "live": True},
    {"name": "Sasikiran L", "email": "sasi@annuniv.edu", "role": "DevOps Engineer", "mfa": True, "last_active": "12m ago", "live": False},
    {"name": "Prof. Ganesh Kumar", "email": "ganesh@annuniv.edu", "role": "Auditor", "mfa": True, "last_active": "1h ago", "live": False},
]

ROLE_COLORS = {
    "Super Admin": "#38bdf8",
    "DevOps Engineer": "#a78bfa",
    "Auditor": "#fbbf24",
}


def render_admin_rows():
    rows = ""
    for u in ADMIN_USERS:
        color = ROLE_COLORS.get(u["role"], "#38bdf8")
        last_active = (
            f'<span class="status-live">{u["last_active"]}</span>'
            if u["live"]
            else f'<span style="color:#94a3b8;">{u["last_active"]}</span>'
        )
        rows += f"""
        <tr>
            <td>{u['name']}</td>
            <td style="color:#94a3b8;">{u['email']}</td>
            <td><span class="role-pill" style="background:rgba(56,189,248,0.12); color:{color}; border:1px solid {color}33;">{u['role']}</span></td>
            <td><span class="mfa-pill">{'✓ Enforced' if u['mfa'] else '— Not set'}</span></td>
            <td>{last_active}</td>
        </tr>"""
    return rows


def render_release_notes():
    items = ""
    for title, desc in current_notes:
        items += f"""
        <div class="notif-item">
            <div class="notif-item-icon">✓</div>
            <div>
                <div class="notif-item-title">{title}</div>
                <div class="notif-item-desc">{desc}</div>
            </div>
        </div>"""
    return items


@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CloudInfra Secure Admin Console — Build #{BUILD_NUMBER}</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: #090d16;
                color: #e2e8f0;
                margin: 0;
                padding: 0;
            }}
            a {{ color: inherit; }}
            .navbar {{
                background: #0d1220;
                border-bottom: 1px solid #1f2937;
                padding: 16px 32px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .navbar h2 {{ margin: 0; font-size: 1.1rem; color: #e2e8f0; display: flex; align-items: center; gap: 10px; font-weight: 600; }}
            .navbar h2 .badge-icon {{
                width: 30px; height: 30px; border-radius: 8px;
                background: linear-gradient(135deg, #38bdf8, #6366f1);
                display: flex; align-items: center; justify-content: center;
                font-size: 1rem;
            }}
            .nav-right {{ display: flex; align-items: center; gap: 22px; }}
            .nav-hostname {{ text-align: right; font-size: 0.72rem; color: #64748b; line-height: 1.3; }}
            .nav-hostname .label {{ text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.62rem; }}
            .nav-hostname code {{ color: #94a3b8; }}

            .notif-container {{ position: relative; cursor: pointer; }}
            .bell-icon {{
                font-size: 1.1rem; background: #151c2c; padding: 9px 11px; border-radius: 50%;
                border: 1px solid #263044; position: relative;
            }}
            .notif-badge {{
                position: absolute; top: -4px; right: -4px;
                background: #ef4444; color: white;
                font-size: 0.65rem; font-weight: bold;
                padding: 1px 6px; border-radius: 999px;
                border: 2px solid #0d1220;
            }}
            .notif-dropdown {{
                display: none; position: absolute; right: 0; top: 48px;
                width: 360px; background: #131a2b; border: 1px solid #263044;
                border-radius: 14px; box-shadow: 0 14px 34px rgba(0,0,0,0.55);
                z-index: 100; padding: 18px;
            }}
            .notif-dropdown.active {{ display: block; }}
            .notif-head {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }}
            .notif-head-title {{ font-weight: 700; color: #f8fafc; font-size: 0.95rem; }}
            .notif-head-sub {{ color: #64748b; font-size: 0.72rem; margin-top: 3px; }}
            .notif-latest-tag {{ background: rgba(56,189,248,0.15); color: #38bdf8; font-size: 0.62rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; letter-spacing: 0.04em; }}
            .notif-item {{ display: flex; gap: 10px; padding: 10px 0; border-top: 1px solid #1f2937; }}
            .notif-item:first-of-type {{ border-top: none; }}
            .notif-item-icon {{
                flex-shrink: 0; width: 20px; height: 20px; border-radius: 50%;
                background: rgba(74,222,128,0.15); color: #4ade80;
                display: flex; align-items: center; justify-content: center; font-size: 0.7rem;
            }}
            .notif-item-title {{ font-size: 0.85rem; font-weight: 600; color: #e2e8f0; }}
            .notif-item-desc {{ font-size: 0.78rem; color: #94a3b8; margin-top: 2px; line-height: 1.4; }}
            .notif-footer {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #1f2937; font-size: 0.78rem; }}
            .notif-footer a {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}

            .avatar {{
                width: 34px; height: 34px; border-radius: 50%;
                background: #1f2937; border: 1px solid #334155;
                display: flex; align-items: center; justify-content: center;
                font-size: 0.78rem; font-weight: 700; color: #cbd5e1;
            }}

            .main-content {{ max-width: 1240px; margin: 0 auto; padding: 28px 24px 60px; }}
            .breadcrumb {{ font-size: 0.75rem; color: #64748b; letter-spacing: 0.03em; display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
            .breadcrumb .env-pill {{ background: rgba(56,189,248,0.12); color: #38bdf8; font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.06em; }}

            h1.page-title {{ margin: 0 0 8px; font-size: 1.75rem; color: #f8fafc; }}
            p.page-sub {{ margin: 0 0 16px; color: #94a3b8; font-size: 0.92rem; }}
            .status-row {{ display: flex; align-items: center; gap: 18px; font-size: 0.8rem; color: #94a3b8; margin-bottom: 26px; }}
            .status-row .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 8px #4ade80; display: inline-block; margin-right: 6px; }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px;
            }}
            .stat-card .label {{ color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}
            .stat-card .value {{ color: #f8fafc; font-size: 1.45rem; font-weight: 700; margin-top: 10px; }}
            .stat-card .sub {{ color: #64748b; font-size: 0.72rem; margin-top: 6px; }}

            .dashboard-grid {{
                display: grid;
                grid-template-columns: 1.7fr 1fr;
                gap: 20px;
            }}
            .panel {{
                background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 24px;
            }}
            .panel-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
            .panel h3 {{ margin: 0; color: #f8fafc; font-size: 1rem; }}
            .panel .panel-sub {{ color: #64748b; font-size: 0.78rem; margin: 2px 0 14px; }}
            .link-btn {{ color: #38bdf8; font-size: 0.78rem; font-weight: 600; text-decoration: none; }}

            table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
            th, td {{ padding: 11px 8px; text-align: left; border-bottom: 1px solid #1f2937; }}
            th {{ color: #64748b; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}
            .role-pill {{ padding: 3px 9px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; }}
            .mfa-pill {{ color: #4ade80; font-size: 0.78rem; }}
            .status-live {{ color: #4ade80; font-weight: 700; }}

            .telemetry-chain {{ display: flex; justify-content: space-between; align-items: center; margin: 6px 0 20px; position: relative; }}
            .chain-step {{ display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; position: relative; z-index: 1; }}
            .chain-dot {{ width: 26px; height: 26px; border-radius: 50%; background: #1f2937; border: 1px solid #334155; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; }}
            .chain-dot.done {{ background: rgba(74,222,128,0.15); border-color: #4ade80; color: #4ade80; }}
            .chain-label {{ font-size: 0.68rem; color: #94a3b8; }}
            .telemetry-chain::before {{ content: ''; position: absolute; top: 13px; left: 5%; right: 5%; height: 1px; background: #263044; z-index: 0; }}

            .telemetry-list {{ font-size: 0.82rem; color: #cbd5e1; line-height: 2.1; margin-bottom: 18px; }}
            .telemetry-list .k {{ color: #64748b; }}

            .enclave-box {{
                background: rgba(74,222,128,0.06); border: 1px solid rgba(74,222,128,0.25);
                border-radius: 10px; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center;
            }}
            .enclave-box .title {{ font-size: 0.82rem; font-weight: 600; color: #e2e8f0; }}
            .enclave-box .sub {{ font-size: 0.72rem; color: #64748b; margin-top: 2px; }}
            .verified-pill {{ background: rgba(74,222,128,0.15); color: #4ade80; font-size: 0.68rem; font-weight: 700; padding: 4px 10px; border-radius: 999px; }}

            .signed-row {{
                margin-top: 20px; background: #111827; border: 1px solid #1f2937; border-radius: 12px;
                padding: 16px 22px; display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;
            }}
            .signed-row .left {{ color: #94a3b8; }}
            .signed-row .left strong {{ color: #e2e8f0; }}
            .signed-row a {{ color: #38bdf8; text-decoration: none; font-weight: 600; margin-left: 18px; font-size: 0.78rem; }}
        </style>
    </head>
    <body>

    <div class="navbar">
        <h2><span class="badge-icon">🛡️</span> CloudInfra Secure Admin Console</h2>
        <div class="nav-right">
            <div class="nav-hostname">
                <div class="label">Container Hostname</div>
                <code>{CONTAINER_ID}</code>
            </div>
            <div class="notif-container" onclick="toggleDropdown()">
                <div class="bell-icon">🔔<span class="notif-badge">{len(current_notes)}</span></div>
                <div class="notif-dropdown" id="notifDropdown">
                    <div class="notif-head">
                        <div>
                            <div class="notif-head-title">Build Release Notes</div>
                            <div class="notif-head-sub">v1.{BUILD_NUMBER}.0 &middot; Deployed {DEPLOY_TIME}</div>
                        </div>
                        <span class="notif-latest-tag">LATEST</span>
                    </div>
                    {render_release_notes()}
                    <div class="notif-footer"><a href="/health">View full changelog &rarr;</a></div>
                </div>
            </div>
            <div class="avatar">{ADMIN_INITIALS}</div>
        </div>
    </div>

    <div class="main-content">
        <div class="breadcrumb">CLOUDINFRA / production <span class="env-pill">PRODUCTION</span></div>
        <h1 class="page-title">Infrastructure overview</h1>
        <p class="page-sub">Your production control plane. Verified, isolated and operating as expected.</p>
        <div class="status-row">
            <span><span class="dot"></span>All systems nominal</span>
            <span>{CLUSTER_REGION}</span>
            <span>Synced 8s ago</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Active Build Version</div>
                <div class="value" style="color: #38bdf8;">v1.{BUILD_NUMBER}.0</div>
                <div class="sub">Signed build &middot; {BUILD_HASH} &middot; stable</div>
            </div>
            <div class="stat-card">
                <div class="label">System Health Status</div>
                <div class="value status-live">Operational</div>
                <div class="sub">99.9% uptime over the last 30 days</div>
            </div>
            <div class="stat-card">
                <div class="label">Malware Scan Gate</div>
                <div class="value" style="color: #4ade80;">Passed &ndash; Exit 0</div>
                <div class="sub">0 threats detected &middot; scanned {DEPLOY_TIME}</div>
            </div>
            <div class="stat-card">
                <div class="label">Active Cluster Nodes</div>
                <div class="value">4 / 4</div>
                <div class="sub">All nodes ready &middot; quorum established</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="panel">
                <div class="panel-head">
                    <h3>👥 Enterprise Access Control &amp; Admin Users</h3>
                    <a class="link-btn" href="#">Manage access</a>
                </div>
                <div class="panel-sub">Privileged identities with access to the production control plane.</div>
                <table>
                    <thead>
                        <tr><th>User / Email</th><th></th><th>Assigned Role</th><th>MFA</th><th>Last Active</th></tr>
                    </thead>
                    <tbody>
                        {render_admin_rows()}
                    </tbody>
                </table>
            </div>

            <div class="panel">
                <div class="panel-head">
                    <h3>⚙️ Pipeline Telemetry</h3>
                    <span class="status-live" style="font-size:0.72rem;">● LIVE</span>
                </div>
                <div class="panel-sub">Deployment chain</div>
                <div class="telemetry-chain">
                    <div class="chain-step"><div class="chain-dot done">✓</div><div class="chain-label">Build</div></div>
                    <div class="chain-step"><div class="chain-dot done">✓</div><div class="chain-label">Scan</div></div>
                    <div class="chain-step"><div class="chain-dot done">✓</div><div class="chain-label">Attest</div></div>
                    <div class="chain-step"><div class="chain-dot done">✓</div><div class="chain-label">Deploy</div></div>
                </div>
                <div class="telemetry-list">
                    <div><span class="k">Orchestrator</span><br>Kubernetes 1.31.2</div>
                    <div><span class="k">Control plane</span><br>prod-cluster-01</div>
                    <div><span class="k">Security engine</span><br>ClamAV 1.4.1</div>
                    <div><span class="k">Signature database</span><br><span style="color:#4ade80;">Current</span> &middot; {DEPLOY_TIME}</div>
                </div>
                <div class="enclave-box">
                    <div>
                        <div class="title">Secure enclave environment</div>
                        <div class="sub">AWS Nitro Enclaves &middot; us-prod-se-01</div>
                    </div>
                    <span class="verified-pill">VERIFIED</span>
                </div>
            </div>
        </div>

        <div class="signed-row">
            <div class="left">Latest signed event &middot; {DEPLOY_TIME} &mdash; <strong>deployment.verified</strong>: v1.{BUILD_NUMBER}.0 promoted to production by ci-service-account</div>
            <div>
                <a href="#">✓ Hash chain intact</a>
                <a href="/health">View audit trail &rarr;</a>
            </div>
        </div>
    </div>

    <script>
    function toggleDropdown() {{
        var drop = document.getElementById('notifDropdown');
        drop.classList.toggle('active');
    }}
    window.onclick = function(event) {{
        if (!event.target.closest('.notif-container')) {{
            document.getElementById('notifDropdown').classList.remove('active');
        }}
    }}
    </script>

    </body>
    </html>
    """


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "build_number": BUILD_NUMBER,
        "container_id": CONTAINER_ID,
        "deployed_at": DEPLOY_TIME,
        "release_notes": [{"title": t, "description": d} for t, d in current_notes],
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
