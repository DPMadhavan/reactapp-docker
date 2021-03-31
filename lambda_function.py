from recommender import *
import pandas as pd
import boto3
import os
import logging
user=None
if os.environ['ENVIRONMENT'].upper() =="DEVELOPMENT":
    place_table= "localzi-place-rating-test"
    user_table = "localzi-user-interest-test"
    recommender_table ="localzi-user-place-recommendation-test"
    sqs='localzi-call-place-recommender'

elif os.environ['ENVIRONMENT'].upper() =="PRODUCTION":
    place_table = "localzi-place-rating"
    user_table = "localzi-user-interestcards"
    recommender_table = "localzi-user-place-recommendation"
    sqs = 'localzi-call-place-recommender'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb=boto3.resource('dynamodb')
try:
    place_interest_rating=dynamodb.Table(place_table)
except Exception as e:
    logger.error(e)
response_placedf = place_interest_rating.scan()

def lambda_handler(event=None, context=None):
    global response_placedf
    global user
    if user_table in event['Records'][0]['eventSourceARN']:
        if event['Records'][0]['eventName']== 'INSERT' or event['Records'][0]['eventName']== 'MODIFY':
            logger.info("got triggered by dynamodb")
            user = event['Records'][0]['dynamodb']['NewImage']['userID']['S']
        elif event['Records'][0]['eventName'] == 'REMOVE':
            user = event['Records'][0]['dynamodb']['OldImage']['userID']['S']
            del_user_if_exist_in_recommender_table(user)
            logger.info("{} userid's recommended places are removed".format(user))
            return "dynamo remove event/trigger occured"
    elif sqs in event['Records'][0]['eventSourceARN']:
        logger.info("got triggered by sqs")
        user=event['Records'][0]['body']

    logger.info("userid is {}".format(user))
    del_user_if_exist_in_recommender_table(user)
    PlaceID=[]
    InterestID=[]
    Rating=[]
    try:
        for place in response_placedf['Items']:
            PlaceID.append(place['placeID'])
            InterestID.append(place['interestID'])
            Rating.append(place['rating'])
    except Exception as e:
        logger.error(e)

    placedf = pd.DataFrame(list(zip(PlaceID, InterestID, Rating)), columns= ['PlaceID', 'InterestID', 'Rating'])
    PlaceID= InterestID = Rating = None
    res=each_user_places_rec(user, placedf, user_table, recommender_table)
    if res:
        logger.info("successfully ran for "+str(user))
    else:
        logger.info("failed for "+str(user)+" user does not exist")



def del_user_if_exist_in_recommender_table(user):
    try:
        table = dynamodb.Table(recommender_table)
        response_query = table.query(KeyConditionExpression=Key('userID').eq(user))
        for del_user in response_query['Items']:
            response = table.delete_item(Key={'userID': del_user['userID'], 'placeID': del_user['placeID']})
        logger.info("deleted successfully if record existed for user id {}".format(user))
    except Exception as exp:
        logger.error(exp)

