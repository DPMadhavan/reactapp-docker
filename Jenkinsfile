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
                 	sh 'pip install --user -r requirements.txt'
			sh "zip -r ../localzi-recommender-lambda.zip ."
			sh "aws s3 cp ../localzi-recommender-lambda.zip s3://localzi-lambda-functions-prod"
		        sh '''aws lambda update-function-code --function-name localzi-place-recommender \\
		                                 --s3-bucket localzi-lambda-functions \\
		                                 --s3-key localzi-recommender-lambda.zip \\
		                                 --region ap-south-1'''
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
