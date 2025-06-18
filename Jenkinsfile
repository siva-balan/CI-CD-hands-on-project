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
        stage('Wait') {
            steps {
                echo 'Waiting 10 seconds...'
                sleep time: 10, unit: 'SECONDS'
            }
        }
        stage('Test Application status'){
            steps{
                sh './test.sh'
            }
        }
    }
}
