#!/usr/bin/env python
# coding: utf-8

# In[50]:


import numpy as np
import pandas as pd


# In[51]:


users=pd.read_csv(r'C:\Users\My PC\Downloads\localzi_user_db.csv')
m_places=pd.read_csv(r'C:\Users\My PC\OneDrive\Documents\placeTable.csv')


# In[52]:


user_l=['u1','u2','u3','u4','u5']
places_l=range(1,13)


# In[ ]:





# In[54]:


grouped=m_places.groupby(m_places.PlaceId)
groupedu=users.groupby(users.userid)


# In[68]:



for user in user_l:
    di={}
    for place in places_l:
        p=grouped.get_group(place)
        u=groupedu.get_group(user)
        #print(p)
        #print("*******************")
        #print(u)
        result=pd.merge(p,u,on='catid')
        
        
        result['score']=result['rating']*result['RatingNormal']
        #print(result)
        di[place]=sum(result['score'])
        #print("-----------------------------------------------------------------------------------------")
    #print(di)
    import operator
    sorted_d = sorted(di.items(), key=operator.itemgetter(1),reverse=True)
    for i in range(5):
        print(sorted_d[i][0])
    print("--------------------------------------------------")
    


# In[ ]:




