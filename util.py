import numpy as np   
import pandas as pd
import requests
from bs4 import BeautifulSoup

centroids = np.genfromtxt('centroids.out',delimiter=',')
means = np.genfromtxt('means.out',delimiter=',')
stds = np.genfromtxt('stds.out',delimiter=',')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
url='https://world.openfoodfacts.org/product/'

def parsero(string,target='',scale=True):
    '''
    Searches product barcode (string argument) at openfoodfacts.org.
    Parses search results and returns rescaled nutrition vector (or 
    dataframe if multiple barcodes) with respect to 100 grams portion.
    Returs also the name of the product
    target is the nutrient which is targeted for optimization
    '''
    keys=['food:proteinsPer100g','food:fatPer100g',
          'food:carbohydratesPer100g','food:energyPer100g',
          'food:sugarsPer100g','food:fiberPer100g',
          'food:cholesterolPer100g','food:transFatPer100g',
          'food:saturatedFatPer100g','food:sodiumEquivalentPer100g']
    tmp=string.split(',')
    #tmp=list(map(str.strip,tmp))
    df=pd.DataFrame(columns=[ _[5:] for _ in keys])
    title=[]
    for i,cbar in enumerate(tmp):
        furl=url+cbar
        page = requests.get(furl, headers=headers)
        soup=BeautifulSoup(page.content, 'html.parser')
        title.append(soup.title.string.split('-')[0].strip())
        if ((title[-1] == 'Add a product') or 
            (title[-1] == 'Search results') or
            (title[-1] == 'Error')):
            del title[-1]
            title.append('<font color="red">Product not foud</font>')
        test=soup.find_all('td', class_="nutriment_value")  
        table={}
        for _ in test:
            if 'content' in _.attrs:
                table[_.attrs['property']]=float(_.attrs['content']) 
        values=[]
        for _ in keys:
            if _ in table:
                values.append(table[_])
            else:
                values.append(0)
        values[3]=values[3]/4.184 #converting kJoule into kcal
        #portion=float(tmp[0])
        x=np.asarray(values).reshape(1,10)
        if scale:
            x=(x-means)/stds #rescale x for computing distances
        df.loc[i]=x.reshape(10,)
    if target: #target not empty
        opt=target.split()[0]
        if opt=='most':
            best=df[target.split()[1]+'Per100g'].idxmax()
        else:
            best=df[target.split()[1]+'Per100g'].idxmin()
    else:
        best=np.nan
    return df,title,best

def distance(c,x):
    return np.linalg.norm(x - c)
    
def classifier(distances):
    '''
    Classifies, finds other close clusters and returns diagnostic string
    '''
    clusters={0:'Balanced', 1:'High sugars, high carbs',
         2:'High saturated fat',
         3:'High trans fat, high total fat',
         4:'High cholesterol, high protein',
         5:'High fiber, high protein',
         6:'High sodium'}
    cluster=distances.argmin()
    tmp =(distances/distances.min() <1.5) & (distances/distances.min() > 1)
    totNeigh=sum(tmp)
    output=clusters[cluster].upper()
    output=output+'<br />'
    j=0
    for i in range(totNeigh):
        output=output+ clusters[(np.argwhere(tmp == np.max(tmp))[i][0])] +'<br />'
        j+=1
    
    return output,j+1

def classifierInt(distances):
    '''
    Classifies, finds other close clusters and returns list of clusters as
    integers
    '''
    out=[]
    clusters=[]
    for _ in range(len(distances)):
        output=[]
        cluster=distances[_,:].argmin()
        tmp =(distances[_,:]/distances[_,:].min() <1.5) & (
                distances[_,:]/distances[_,:].min() > 1)
        totNeigh=sum(tmp.ravel()) #ravel makes 2D array into 1D
        output.append(cluster)
        j=0
        for i in range(totNeigh): #adding close neighbors to output
            output.append((np.argwhere(tmp == np.max(tmp))[i][0]))
            j+=1
        out.append(output)
        clusters.append(j+1)
    return out,clusters
  
