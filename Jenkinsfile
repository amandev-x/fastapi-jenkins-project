pipeline {
    agent any

    stages {
        stage("Checkout Git Repository")
        {
            steps {
                echo "Checking out git repository"
                checkout scm
            }
        }

        stage("Environment Info"){
            steps {
                sh '''
                   echo "Python Version"
                   python3 --version
                   echo "Current Directory"
                   pwd 
                   echo "List files"
                   ls -la
                   '''
            }
        }

        stage("Setup Python Environment") {
            steps {
                sh '''
                   python3 -m venv .venv
                   . .venv/bin/activate
                   pip3 install -r requirements.txt
                   '''
            }
        }

        stage("Testing Code") {
            steps {
                sh '''
                   echo "Testing code using pytest"
                   . .venv/bin/activate
                   pytest -v
                   '''
            }
        }

        stage("Success"){
            steps {
                echo "✅ Pipeline completed successfully!"
            }
        }
    }

    post {
        always {
            echo "Cleaning up"
            sh 'rm -rf .venv'
        }

        success {
            echo "🎉 Build succeeded!"
        }

        failure {
            echo '❌ Build failed!'
        }
    }
}