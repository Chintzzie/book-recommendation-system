import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import re 
wnl = WordNetLemmatizer()
porter_stemmer = PorterStemmer()

results={}
IdsPresent={}
IndexToIdMapping={}
users={}
ratings={}

extendedUsers={}

path="C:/Users/Dell/Desktop/big-data-projo/code/data/books/"
actualds = pd.read_csv(path+"bookDesc.csv")
df_users = pd.read_csv(path + "BX-Users.csv", sep=';', encoding="ISO-8859-1")
df_ratings = pd.read_csv(path + "BX-Book-Ratings.csv")



def stemming_tokenizer(str_input):
    words = re.compile('[A-Za-z0-9]+').findall(str_input)
    # print(words)
    words = [porter_stemmer.stem(word) for word in words]
    return words

def performSimilarityComputation():
    ds = actualds[actualds['description'].notnull()].copy()
    usersPerIsbn = df_ratings['isbn'].value_counts()
    # print(ds.shape)
    ds = ds[ds['isbn'].isin(usersPerIsbn[usersPerIsbn>20].index)]
    # print(ds.shape)
    IndexToIdMapping={}
    index=0
    for idx,row in ds.iterrows():
        IndexToIdMapping[index]=idx
        IdsPresent[idx]=index
        index+=1
    tf = TfidfVectorizer(analyzer='word',stop_words='english')
    tfidf_matrix = tf.fit_transform(ds['description']+ds['author']+ds['title']+ds['categories'])
    # print(len(tf.get_feature_names()))

    # print("TFIDF Matrix Shape=",tfidf_matrix.shape)
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    # print("COsine similarities shape=",cosine_similarities.shape)

    index=0
    for idx, row in ds.iterrows():

        similar_indices = cosine_similarities[index].argsort()[:-1500:-1]
        similar_items = [(cosine_similarities[index][i], IndexToIdMapping[i] ) for i in similar_indices if IndexToIdMapping[i]!=idx]
        # if idx==2:
        #     print(similar_items,idx)
        results[row['id']] = similar_items
        index+=1
        
    print('CBR: Similarity Computation Done')

def getItemTitle(id):
    title=actualds.loc[actualds['id'] == id]['title'].tolist()
    # print("title={}".format(title[0]))
    return str(title[0])

def getItemDetail(id):
    item_detail=actualds.loc[actualds['id'] == id].values.tolist()[0]
    indexToTitleMapping=['id','isbn','title','author','pub-year','publisher','category','description']
    item={}
    for index in range(len(indexToTitleMapping)):
        item[indexToTitleMapping[index]]=item_detail[index]
    return item

def getUserDetail(id):
    user_detail=df_users.loc[df_users['ID'] == id].values.tolist()[0]
    indexToTitleMapping=['id','location','age']
    user={}
    for index in range(len(indexToTitleMapping)):
        user[indexToTitleMapping[index]]=user_detail[index]
    return user

def getItemDesc(id):
    desc=actualds.loc[actualds['id'] == id]['description'].tolist()
    return str(desc[0])

# Just reads the results out of the dictionary.
def recommend(item_id, num):
    # print(item_id,IdsPresent[item_id])
    if item_id not in IdsPresent:
        print("No recommendations for {} since there is no summary".format(item_id))
        return

    print("Recommending " + str(num) + " products similar to " + getItemTitle(item_id) )
    print(getItemDesc(item_id))
    print("-------")
    recs = results[item_id][:num]
    for score,id in recs:
        print("Recommended: " + getItemTitle(id) + " (score:" + str(score) + ")")
        print(getItemDesc(id))
    print("------")

def startRecommendation():
    while True:
        item_id=int(input())
        recommend(item_id=item_id, num=2)

def addRating(user_id,book_id,rating):
    global extendedUsers

    if user_id not in extendedUsers:
        getUser(user_id)

    print("CBR: Before Rating modified",extendedUsers[user_id])

    extendedUsers[user_id]['ratings'][book_id]=rating

    print("CBR: Added Rating",extendedUsers[user_id])

def getUser(user_id):

    global extendedUsers

    if user_id in extendedUsers:
        return extendedUsers[user_id]


    user=users[user_id]
    if user_id not in ratings:
        user['ratings']={}
        return user
    userRatings=ratings[user_id]
    # print("user ratings=",userRatings)
    for id in userRatings:
        # print(id)
        if "ratings" not in user:
            user['ratings']={}
        isbn,rating=df_ratings.loc[df_ratings['ID']==id][["isbn","Book-Rating"]].values.tolist()[0]
        # print(id,isbn,rating)
        bookId=actualds.loc[actualds['isbn']==isbn][['id']].values.tolist()
        if len(bookId)==1:
            bookId=bookId[0][0]
            user['ratings'][bookId]=rating

    extendedUsers[user_id]=user

    return user
    # user['ratings']=

def computeSimilarItemListForAUser(user,num_of_items=100):
    sim_items={}
    for bookId in user['ratings'].keys():
        if bookId not in results:
            continue
        for score,itemId in results[bookId]:
            if itemId in sim_items:
                sim_items[itemId]+=score
            else:
                sim_items[itemId]=score

    sim_items_list=[]
    for itemId,score in sim_items.items():
        sim_items_list.append((itemId,score))

    sim_items_list.sort(key=lambda x: (x[1]),reverse=True)

    if len(sim_items_list)>num_of_items:
        return sim_items_list[:num_of_items]
    else:
        return sim_items_list

def getAllRatingRecordsForAllUsers():
    # print("Getting records")
    # ratingsOfUser=df_ratings.loc[df_ratings["User-ID"]==user_id][['isbn','Book-Rating']]
    # ratingsOfUser= ratingsOfUser.to_dict('records')
    ratingsOfUser=df_ratings.groupby('User-ID').groups
    # print("got records")
    return (ratingsOfUser)

def getAllUsers():
    global users
    global ratings
    # user_id=276746
    # print("Getting dict")
    users=df_users.set_index('ID').to_dict('index')
    # print("Got dict")
    # print(users[user_id])
    # for user_id in users.keys():
    #     users[user_id]['ratings']=getAllRatingRecordsForAUser(user_id)
    # print(users[user_id])
    ratings=getAllRatingRecordsForAllUsers()
    # print(users[user_id],ratings[user_id])
    print("Got all user data!")

def displayPreviouslyUsedItemsByAUser(user):
    if len(user['ratings'].keys())==0:
        print("There are no previously Used Items for this user")
        return
    print("------------Previously Used Items-----------")

    for itemId in user['ratings'].keys():
        
        print(getItemTitle(itemId),itemId)

def displayRecommendationsForAUser(sim_items_list):
    if len(sim_items_list)==0:
        print("Since there are no previously Used Items for this user,there are no recommendations")
        return
    print("------------Recommendation Items-----------")
    for itemId,score in sim_items_list:
        print(getItemTitle(itemId),itemId,score)

def getRecommendationsForAUser(userId):
    if userId not in users:
        print("No user with such an ID")
        return
    user=getUser(userId)
    sim_items_list=computeSimilarItemListForAUser(user)
    displayPreviouslyUsedItemsByAUser(user)
    displayRecommendationsForAUser(sim_items_list)

def preCompute():
    performSimilarityComputation()
    getAllUsers()


def start():
    preCompute()
    return results

    # while(True):
    #     print("Enter userId to get recommendations")
    #     userId=int(input())
    #     getRecommendationsForAUser(userId)

# start()


