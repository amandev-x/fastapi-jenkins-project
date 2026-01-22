pipeline {
    agent { label "build-agent" }
    // agent any

    parameters {
    //     choice(
    //         name: "RUN_LINTING",
    //         choices: ["yes", "no"],
    //         description: "Run linting?"
    //     )

    //     choice(
    //         name: "RUN_TESTS",
    //         choices: ["yes", "no"],
    //         description: "Run unit tests?"
    //     )

        string(
            name: "COVERAGE_THRESHOLD",
            defaultValue: "80",
            description: "Minimum code coverage percentage"
        )
    }

    environment {
        PYTHON_VERSION = "python3"
        VENV_DIR = ".venv"
        APP_NAME = "FastAPI Todo API"
        DOCKER_IMAGE = "amandabral9954/fastapi-todo"
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = credentials("dockerhub-credentials")

        // Deployment Settings
        DEPLOYMENT_HOST = "localhost"
        DEPLOYMENT_USER = "ubuntu"
        DEPLOYMENT_PATH = "/opt/fastapi-app"
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
                   '''
                echo "Environment setup complete..."
            }
        }

        stage("Counting lines of code") {
            steps {
                sh 'find app/ -name "*.py" | xargs wc -l'
            }
        }

        stage("Security Scan with Bandit") {
            steps {
                echo "Running security scan with Bandit..."
                sh '''
                    . ${VENV_DIR}/bin/activate
                    bandit -r app/ --level medium --format html -o bandit-report.html --exit-zero || true
                '''
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: ".",
                    reportFiles: "bandit-report.html",
                    reportName: "Bandit Security Report"
                ])
                echo "Security scan complete."
            }
        }

        stage("Code Quality and Test") {
            parallel {
                stage("Linting") {
                    // when {
                    //     expression { params.RUN_LINTING == "yes"}
                    //     }
                    steps {
                        echo "Running code quality checks..."

                        sh '''
                          . ${VENV_DIR}/bin/activate
                          echo "Running flake8..."
                          flake8 --max-line-length 100 app/ --exit-zero || true

                          echo "Running Black..."
                          black --check app/ tests/ || true
                          '''
                        echo "Linting complete."
                    }
                }

                stage("Unit Testing") {
                    // when {
                    //     expression { params.RUN_TESTS }
                    //     }
                    steps {
                        echo "Running Unit Tests..."
                        sh '''
                          . ${VENV_DIR}/bin/activate
                          pytest --junitxml=test-result.xml --cov-fail-under=${COVERAGE_THRESHOLD}
                          '''
                        echo "Test passed."
                    }
                }
            }
        }

        stage("Build Docker Image") {
            steps {
                echo "🐳 Building Docker image..."
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
                echo "✅ Docker image build successfully..."
            }
        }

        stage("Test Docker Image") {
            steps {
                echo "Running docker image..."
                sh '''
                  docker run -d --name test-container -p 8001:8000 ${DOCKER_IMAGE}:${DOCKER_TAG}

                  sleep 5

                  # Test health endpoint
                  curl -f http://localhost:8001/health || exit 1

                  # Test root endpoint
                  curl -f http://localhost:8001/ || exit 1

                  # Stop and remove docker container
                  docker rm -f test-container
                '''
                echo "✅ Docker image test passed..."
            }
        }

        stage("Push to Dockerhub") {
            steps {
                echo "Pushing to dockerhub"
                script {
                    docker.withRegistry("https://registry.hub.docker.com", "dockerhub-credentials") {
                      docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                      docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
                echo "✅ Image pushed successfully"
            }
        }

        stage("Deploy to Dev") {
            steps {
                // Remove old fastapi containers if exists
                sh '''
                  docker rm -f fastapi-dev || true 

                  docker image pull ${DOCKER_IMAGE}:${DOCKER_TAG}

                  # Run a new container
                  docker run -d --name fastapi-dev -p 8100:8000 --restart unless-stopped \
                  ${DOCKER_IMAGE}:${DOCKER_TAG}

                  # Wait for container to restart
                  sleep 10

                  # Test the healthcheck
                  curl -f http://localhost:8100/health || exit 1
                '''
                echo "Deployed to Dev Successfully"
            }
        }

        stage("Deploy to Staging") {
            steps {
            // Remove old containers if exists
            sh '''
              docker rm -f fastapi-staging

              docker image pull ${DOCKER_IMAGE}:${DOCKER_TAG}

              # Run a new container
              docker run -d --name fastapi-staging -p 8200:8000 --restart unless-stopped \
              ${DOCKER_IMAGE}:${DOCKER_TAG}

              # Wait for container to start
              sleep 10

              # Test the healthcheck
              curl -f http://localhost:8200/health || exit 1
            '''
            echo "Deployed to Staging: http://localhost:8200"
        }
        }

        stage("Approval for Production") {
            steps {
                echo "Waiting for manual approval to deploy to Production"
                input message: "Deploy to Production?", ok: "Deploy"
            }
        }

        stage("Deploy to Production - Blue/Green") {
            steps {
                echo "Deploying to Blue/Green Production"
                script {
                    // Determine current and next colours
                    def currentColor = sh (
                        script: "docker ps --filter 'name=fastapi-prod' --format '{{.Names}}' | grep -o 'blue\\green' || echo 'blue'",
                        returnStdout: true     
                    ).trim()

                    def nextColor = (currentColor == "blue")? "green": "blue"
                    echo "Current color: ${currentColor}, Deploying: ${nextColor}"

                    // Deploy to new version
                    sh """
                      # Stop and remove next color if exists
                      docker rm -f fastapi-prod--${nextColor} || true

                      # Pull latest image
                      docker image pull ${DOCKER_IMAGE}:${DOCKER_TAG}

                      # Run new container on standby port
                      docker run -d --name fastapi-prod-${nextColor} -p 9000:8000 \
                      --restart unless-stopped ${DOCKER_IMAGE}:${DOCKER_TAG}

                      # Wait for container to start
                      sleep 10

                      # Healthcheck on standby port
                      curl -f http://localhost:9000/health || exit 1
                      echo "Healthcheck passed successfull on standy port"
                    """

                    // Prompt to switch traffic
                    input message: "Switch traffic from ${currentColor} to ${nextColor}?", ok: "switch"

                    // Switch Traffic
                    sh """
                      # Stop current production container
                      docker rm -f fastapi-prod-${currentColor} || true

                      # Recreate new container on production port
                      docker run -d --name fastapi-prod-${nextColor} -p 8000:8000 \
                      --restart unless-stopped ${DOCKER_IMAGE}:${DOCKER_TAG}
                      
                      # Final health check
                      sleep 5
                      curl -f http://localhost:8000/health || exit 1
                      echo "Traffic switched to ${nextColor}"
                      echo "Current color is now standby. Can be used to rollback."
                    """
                }
            }
        }

        stage("Cleanup Docker") {
            steps {
                echo "Cleaning docker images"
                sh '''
                  docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                  docker rmi ${DOCKER_IMAGE}:latest || true

                  # Clean up dangling images
                  docker image prune -f
                '''
                echo "✅ Docker cleanup successfully"
            }
        }

        stage("Build Summary") {
            steps {
                echo "Build Summary"
                sh '''
                  echo "====================="
                  echo "Application: ${APP_NAME}"
                  echo "Build Number: ${BUILD_NUMBER}"
                  echo "Build Url: ${BUILD_URL}"
                  echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                  echo "Git Branch: ${GIT_BRANCH}"
                  echo "Git Commit: ${GIT_COMMIT}"
                  echo "====================="
                  echo "Dev:   http://${DEPLOY_HOST}:8100"
                  echo "Stage: http://${DEPLOY_HOST}:8200"
                  echo "Prod:  http://${DEPLOY_HOST}:8000"
                '''
            }
        }
    }

    post {
        always {
            echo "Cleaning up"
            sh 'rm -rf ${VENV_DIR}'
            junit "test-result.xml"
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: "htmlcov",
                reportFiles: "index.html",
                reportName: "Code Coverage Report"
            ])
        }

        success {
            echo "🎉 Pipeline build successfull. All Tests case passed."
            echo """ 
              Deployment Successfull...
              Access your application:
              - Dev http://YOUR-EC2-IP/8100/docs
              - Stage htpp://YOUR-EC2-IP/8200/docs
              - Prod http://YOUR-EC2-IP/8000/docs
            """

            // emailext(
            //     subject: "Success Job '${env.JOB_NAME}' [${env.BUILD_NUMBER}]'",
            //     body: """
            //       <p> Good News! The job was build successfully! </p>
            //       <p><b>Job:</b> ${env.JOB_NAME} </p>
            //       <p><b>Build number:</b> ${env.BUILD_NUMBER} </p>
            //       <p><b>Build URL:</b> </a href="${env.BUILD_NUMBER}">${env.BUILD_URL}</a></p>
            //     """,
            //     to: "",
            //     mimeType: "text/html"
            // )
        }

        failure {
            echo '❌ Build failed! Please check the logs and fix the issues.'
            // emailext(
            //     subject: "Failure Job ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
            //     body: """
            //       <p> Unfortuanately build failed </p>
            //       <p><b>Job:</b> ${env.JOB_NAME}</p>
            //       <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
            //       <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
            //       <p>Please check the console output for details.</p>
            //       """,
            //       to: "",
            //       mimeType: "text/html"
            // )
        }

        unstable {
            echo "Pipeline is unstable. Some tests case have benn failed."
        }
    }
}