#!/bin/bash
# Read and increment build number
if [ ! -f .build_num ]; then echo 0 > .build_num; fi
BUILD_NUMBER=$(($(cat .build_num) + 1))
echo $BUILD_NUMBER > .build_num

echo "=================================================="
echo "🚀 JENKINS CI/CD PIPELINE — BUILD #$BUILD_NUMBER"
echo "=================================================="

echo "📥 [Stage 1: Checkout] Checking repository state..."
git status -s

echo "🔍 [Stage 2: Malware Scan] Running ClamAV Engine..."
clamscan -r . --exclude-dir=".git"
SCAN_RESULT=$?

if [ $SCAN_RESULT -eq 1 ]; then
    echo "--------------------------------------------------"
    echo "❌ CRITICAL: MALWARE DETECTED IN COMMIT!"
    echo "🛑 Pipeline aborted at Stage 2. Docker Build & Deploy SKIPPED."
    echo "=================================================="
    exit 1
elif [ $SCAN_RESULT -eq 2 ]; then
    echo "⚠️ ERROR: ClamAV scan error."
    exit 2
else
    echo "✅ Scan complete — Exit Code 0 (No threats found)."
fi

echo "📦 [Stage 3: Build Docker Image] Building devsecops-app..."
docker build -t devsecops-app .

echo "🚀 [Stage 4: Deploy] Deploying Container on Port 5000..."
docker stop devsecops-app 2>/dev/null || true
docker rm devsecops-app 2>/dev/null || true
docker run -d --name devsecops-app -p 5000:5000 -e BUILD_NUMBER=$BUILD_NUMBER devsecops-app

echo "=================================================="
echo "✅ DEPLOYMENT SUCCESSFUL — Build #$BUILD_NUMBER Live at http://localhost:5000"
echo "=================================================="
