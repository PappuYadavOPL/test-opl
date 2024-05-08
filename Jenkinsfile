pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from Git
                git branch: 'main', url: 'https://github.com/PappuYadavOPL/test-opl.git'
            }
        }
        stage('Add File') {
            steps {
                // Add a txt file to the workspace
                sh 'echo "This is a test file" > test.txt'
            }
        }
        stage('Check Branch and Push') {
            steps {
                // Check if the branch exists
                script {
                    def branchExists = sh(script: 'git ls-remote --heads origin new-branch', returnStatus: true) == 0

                    if (branchExists) {
                        // If branch exists, push changes to it
                        sh 'git checkout new-branch'
                    } else {
                        // If branch does not exist, create a new branch
                        sh 'git checkout -b new-branch'
                    }

                    // Add all changes
                    sh 'git add .'

                    // Commit changes
                    sh 'git commit -m "Adding test.txt file"'

                    // Push changes to the branch
                    sh 'git push origin new-branch'
                }
            }
        }
    }
}
