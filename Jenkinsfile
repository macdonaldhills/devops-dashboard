pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'chibi7/devops-dashboard'
    }

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
                        -t ${DOCKER_IMAGE}:latest \
                        -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
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
                        docker push ${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl set image deployment/devops-dashboard \
                        devops-dashboard=${DOCKER_IMAGE}:${BUILD_NUMBER}

                    kubectl rollout status deployment/devops-dashboard \
                        --timeout=120s
                '''
            }
        }

        stage('Kubernetes Health Check') {
            steps {
                sh '''
                    kubectl wait \
                        --for=condition=available \
                        deployment/devops-dashboard \
                        --timeout=120s

                    kubectl get pods
                    kubectl get service devops-dashboard

                    echo "Kubernetes deployment is healthy."
                '''
            }
        }
    }

    post {
        success {
            echo "DevOps Dashboard build ${BUILD_NUMBER} deployed successfully to Kubernetes!"
        }

        failure {
            echo "DevOps Dashboard build ${BUILD_NUMBER} failed."
        }
    }
}
