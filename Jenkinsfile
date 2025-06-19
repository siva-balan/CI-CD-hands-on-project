pipeline {
    agent { label 'docker-agent' }
    stages{
        stage('Build Docker Image'){
            steps{
                sh './build.sh'
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
