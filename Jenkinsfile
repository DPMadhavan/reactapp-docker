pipeline {
    environment{
        BRANCH_NAME= "${env.BRANCH_NAME}"
        LocalziGit =credentials("Localzigit")
    }
    agent any
    stages{
        stage('Clone Repo and Clean it'){
            steps{
                echo "${BRANCH_NAME}"
                sh 'rm -rf localzi-recommender-lambda'
                sh 'git clone https://$LocalziGit_USR:$LocalziGit_PSW@github.com/localzi/localzi-recommender-lambda.git'
            }
        }
                
        stage('Production'){
            when{
                expression { BRANCH_NAME =='main'}
            }
            steps{
                sh "mvn package"
                 timeout(time:5, unit:'DAYS'){
                     //input message:'Approve deployment?', submitter: 'localzi'
                 }
                sh "aws s3 cp target/localzi-document-upload-1.0.0.jar s3://localzi-documents-service"
                sh '''aws lambda update-function-code --function-name blueprint-python-lambda --s3-bucket localzi-documents-service --s3-key localzi-document-download-1.0.0.jar --region ap-south-1'''
            }
            post{
                success{
                    echo "Successfully deployed to Production"
                }
                failure{
                    echo "Failed deploying to Production"
                }
            }
        }
        stage('Development'){
                    when{
                        expression { BRANCH_NAME =='dev'}
                    }
                    steps{
                        sh "mvn package"
                        sh "aws s3 cp target/localzi-document-download-1.0.0.jar s3://localzi-documents-service-test"
                        sh '''aws lambda update-function-code --function-name localzi-encrypt-document-download-lambda-test --s3-bucket localzi-documents-service-test --s3-key localzi-document-download-1.0.0.jar --region ap-south-1'''
                        sh '''aws lambda update-function-code --function-name localzi-encrypt-document-preview-lambda-test --s3-bucket localzi-documents-service-test --s3-key localzi-document-download-1.0.0.jar --region ap-south-1'''
                    }
                    post{
                        success{
                            echo "Successfully deployed to Stagging"
                        }
                        failure{
                            echo "Failed deploying to Stagging"
                        }
                    }
                }
                stage('Testing'){
                            when{
                                expression { BRANCH_NAME !='main' && BRANCH_NAME !='dev'}
                            }
                            steps{
                            	sh 'pip install --user -r requirements.txt'
				sh "zip -r ../localzi-recommender-lambda.zip ."
				sh "aws s3 cp ../localzi-recommender-lambda.zip s3://localzi-lambda-functions-test"
		                sh '''aws lambda update-function-code --function-name localzi-place-recommender-test \\
		                                       --s3-bucket localzi-lambda-functions-test \\
		                                       --s3-key localzi-recommender-lambda.zip \\
		                                       --region ap-south-1'''
                            }
                            post{
                                success{
                                    echo "Successfully deployed to Development"
                                }
                                failure{
                                    echo "Failed deploying to Development"
                            }
                     }
                }
    }

}
