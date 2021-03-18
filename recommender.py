import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def each_user_places_rec(user,placedf=None,user_table=None,recommender_table=None):
    group_by_placeid = placedf.groupby(placedf.PlaceID)
    unique_placeid = list(set(placedf['PlaceID']))
    userdf=fetch_user_details(user, user_table)
    di = []

    for place in unique_placeid:
        each_place = group_by_placeid.get_group(place)
        merge_each_user_place = pd.merge(userdf, each_place, on='InterestID')
        di.append((place, sum(merge_each_user_place['Rating'])))

    di.sort(key=lambda x: x[1], reverse=True)
    res=results_into_dynamo(user,placedf, di,recommender_table)
    return 1


def results_into_dynamo(user,placedf,sorted_di,recommender_table):
    db = boto3.resource('dynamodb')
    tab = db.Table(recommender_table)
    try:
        for i in range(5):
            tab.put_item(
                Item={
                    'userID': user,
                    'placeID': str(placedf.loc[placedf['PlaceID'] == sorted_di[i][0], 'PlaceID'].iloc[0])
                })

    except Exception as exp:
        logger.error(exp)
        #print(str(placedf.loc[placedf['PlaceID'] == sorted_di[i][0], 'PlaceID'].iloc[0]))
    return 1


def fetch_user_details(user,user_table):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(user_table)
        response = table.query(KeyConditionExpression=Key('userID').eq(user))
    except Exception as exp:
        logger.error(exp)
    UserID=[]
    InterestID=[]
    try:
        for user in response['Items']:
            UserID.append(user['userID'])
            InterestID.append(user['interestCardID'])
    except Exception as exp:
        logger.error(exp)
    userdf=pd.DataFrame(list(zip(UserID, InterestID)), columns=['UserID', 'InterestID'] )
    #print("user details are")
    #print(UserID, InterestID)
    return userdf