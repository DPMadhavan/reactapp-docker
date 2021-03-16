from recommender import *
import pandas as pd
import boto3
import os
import logging

if os.environ['ENVIRONMENT'].upper() =="DEVELOPMENT":
    place_table = "localzi-place-rating"
    user_table = "localzi-user-interestcards"
    recommender_table ="localzi-places-recommended-test"
    user = "u1"
elif os.environ['ENVIRONMENT'].upper() =="PRODUCTION":
    place_table = "localzi-place-rating"
    user_table = "localzi-user-interestcards"
    recommender_table = "places-recommended"
    user = "u1"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


db=boto3.resource('dynamodb')

try:
    place_category_rating=db.Table(place_table)
except Exception as e:
    logger.error(e)
response = place_category_rating.scan()

def lambda_handler(event=None, context=None):

    PlaceID=[]
    CategoryID=[]
    Rating=[]
    try:
        for place in response['Items']:
            PlaceID.append(place['PlaceID'])
            CategoryID.append(place['CategoryID'])
            Rating.append(place['Rating'])
    except Exception as e:
        logger.error(e)

    placedf = pd.DataFrame(list(zip(PlaceID, CategoryID, Rating)), columns= ['PlaceID', 'CategoryID', 'Rating'])
    PlaceID= CategoryID = Rating = None
    res=each_user_places_rec(user, placedf, user_table, recommender_table)
    if res:
        logger.info("successfully ran for "+str(user))
    else:
        logger.info("failed for "+str(user))