def nutritionList(array):
    '''
    Creates list with text variables to be rendered into an html
    nutrition table (scaled according to 100 grams)
    '''
    df=pd.DataFrame(columns=list(range(16)))
    for i in range(len(array)):
        vect=array.iloc[i].values
        nlist=[]
        nlist.append('Calories '+str(int(round(vect[3])))) 
        nlist.append('Total Fat '+str(int(round(vect[1])))+'g')
        nlist.append(''+str(int(round(100*vect[1]/65)))+'%'+' ')
        nlist.append('Saturated Fat '+str(int(round(vect[8])))+'g')
        nlist.append(''+str(int(round(100*vect[8]/20)))+'%'+' ')
        nlist.append('Trans Fat '+str(int(round(vect[7])))+'g')
        nlist.append('Cholesterol '+str(int(round(vect[6]*1000)))+'mg')
        nlist.append(''+str(int(round(100*vect[6]/0.3)))+'%'+' ')
        nlist.append('Sodium '+str(int(round(vect[9]*1000)))+'mg') 
        nlist.append(''+str(int(round(100*vect[9]/2.4)))+'%'+' ')
        nlist.append('Total Carbohydrate '+str(int(round(vect[2])))+'g') 
        nlist.append(''+str(int(round(100*vect[2]/300)))+'%'+' ')
        nlist.append('Dietary Fiber '+str(int(round(vect[5])))+'g') 
        nlist.append(''+str(int(round(100*vect[5]/25)))+'%'+' ')
        nlist.append('Sugars '+str(int(round(vect[4])))+'g') 
        nlist.append('Protein '+str(int(round(vect[0])))+'g')
        df.loc[i]=nlist
    
    return df

def cluster2table(clusterList):
    '''
    Cluster to html nutrition table map indicating which entries
    have to be highlighted
    '''
    translator={1:[14,10,11],2:[3,4,15],3:[5],4:[6,7],
              5:[12,13],6:[8,9]}
    out=[]
    for _ in clusterList:
        output=[]
        for i in _:
            if i != 0:
                output.extend(translator[i])    
        out.append(output)
    return out

def decorations(nutList,tagList):
    '''
    color decorators for html nutrition table
    '''
    tagB={0:'<span style="background-color: #f6f959">',
        1:'<span style="background-color: #ff6347">',
        2:'<span style="background-color: #ff6347">',
        3:'<span style="background-color: #ff6347">',
        4:'<span style="background-color: #ff6347">',
        5:'<span style="background-color: #ff6347">',
        6:'<span style="background-color: #ff6347">',
        7:'<span style="background-color: #ff6347">',
        8:'<span style="background-color: #ff6347">', #red
        9:'<span style="background-color: #ff6347">',
        10:'<span style="background-color: #f6f959">',
        11:'<span style="background-color: #f6f959">',
        12:'<span style="background-color: #6bff74">',#green
        13:'<span style="background-color: #6bff74">',
        14:'<span style="background-color: #f6f959">',
        15:'<span style="background-color: #6bff74">'}
    for k in range(len(nutList)):#each row corresponds to a barcode
        for i in tagList[k]:#each list in tagList corresponds to each row
            nutList.iloc[k,i]=tagB[i]+nutList.iloc[k,i]+"</span>"

def adjectives(string,convert=False):
    '''
    adds an adjective before string, choosing between good or bad. 
    The values for good and bad list have to match the values returned
    from the variable "lookFor" which is entered through index.html.
    '''
    good=["fiber","proteins",'protein']
    output={"fiber":"fiber","proteins":'protein',"energy":'calories',
            "carbohydrates":"carbs","cholesterol":"cholesterol",
            "saturatedFat":"sat. fat","sodiumEquivalent":"salt",
         "sugars":"sugar","fat":"total fat","transFat":"trans. fat"}
    if convert:
        string=output[string.split()[1]]
    if string in good:
        string='most '+string
    else:
        string='least '+string
    return string
    
def simply_the_best(nutrient):
    '''
    find which of the products has the optimal value given 
    the nutrient constraint.
    '''
    