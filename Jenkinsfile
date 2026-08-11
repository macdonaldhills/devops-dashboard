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
        sh 'pip install -r requirements.txt'
        sh 'pytest'
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
                        -p 5001:5000 \
                        devops-dashboard:jenkins
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 5
                    curl -f http://localhost:5001/health
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
