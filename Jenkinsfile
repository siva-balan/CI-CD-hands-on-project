pipeline {
    agent { label 'docker-agent' }
    stages{
        stage('Build Docker Image'){
            steps{
                sh './build.sh'
            }
        }
        stage('Push Image to Docker Hub'){
            steps{
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push sivabalansp/fix_log_analyzer:$BUILD_NUMBER'
                    sh 'docker push sivabalansp/fix_log_analyzer:latest'
                }
            }
        }
        stage('Deploy Container'){
            steps{
                sh './deploy.sh'
            }
        }
        stage('Test Application status'){
            steps{
                sh './test.sh'
            }
        }
    }
}
