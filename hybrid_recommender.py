import collab_filtering_recommender as cfr
import content_based_recommender as cbr
import random
from matplotlib import pyplot as plt



cfr_items=cfr.start()
cbr_sim_items=cbr.start()

def getCBRSimilarItemsForAItem(itemId):

    if itemId not in cbr_sim_items:
        # print("Item with itemId={}, is not analyzed by CBR and so no similar items".format(itemId))
        return []

    # items=cbr_sim_items[itemId][:100]
    # scores,ids=zip(*items)
    # print(items,scores)
    # plt.scatter(["Content Based" for i in range(len(scores))],scores)
    # plt.title("Similarity Score Trends")
    # plt.ylabel("Similarity Score")
    # plt.show()
    return cbr_sim_items[itemId]

def getCFRSimilarItemsForAItem(itemId):
    items=cfr.computeSimiliartyScoresForAItem(cfr_items,itemId)
    
    # citems=items[:100]
    # y=[]
    # for id,s,m,r in citems:
    #     y.append(s*m*r/24)
    # plt.scatter(["Collaborative Filtering" for i in range(len(y))],y)
    # plt.title("Similarity Score Trends")
    # plt.ylabel("Similarity Score")
    # plt.show()
    return items

def getTransformedSimilarItems(sim_items,itemId):
    transformed_sim_items=[]

    for cbr_score,cbr_itemId in sim_items:
        cfr_score,matching_users,avg_rating=cfr.sim_euclidean(cfr_items,itemId,cbr_itemId)
        transformed_sim_items.append((cbr_itemId,cbr_score,cfr_score,matching_users,avg_rating))

    return transformed_sim_items

def getHybridSimilarItemsForAItem(itemId,num_of_items=100,initial_num_of_items=1000):
    

    if len(getCBRSimilarItemsForAItem(itemId))==0:
        sim_items=getCBRSimilarItemsForAItem(156)[:initial_num_of_items]
    else:
        sim_items=getCBRSimilarItemsForAItem(itemId)[:initial_num_of_items]
    

    transformed_sim_items=getTransformedSimilarItems(sim_items,itemId)

    transformed_sim_items.sort(key=lambda x:(x[2],x[3],x[4]),reverse=True)


    items=transformed_sim_items[:num_of_items]
    # scores,ids=zip(*items)
    # citems=items[:100]
    # y=[]
    # for id,cs,cfs,m,r in citems:
    #     y.append(cs)
    # plt.scatter(["Hybrid Filtering" for i in range(len(y))],y)
    # # print("Hybrid",items)
    # plt.title("Similarity Score Trends")
    # plt.ylabel("Similarity Score")
    # plt.show()
    return items

def getCBRSimilarItemsForAUser(userId,num_of_items=100):
    user=cbr.getUser(userId)
    sim_items=cbr.computeSimilarItemListForAUser(user)
    return sim_items[:num_of_items]

def getCFRSimilarItemsForAUser(userId,num_of_items=100):
    user=cbr.getUser(userId)
    sim_items={}
    for bookId in user['ratings'].keys():

        for itemId,cfr_score,matches,avg_rating in getCFRSimilarItemsForAItem(bookId):
            if itemId in sim_items:
                sim_items[itemId]+=cfr_score*matches*avg_rating
            else:
                sim_items[itemId]=cfr_score*matches*avg_rating

    sim_items_list=[]
    for itemId,score in sim_items.items():
        sim_items_list.append((itemId,score))

    sim_items_list.sort(key=lambda x: (x[1]),reverse=True)

    if len(sim_items_list)>num_of_items:
        return sim_items_list[:num_of_items]
    else:
        return sim_items_list

def getHybridSimilarItemsForAUser(userId,num_of_items=100):
    user=cbr.getUser(userId)
    sim_items={}
    if(len(user['ratings'].keys()))==0:
        for itemId,cbr_score,cfr_score,matches,avg_rating in getHybridSimilarItemsForAItem(156):
            randFactor=random.randint(1,10)
            if itemId in sim_items:
                sim_items[itemId]+=randFactor+cbr_score+cfr_score*matches*avg_rating
            else:
                sim_items[itemId]=randFactor+cbr_score+cfr_score*matches*avg_rating

    else:

        for bookId in user['ratings'].keys():

            for itemId,cbr_score,cfr_score,matches,avg_rating in getHybridSimilarItemsForAItem(bookId):
                if itemId in sim_items:
                    sim_items[itemId]+=cbr_score+cfr_score*matches*avg_rating
                else:
                    sim_items[itemId]=cbr_score+cfr_score*matches*avg_rating

    sim_items_list=[]
    for itemId,score in sim_items.items():
        sim_items_list.append((itemId,score))

    sim_items_list.sort(key=lambda x: (x[1]),reverse=True)

    if len(sim_items_list)>num_of_items:
        return sim_items_list[:num_of_items]
    else:
        return sim_items_list

def paint(title,items,num_of_items=10,printableMatterIndex=0):
    if len(items)>num_of_items:
        items=items[:num_of_items]
    print("-------------- {} ---------------".format(title))
    # print(items)
    if len(items)==0:
        print("No item recommendations available for this datapoint!")
    else:
        for item in items:
            print("    {}".format(cbr.getItemTitle( item[printableMatterIndex] ) ) )
    print("-------------- END ---------------")
    print()

def paintDict(title,data):
    print(title)
    for key,val in data.items():
        print("{}:- {}".format(key,val))
    print()

def processQueryByUserId():
    print("Enter UserId ")
    
    try:
        userId=int(input())
        paintDict("User Detail",cbr.getUserDetail(userId))
        cbr.displayPreviouslyUsedItemsByAUser(cbr.getUser(userId))
        paint("CBR Users",getCBRSimilarItemsForAUser(userId))
        paint("CFR Users",getCFRSimilarItemsForAUser(userId))
        paint("Hybrid Users",getHybridSimilarItemsForAUser(userId))
    except:
        print("Invalid UserId")
        return

def processQueryByItemId():
    print("Enter ItemId ")
    

    try:
        itemId=int(input())
        paintDict("Item Info",cbr.getItemDetail(itemId))
        paint("CBR Items",getCBRSimilarItemsForAItem(itemId),printableMatterIndex=1)
        paint("CFR Items",getCFRSimilarItemsForAItem(itemId))
        paint("Hybrid Items",getHybridSimilarItemsForAItem(itemId))
    except:
        print("Invalid ItemId")
        return

def getUserDetail():
    print("Enter UserId ")
    
    try:
        userId=int(input())
        paintDict("User Detail",cbr.getUserDetail(userId))
    except:
        print("Invalid UserId")
        return
def getItemDetail():
    
    
    try:
        print("Enter ItemId ")
        itemId=int(input())
        paintDict("Item Info",cbr.getItemDetail(itemId))
    except:
        print("Invalid ItemId")
        return

while True:

    print("\nSelect any one \n1.Recommendations by UserID \n2.Recommendations by ItemID\n3.Get user detail\n4.Get item detail\n5.Exit\n")
    choice=int(input())
    
    if choice==1:
        processQueryByUserId()
    elif choice==2:
        processQueryByItemId()
    elif choice==3:
        getUserDetail()
    elif choice==4:
        getItemDetail()
    elif choice==5:
        print("bye-bye")
        break
    else:
        print("Invalid Input")
        continue
        


