# class Recommender():
import math    
import pandas as pd
import pickle

avgRatings={}

def ampUpRating(items,prefs,p1,p2):
    for itemId in items.keys():
        if prefs[p1][itemId]==0:
            prefs[p1][itemId]=2
        if prefs[p2][itemId]==0:
            prefs[p2][itemId]=2
    return prefs

def alterSimilarityForItemsWithLessMatchingUsers(dist,matching_users,choke_matching_users):
    # print("init dist=",dist)
    if matching_users<choke_matching_users:
        dist+=(dist+1)*(choke_matching_users-matching_users)
    # print("final dist=",dist)
    return dist


def computeAvgRating(prefs,itemId):
    global avgRatings

    if itemId in avgRatings:
        return avgRatings[itemId]

    sum=0
    for userId,rating in prefs[itemId].items():
        sum+=rating
    result=sum/len(prefs[itemId])

    avgRatings[itemId]=result
    return avgRatings[itemId]

def sim_euclidean(prefs,p1,p2,choke_matching_users=3):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    matching_users=len(si)
    if matching_users==0:
        return (0,0,computeAvgRating(prefs,p2))
    # Find the number of elements
    rankings=[(prefs[p1][item],prefs[p2][item]) for item in si]
    # print(rankings)

    distances=[pow(rank[0]-rank[1],2) for rank in rankings]
    euclid_score=math.sqrt( alterSimilarityForItemsWithLessMatchingUsers( sum(distances) , matching_users , choke_matching_users ) )
    return ( 1/(1+ ( euclid_score ) ) , matching_users ,computeAvgRating(prefs,p2)) 

def sim_pearson(prefs,p1,p2):
 # Get the list of mutually rated items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    # Find the number of elements
    n=len(si)
    # print(si)
    prefs=ampUpRating(si,prefs,p1,p2)
    # print(si)
    # if they are no ratings in common, return 0
    if n==0: return 0
    # Add up all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    # Calculate Pearson score
    num=pSum-(sum1*sum2/n)
    den=math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    print("Common items={},num={},denom={},psum={},sum1={},sum2={}".format(si,num,den,pSum,sum1,sum2))
    for it in si:
        print("item={},x'srating={},y's rating={}".format(it,prefs[p1][it],prefs[p2][it])) 
    if den==0: return 0
    r=num/den
    return r

def computeSimiliartyScoresForAItem(items,presentItem,similarity=sim_euclidean,num_of_items=1000):

    sim_items=[]

    for other in items:
        # don't compare me to myself
        if other==presentItem: continue

        sim_score,matching_users,avg_rating=similarity(items,presentItem,other)
        sim_items.append((other,sim_score,matching_users,avg_rating))

    sim_items.sort(key=lambda x: ( x[1],x[2],x[3] ),reverse=True)

    return sim_items[:num_of_items]

def computeSimiliartyScores(items,similarity=sim_euclidean):

    cnt=1
    similarities_matrix={}

    for presentItem in items:
        print(cnt,presentItem)
        cnt+=1
        
        similarities_matrix[presentItem]=computeSimiliartyScoresForAItem(items,presentItem,similarity)

    return similarities_matrix
       
def loadBooksDataFromCSV(path='C:/Users/Dell/Desktop/big-data-projo/code/data/books'):
# Get movie titles
    isbnToIdMapping={}
    books = pd.read_csv(path+"/bookDesc.csv")
    for idx,row in books.iterrows():
        print(idx,"Book Desc")
        (id,isbn)=(row['id'],row['isbn'])
        isbnToIdMapping[isbn]=id
    
    ratings = pd.read_csv(path+'/BX-Book-Ratings.csv')
    prefs=ratings.groupby('isbn').groups
    print(len(prefs))
    cnt=-1
    for isbnId in list(prefs.keys()):
        if isbnId not in isbnToIdMapping:
            del prefs[isbnId]
            continue
        cnt+=1
        
        # if cnt<20:
        prefs[isbnId]=getRatingsForAItemByISBN(isbnId,prefs,ratings)
        if cnt%100==0:
            print(cnt,isbnToIdMapping[isbnId],prefs[isbnId])
        prefs[isbnToIdMapping[isbnId]]=prefs[isbnId]
        del prefs[isbnId]
    print(len(prefs))
    return prefs

def getRatingRecordByID(ratings,index):
    result=ratings.loc[ratings['ID'] == index][ ['User-ID', 'Book-Rating'] ].values.tolist()[0]
    # print("getRatingRecordByID(ratings,index): ",result,index)
    return result

def getRatingsForAItemByISBN(isbnId,prefs,ratings_df):
    ratings={}
    for ratingIndex in prefs[isbnId]:
        userId,userRating=getRatingRecordByID(ratings_df,ratingIndex)
        ratings[userId]=userRating

    return ratings

def storeData(data,fileName):
    path='C:/Users/Dell/Desktop/big-data-projo/code/data/books/'
    dataFile = open(path+fileName, 'wb') 
      
    # source, destination 
    pickle.dump(data,dataFile)   
    # dataFile.write(str)                   
    dataFile.close() 
    print("Data stored successfully into file:{}".format(path+fileName))


def loadData(fileName): 
    # for reading also binary mode is important 
    path='C:/Users/Dell/Desktop/big-data-projo/code/data/books/'
    dbfile = open(path+fileName, 'rb')      
    db = pickle.load(dbfile) 
    dbfile.close() 
    print("Data Loaded successfully from file:{}".format(path+fileName))

    return db

def start():
    # data=loadBooksDataFromCSV()
    # storeData(data,'collab_inter_data')
    items=loadData('collab_inter_data')
    return items
    # print(items[223])
    # sim_items=computeSimiliartyScores(items)
    # storeData(sim_items,'collab_sim_items')
    # sim_items_data=loadData('collab_sim_items')
    # while True:
        # x,y=map(int,input().split())
        # print(sim_euclidean(items,x,y,1),sim_euclidean(items,x,y))
        # x=int(input())
        # print(computeSimiliartyScoresForAItem(items,x))
        # print(sim_items_data[x])
        # print(items[x],items[y])
    # print(getRecommendations(prefs,"6"))

# start()