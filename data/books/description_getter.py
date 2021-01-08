import requests
import pandas as pd


def getBookDescByISBN(isbn):
    print("Logging req for:",isbn)
    baseUrl="https://www.googleapis.com/books/v1/volumes?q=isbn:"
    finalUrl=baseUrl+isbn

    response=requests.get(finalUrl).json()
    if 'items' not in response or "volumeInfo" not in response['items'][0] or "description" not in response['items'][0]["volumeInfo"] or "categories" not in response['items'][0]["volumeInfo"]:
        return ("notFound","notFound")
    return((response['items'][0]["volumeInfo"]["description"],response['items'][0]["volumeInfo"]["categories"][0]))

def isNaN(string):
    return string != string

def startGettingDesc():
    ds = pd.read_csv("C:/Users/Dell/Desktop/big-data-projo/code/data/books/bookDesc.csv")
    cnt=0
    for idx,row in ds.iterrows():
        # print(idx,row['description'],row['categories'],isNaN(row['description']))
        if isNaN(row['description']) or isNaN(row['categories']):
            description,categories=getBookDescByISBN(row['isbn'])
            if isNaN(row['description']):
                ds['description'][idx]=description
            if isNaN(row['categories']):
                ds['categories'][idx]=categories
            print(idx,description,categories,cnt)
            cnt+=1
        if cnt>3000:
            break

    ds.to_csv('C:/Users/Dell/Desktop/big-data-projo/code/data/books/bookDesc.csv',index=False)

def test():
    nme = ["aparna", "pankaj", "sudhir", "Geeku"] 
    deg = ["MBA", "BCA", "M.Tech", "MBA"] 
    scr = [90, 40, 80, 98] 
    
    # dictionary of lists  
    dict = {'name': nme, 'degree': deg, 'score': scr}  
        
    df = pd.DataFrame(dict) 
    
    # saving the dataframe 
    df.to_csv('C:/Users/Dell/Desktop/big-data-projo/code/data/books/file1.csv') 


startGettingDesc()