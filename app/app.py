from flask import Flask
import os

app = Flask(__name__)

COUNTER_FILE = "/tmp/deploy_count.txt"

def get_deploy_number():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            count = int(f.read().strip())
    else:
        count = 0
    count += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
    return count

DEPLOY_NUMBER = get_deploy_number()

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevSecOps Pipeline-Demo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #1e1e2e;
                color: #cdd6f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #313244;
                border-radius: 12px;
                padding: 40px 60px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            }}
            h1 {{ color: #a6e3a1; font-size: 2rem; }}
            .badge {{
                background-color: #a6e3a1;
                color: #1e1e2e;
                padding: 6px 16px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin: 10px 0;
            }}
            .deploy-num {{
                font-size: 4rem;
                font-weight: bold;
                color: #89b4fa;
                margin: 20px 0;
            }}
            .info {{ color: #cdd6f4; font-size: 0.95rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>✅ Deployment Successful</h1>
            <div class="badge">SECURE — ClamAV Scan Passed</div>
            <div class="deploy-num">#{DEPLOY_NUMBER}</div>
            <div class="info">
                <p>Pipeline: <strong>GitHub → Jenkins → ClamAV → Docker</strong></p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)