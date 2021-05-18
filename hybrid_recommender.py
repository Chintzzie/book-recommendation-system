from numpy.core.numeric import True_
import collab_filtering_recommender as cfr
import content_based_recommender as cbr
import random
import math
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
            print("    {}   {}".format(cbr.getItemTitle( item[printableMatterIndex] ) ,item[0]) )
    print("-------------- END ---------------")
    print()

def paintDict(title,data):
    print(title)
    for key,val in data.items():
        print("{}:- {}".format(key,val))
    print()

def magnitude(vector):
    res=0
    for x,y in vector.items():
        res+=y*y
    return math.sqrt(res)

def multVector(A,B):

    C,D=A,B

    res=0

    for x,y in C.items():
        if x not in D:
            continue
        res+=y*D[x]

    return res

def dotVector(A,B):
    numerator=multVector(A,B)
    denominator=magnitude(A)*magnitude(B)
    if denominator==0:
        return 0
    return numerator/denominator


def printFocusPoints(vector,title):

    listt=[]
    for i,j in vector.items():
        listt.append((i,j))

    listt.sort(key=lambda x:x[1],reverse=True)

    print("Focal Points of {} recommendation are-".format(title))
    for i in range(min(5,len(listt))):
        print(listt[i][0],end=",")

    print()

def getVector(Items,Attributes,title):



    vector={}

    for itemId,score in Items:

        try:
            item=cbr.getItemDetail(itemId)

        except:
            continue

        for attribute in Attributes:
            entity=item[attribute]
            if entity not in vector:
                vector[entity]=0
            vector[entity]+=1

    print() 
    printFocusPoints(vector,title)

    return vector





def computeMetrics(CBR,CFR,Hybrid,Attributes):
    print("Insights regarding recommendations")

    CBRV,CFRV,HybridV=getVector(CBR,Attributes,"CBR"),getVector(CFR,Attributes,"CFR"),getVector(Hybrid,Attributes,"hybrid")
    
    #print("Vectors generated")

    CBRCFR=dotVector(CBRV,CFRV)
    CBRHyb=dotVector(CBRV,HybridV)
    CFRHyb=dotVector(CFRV,HybridV)
    final=CBRCFR*CBRHyb*CFRHyb

    print("Convergence score=",final)

    #print("Leaving computemTerics")



def processQueryByUserId():
    print("Enter UserId ")
    
    #try:

    userId=int(input())
    paintDict("User Detail",cbr.getUserDetail(userId))
    cbr.displayPreviouslyUsedItemsByAUser(cbr.getUser(userId))

    CBRItems=getCBRSimilarItemsForAUser(userId)
    CFRItems=getCFRSimilarItemsForAUser(userId)
    HybridItems=getHybridSimilarItemsForAUser(userId)

    computeMetrics(CBRItems,CFRItems,HybridItems,["category","author"])

    paint("CBR Users",CBRItems)
    paint("CFR Users",CFRItems)
    paint("Hybrid Users",HybridItems)

    """except:
        print("Invalid UserId")
        return  """

def processQueryByItemId():
    print("Enter ItemId ")
    

    try:

        itemId=int(input())
        paintDict("Item Info",cbr.getItemDetail(itemId))

        CBRItems=getCBRSimilarItemsForAItem(itemId)
        CFRItems=getCFRSimilarItemsForAItem(itemId)
        HybridItems=getHybridSimilarItemsForAItem(itemId)

        #computeMetrics(CBRItems,CFRItems,HybridItems,["category","author"])

        paint("CBR Items",CBRItems,printableMatterIndex=1)
        paint("CFR Items",CFRItems)
        paint("Hybrid Items",HybridItems)

    except:
        print("Invalid ItemId")
        return 

def getUserDetail():
    print("Enter UserId ")
    
    try:
        userId=int(input())
        paintDict("User Detail",cbr.getUserDetail(userId))
    except:
        #raise("Invalid userId")
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


def addRating():
    print("Enter userId,bookId,rating seperated by spaces")
    inps=list(map(int,input().split()))
    try:
        cbr.getUserDetail(inps[0])
        cbr.getItemDetail(inps[1])
    except:
        print("Invalid userId or itemId")
        return

    try:

        cbr.addRating(inps[0],inps[1],inps[2])
    except:
        print("Mismatch in no. of input values")


def searchForItems(searchTerm,userId,attributes=['title','author','pub-year','publisher','category','description']):

    hybridItems=getHybridSimilarItemsForAUser(userId,1000)

    hybridItemsExtended=[]
    for hybridItem in hybridItems:

        id,simScore=hybridItem[0],hybridItem[1]
        
        item=cbr.getItemDetail(id)
        

        text=""
        for attribute in attributes:
            text+=str(item[attribute])

        text=text.lower()

        searchScore=getScoreForText(text,searchTerm)

        hybridItemsExtended.append((id,searchScore,simScore))

    hybridItemsExtended.sort(key=lambda x:( x[1],x[2] ),reverse=True)

    print(hybridItemsExtended[:20])

    return hybridItemsExtended








def getScoreForText(text,searchTerm):
    score=0

    wordsInSearchTerm=searchTerm.split()
    for wordInSearchTerm in wordsInSearchTerm:
        adder=len(wordInSearchTerm)
        wordsInText=text.split()

        wordsInTextFreq={}
        for i in wordsInText:
            if i not in wordsInTextFreq:
                wordsInTextFreq[i]=0
            wordsInTextFreq[i]+=1

        if wordInSearchTerm in wordsInTextFreq:
            score+=adder*wordsInTextFreq[wordInSearchTerm]

    return score


def search():
    print("Enter userId and search term")
    userId,searchTerm=input().split()
    userId=int(userId)

    paint("Search results",searchForItems(searchTerm,userId))


while True:

    print("\nSelect any one \n1.Get user recommendations \n2.Get similar items\n3.Print user Info\n4.Get item info\n5.Add Rating to a Item\n6.Search for item\n7.Exit\n")
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
        addRating() 
    elif choice==6:
        search()   
    elif choice==7:
        print("bye-bye")
        break
    else:
        print("Invalid Input")
        continue
        


