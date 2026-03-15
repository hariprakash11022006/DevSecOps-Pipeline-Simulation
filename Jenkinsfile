pipeline {
    agent any

    triggers {
        githubPush()    
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Malware Scan') {
            steps {
                script {
                    def scanResult = sh(
                        script: 'clamscan -r . --exclude-dir=".git"',
                        returnStatus: true
                    )
                    if (scanResult == 1) {
                        error("MALWARE DETECTED — Deployment blocked!")
                    } else if (scanResult == 2) {
                        error("ClamAV scan error — check ClamAV setup")
                    } else {
                        echo "Scan complete — No threats found"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devsecops-app .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker stop devsecops-app || true
                    docker rm devsecops-app || true
                    docker run -d --name devsecops-app -p 5000:5000 devsecops-app
                '''
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed — check scan results or build logs"
        }
        success {
            echo "Deployment successful — app running on port 5000"
        }
    }
}