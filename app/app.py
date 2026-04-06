from flask import Flask
import datetime

app = Flask(__name__)

DEPLOYMENT_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevSecOps Pipeline</title>
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
            .info {{ color: #89b4fa; margin-top: 20px; font-size: 0.95rem; }}
            .time {{ color: #f38ba8; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>✅ Deployment Successful</h1>
            <div class="badge">SECURE</div>
            <p>This build passed the ClamAV malware scan</p>
            <div class="info">
                <p>Pipeline: <strong>GitHub → Jenkins → ClamAV → Docker</strong></p>
                <p>Deployed at: <span class="time">{DEPLOYMENT_TIME}</span></p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)