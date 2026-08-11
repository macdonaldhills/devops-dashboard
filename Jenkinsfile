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
                sh '''
                    docker build \
                        -t chibi7/devops-dashboard:latest \
                        -t chibi7/devops-dashboard:${BUILD_NUMBER} \
                        .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker push chibi7/devops-dashboard:latest
                        docker push chibi7/devops-dashboard:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f devops-dashboard-test || true
                    docker pull chibi7/devops-dashboard:${BUILD_NUMBER}
                    docker run -d \
                        --name devops-dashboard-test \
                        --network jenkins \
                        chibi7/devops-dashboard:${BUILD_NUMBER}
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
            echo "DevOps Dashboard build ${BUILD_NUMBER} completed successfully!"
        }

        failure {
            echo "DevOps Dashboard build ${BUILD_NUMBER} failed."
        }
    }
}
