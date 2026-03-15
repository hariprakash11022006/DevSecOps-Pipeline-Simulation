# DevSecOps Pipeline with Automated Malware Detection

A DevSecOps CI/CD pipeline that automatically scans code for malware before deployment.
If malware is detected, the pipeline blocks deployment entirely. Only clean code gets built and deployed.

---

## Architecture
```
Developer → git push → GitHub → Webhook → Jenkins
                                              |
                                    Pull repository files
                                              |
                                    ClamAV Malware Scan
                                         /         \
                                      CLEAN       INFECTED
                                        |              |
                                Docker Build     Pipeline FAILS
                                        |        (blocks deploy)
                                Docker Deploy
                                        |
                                App live on port 5000
```

## Tech Stack

| Tool | Purpose |
|---|---|
| GitHub | Source code repository |
| Jenkins | CI/CD pipeline orchestration |
| ClamAV | Malware scanning engine (3.6M+ signatures) |
| Docker | Containerized build and deployment |
| ngrok | Exposes local Jenkins to GitHub webhooks |
| Python + Flask | Sample application being deployed |

---

## Pipeline Stages

**1. Checkout** — Jenkins pulls latest code from GitHub

**2. Malware Scan** — ClamAV recursively scans all repository files
- Exit code 0 → Clean, pipeline continues
- Exit code 1 → Malware detected, pipeline fails and blocks deployment

**3. Build** — Docker builds the application image (only if scan passes)

**4. Deploy** — Docker runs the container on port 5000 (only if scan passes)

---

## Demo Scenarios

**Clean code push:**
```
git push → webhook triggers Jenkins → ClamAV scan passes
→ Docker builds image → App deployed on localhost:5000
```

**Malware detected:**
```
git push (with EICAR test file) → webhook triggers Jenkins
→ ClamAV detects threat → Pipeline blocked
→ Docker stages skipped → No deployment
```

---

## Project Setup

### Prerequisites
- Fedora Linux
- Jenkins
- Docker
- ClamAV
- ngrok

### Installation

**Jenkins:**
```bash
sudo dnf install jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

**Docker:**
```bash
sudo dnf install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo usermod -aG docker jenkins
```

**ClamAV:**
```bash
sudo dnf install clamav clamav-update
sudo freshclam
```

**ngrok:**
```bash
sudo snap install ngrok
ngrok config add-authtoken YOUR_TOKEN
ngrok http 8080
```

### Jenkins Configuration
1. Install plugins: Git, Pipeline, GitHub
2. Add GitHub credentials (Personal Access Token)
3. Create Pipeline job → Pipeline script from SCM
4. Set repository URL and branch
5. Add ngrok URL as GitHub webhook

---

## Project Structure
```
devsecops-pipeline/
├── app/
│   ├── app.py            # Flask web application
│   └── requirements.txt  # Python dependencies
├── Dockerfile            # Docker image definition
└── Jenkinsfile           # Pipeline stages definition
```

---

## Key Concepts

**DevSecOps** — Integrating security directly into the CI/CD pipeline instead of treating it as a separate step. Security is automated and mandatory — bad code never reaches production.

**ClamAV** — Open source antivirus engine with 3.6 million+ virus signatures. Returns exit codes that Jenkins uses to pass or fail the pipeline.

**Docker layer caching** — Unchanged layers are cached during rebuild, making subsequent builds significantly faster.

---

## Author

**Kulasekaran M**

B.E CSE — Anna University, Guindy

GitHub: [KULASEKARAN11](https://github.com/KULASEKARAN11)
