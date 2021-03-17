from recommender import *
import pandas as pd
import boto3
import os
import logging

if os.environ['ENVIRONMENT'].upper() =="DEVELOPMENT":
    place_table = "localzi-place-rating-test"
    user_table = "localzi-user-interest-test"
    recommender_table ="localzi-places-recommended-test"
    user = os.environ['USERID']
    #for of now the userid is given manually later its dynamically assigned
elif os.environ['ENVIRONMENT'].upper() =="PRODUCTION":
    place_table = "localzi-place-rating"
    user_table = "localzi-user-interestcards"
    recommender_table = "places-recommended"
    user = "u1"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db=boto3.resource('dynamodb')
try:
    place_interest_rating=db.Table(place_table)
except Exception as e:
    logger.error(e)
response = place_interest_rating.scan()

def lambda_handler(event=None, context=None):
    PlaceID=[]
    InterestID=[]
    Rating=[]
    try:
        for place in response['Items']:
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



