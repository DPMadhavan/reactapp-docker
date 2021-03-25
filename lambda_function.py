from recommender import *
import pandas as pd
import boto3
import os
import logging

if os.environ['ENVIRONMENT'].upper() =="DEVELOPMENT":
    place_table= "localzi-place-rating-test"
    user_table = "localzi-user-interest-test"
    recommender_table ="localzi-user-place-recommendation-test"
    #for of now the userid is given manually later its dynamically assigned
elif os.environ['ENVIRONMENT'].upper() =="PRODUCTION":
    place_table = "localzi-place-rating"
    user_table = "localzi-user-interestcards"
    recommender_table = "localzi-user-place-recommendation"


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
    if event['Records'][0]['eventSourceARN'] == 'arn:aws:dynamodb:ap-south-1:895767246702:table/localzi-user-interest-test/stream/2021-03-22T04:30:35.232':
        if event['Records'][0]['eventName']== 'INSERT' or event['Records'][0]['eventName']== 'MODIFY':
            user = event['Records'][0]['dynamodb']['NewImage']['userID']['S']
            logger.info(user)
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
                logger.info("failed for "+str(user))
                
        elif event['Records'][0]['eventName']== 'REMOVE':
            user = event['Records'][0]['dynamodb']['OldImage']['userID']['S']
            table = dynamodb.Table(recommender_table)
            response = table.query(KeyConditionExpression=Key('userID').eq(user))
            delete_recommended_of_user(response, table)


def del_user_if_exist_in_recommender_table(user):
    try:
        table = dynamodb.Table(recommender_table)
        response = table.query(KeyConditionExpression=Key('userID').eq(user))
        if len(response['Items'])>0:
            delete_recommended_of_user(response,table)
    except Exception as exp:
        logger.error(exp)

def delete_recommended_of_user(response_query,table):
    try:
        for del_user in response_query['Items']:
            response = table.delete_item(Key={'userID': del_user['userID'], 'placeID': del_user['placeID']})
        logger.info("deleted successfully {}".format(response_query['Items'][0]['userID']))
    except:
        logger.error(e)
