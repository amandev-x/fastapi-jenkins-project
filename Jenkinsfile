pipeline {
    agent any

    environment {
        PYTHON_VERSION = "python3"
        VENV_DIR = ".venv"
        APP_NAME = "FastAPI Todo API"
    }

    stages {
        stage("Checkout Git Repository")
        {
            steps {
                echo "Checking out git repository"
                checkout scm
                echo "Checkout Successfully"
            }
        }

        stage("Environment Setup"){
            steps {
                sh '''
                   echo "Python Version"
                   ${PYTHON_VERSION} --version

                   echo "Creating virtual environment..."
                   ${PYTHON_VERSION} -m venv ${VENV_DIR}

                   echo "Activating Python virtual environment..."
                   . ${VENV_DIR}/bin/activate

                   echo "Installing dependencies..."
                   pip3 install -r requirements.txt
                   pip3 install -r requirements-dev.txt

                   echo "Installed packages"
                   pip3 list

                   echo "Current Directory"
                   pwd 
                   echo "List files"
                   ls -la
                   '''
                echo "Environment setup complete..."
            }
        }

        stage("Counting lines of code") {
            steps {
                sh 'find app/ -name "*.py" | xargs wc -l'
            }
        }

        stage("Code Quality and Test") {
            parallel {
                stage("Linting") {
                    steps {
                        echo "Running code quality checks..."

                        sh '''
                          . {VENV_DIR}/bin/activate
                          echo "Running flake8..."
                          flake8 --max-length-line 100 app/ --exit-zero || true

                          echo "Running Black..."
                          black --check app/ tests/ || true
                          '''
                        eccho "Linting complete."
                    }
                }

                stage("Unit Testing") {
                    steps {
                        echo "Running Unit Tests..."
                        sh '''
                          . {VENV_DIR}/bin/activate
                          pytest --junitxml=test-result.xml
                          '''
                        echo "Test passed."
                    }
                }
            }
        }

        stage("Test Report") {
            steps {
                echo "Generating Test Report"
                junit "test-result.xml"

                // Archive Coverage Report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: "htmlcov",
                    reportFiles: "index.html",
                    reportName: "Code Coverage Report"
                ])
                echo "Test Report Generated Successfully"
            }
        }

        stage("Build Summary") {
            steps {
                echo "Build Summary"
                sh '''
                  echo "====================="
                  echo "Application: ${APP_NAME}"
                  echo "Build Number: ${BUILD_NUMBER}
                  echo "Build Url: ${BUILD_URL}"
                  echo "Git Branch: ${GIT_BRANCH}"
                  echo "Git Commit: ${GIT_COMMIT}"
                  echo "====================="
                '''
            }
        }
    }

    post {
        always {
            echo "Cleaning up"
            sh 'rm -rf ${VENV_DIR}'
        }

        success {
            echo "🎉 Pipeline build successfull. All Tests case passed."
        }

        failure {
            echo '❌ Build failed! Please check the logs and fix the issues.'
        }

        unstable {
            echo "Pipeline is unstable. Some tests case have benn failed."
        }
    }
}