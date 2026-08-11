pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m venv venv'
                sh 'venv/bin/pip install -r requirements.txt'
                sh 'venv/bin/pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-dashboard:jenkins .'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                    docker rm -f devops-dashboard-test || true
                    docker run -d \
                        --name devops-dashboard-test \
                        --network jenkins \
                        devops-dashboard:jenkins
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 5
                    curl -f http://devops-dashboard-test:5000/health
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f devops-dashboard-test || true'
        }

        success {
            echo 'DevOps Dashboard pipeline completed successfully!'
        }

        failure {
            echo 'DevOps Dashboard pipeline failed.'
        }
    }
}
