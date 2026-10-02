pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        IMAGE_NAME = 'taskflow-app'
        CONTAINER_NAME = "taskflow-ci-${env.BUILD_NUMBER}"
        CI_PORT = '5001'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Application Validation') {
            steps {
                sh '''
                    docker run -d --name ${CONTAINER_NAME} -p ${CI_PORT}:5000 ${IMAGE_NAME}:${BUILD_NUMBER}
                    for i in $(seq 1 15); do
                        if curl -fs http://localhost:${CI_PORT}/health; then
                            echo "Health check passed"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Health check FAILED"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
        success {
            echo 'Pipeline succeeded: tests passed, image built, container healthy.'
        }
        failure {
            echo 'Pipeline FAILED. Check the failing stage above.'
        }
    }
}
