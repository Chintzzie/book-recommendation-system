import collab_filtering_recommender as cfr
import content_based_recommender as cbr

cfr_items=cfr.start()
cbr_sim_items=cbr.start()

def getCBRSimilarItemsForAItem(itemId):

    if itemId not in cbr_sim_items:
        # print("Item with itemId={}, is not analyzed by CBR and so no similar items".format(itemId))
        return []

    return cbr_sim_items[itemId]

def getCFRSimilarItemsForAItem(itemId):
    return cfr.computeSimiliartyScoresForAItem(cfr_items,itemId)

def getTransformedSimilarItems(sim_items,itemId):
    transformed_sim_items=[]

    for cbr_score,cbr_itemId in sim_items:
        cfr_score,matching_users,avg_rating=cfr.sim_euclidean(cfr_items,itemId,cbr_itemId)
        transformed_sim_items.append((cbr_itemId,cbr_score,cfr_score,matching_users,avg_rating))

    return transformed_sim_items

def getHybridSimilarItemsForAItem(itemId,num_of_items=100,initial_num_of_items=1000):
    
    sim_items=getCBRSimilarItemsForAItem(itemId)[:initial_num_of_items]

    transformed_sim_items=getTransformedSimilarItems(sim_items,itemId)

    transformed_sim_items.sort(key=lambda x:(x[2],x[3],x[4]),reverse=True)

    return transformed_sim_items[:num_of_items]

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
    userId=int(input())
    
    paintDict("User Detail",cbr.getUserDetail(userId))
    cbr.displayPreviouslyUsedItemsByAUser(cbr.getUser(userId))
    paint("CBR Users",getCBRSimilarItemsForAUser(userId))
    paint("CFR Users",getCFRSimilarItemsForAUser(userId))
    paint("Hybrid Users",getHybridSimilarItemsForAUser(userId))

def processQueryByItemId():
    print("Enter ItemId ")
    itemId=int(input())

    paintDict("Item Info",cbr.getItemDetail(itemId))
    paint("CBR Items",getCBRSimilarItemsForAItem(itemId),printableMatterIndex=1)
    paint("CFR Items",getCFRSimilarItemsForAItem(itemId))
    paint("Hybrid Items",getHybridSimilarItemsForAItem(itemId))

while True:

    print("Select any one \n1.Recommendations by UserID \n2.Recommendations by ItemID")
    choice=int(input())
    
    if choice==1:
        processQueryByUserId()
    elif choice==2:
        processQueryByItemId()
    else:
        print("Bye--Bye")
        break


