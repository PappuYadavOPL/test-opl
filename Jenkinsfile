pipeline {
    agent any
    environment {
        GIT_CREDENTIALS = credentials('GitHub_Credential') // Use the ID you provided for your credentials
    }
    stages {
       stage('Checkout') {
            steps {
                // Checkout code from Git using credentials
                git branch: 'main', credentialsId: 'GitHub_Credential', url: 'https://github.com/PappuYadavOPL/test-opl.git'
                //git credentials: GIT_CREDENTIALS, branch: 'main', url: 'https://github.com/PappuYadavOPL/test-opl.git'
            }
        }
        stage('Add File') {
            steps {
                // Add a txt file to the workspace
                sh 'echo "This is a test file" > test2.txt'
            }
        }
        stage('Check if branch exists') {
            steps {
                script {
                    def branchExists = sh(script: 'git show-ref --verify --quiet "refs/heads/new-branch"', returnStatus: true) == 0
                    if (branchExists) {
                        echo "Branch 'new-branch' already exists."
                    } else {
                        // Create the branch "new-branch"
                        sh 'sudo git checkout -b new-branch'
                        echo "Branch 'new-branch' created."
                    }
                }
            }
        }
        stage('Commit and push changes') {
            steps {
                script {
                    sh 'sudo git config --global user.email "pappu.yadav@oplinnovate.com"'
                    sh 'sudo git config --global user.name "Pappu Yadav"'
                    sh 'sudo git add .'
                    sh 'sudo git commit -m "added to new branch"'
                    sh "git push https://PappuYadavOPL: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@github.com/PappuYadavOPL/test-opl.git HEAD:new-branch --force"
                    //sh 'sudo git push origin HEAD:new-branch --force'
                }
            }
        }
    }
}
