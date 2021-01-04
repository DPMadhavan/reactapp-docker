import json
import pandas as pd
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key
import operator
def lambda_handler(event=None, context=None):
    db=boto3.resource('dynamodb')
    user_interest_cards=db.Table('localzi-user-interestcards')
    place_category_rating=db.Table('localzi-place-rating')
    #-----fetching user details
    #val='u1'
    response = user_interest_cards.scan()
    UserID=[]
    CategoryID=[]
    Rating=[]
    for user in response['Items']:
        UserID.append(user['UserID'])
        CategoryID.append(user['CategoryID'])
        Rating.append(user['Rating'])
    userdf=pd.DataFrame(list(zip(UserID,CategoryID,Rating)), columns =['UserID', 'CategoryID','Rating'])
    #when group by has to be done?
    group_by_userid = userdf.groupby(userdf.UserID) #grouping by userid
    unique_users = list(set(UserID))
    UserID =CategoryID =Rating = None
    #--------end of fetching from user intrest cards table
    #--------fetching places under each category of user'''
    response = place_category_rating.scan()
    PlaceID=[]
    CategoryID=[]
    PlaceName=[]
    Rating=[]
    for place in response['Items']:
        PlaceID.append(place['PlaceID'])
        CategoryID.append(place['CategoryID'])
        PlaceName.append(place['PlaceName'])
        Rating.append(place['Rating'])
    unique_placeid=list(set(PlaceID))
    placedf = pd.DataFrame(list(zip(PlaceID,CategoryID,PlaceName,Rating)), columns =['PlaceID', 'CategoryID','PlaceName','Rating'])
    group_by_placeid=placedf.groupby(placedf.PlaceID)
    PlaceID=CategoryID =PlaceName =Rating = None
    #----- end of fectching from place category table
    print(placedf.head(10))
    print(userdf.head(10))
    #---------- grouping

    for user in unique_users:
        di={}
        for place in unique_placeid:
            each_user = group_by_userid.get_group(user)
            each_place=group_by_placeid.get_group(place)
            merge_each_user_place=pd.merge(each_user,each_place,on='CategoryID')
            merge_each_user_place['Score']=merge_each_user_place['Rating_x']*merge_each_user_place['Rating_y']
            di[place]=sum(merge_each_user_place['Score'])
        
        sorted_di= sorted(di.items(), key=operator.itemgetter(1),reverse=True)
        print(user)
        print("---------")
        for i in range(5):
            print(placedf.loc[placedf['PlaceID']==sorted_di[i][0],'PlaceName'].iloc[0])
        print("--------------------------------------------------")
    














    
    return 1

