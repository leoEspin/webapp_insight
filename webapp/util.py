import numpy as np   
import requests
from bs4 import BeautifulSoup

centroids = np.genfromtxt('centroids.out',delimiter=',')
means = np.genfromtxt('means.out',delimiter=',')
stds = np.genfromtxt('stds.out',delimiter=',')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
url='https://world.openfoodfacts.org/product/'

def parsero(string,scale=True):
    '''
    Parses string and returns rescaled nutrition vector with 
    respect to 100 grams portion
    '''
    keys=['food:proteinsPer100g','food:fatPer100g',
          'food:carbohydratesPer100g','food:energyPer100g',
          'food:sugarsPer100g','food:fiberPer100g',
          'food:cholesterolPer100g','food:transFatPer100g',
          'food:saturatedFatPer100g','food:sodiumEquivalentPer100g']
    tmp=string.strip()
    furl=url+tmp
    page = requests.get(furl, headers=headers)
    soup=BeautifulSoup(page.content, 'html.parser')
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
    return x

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
    output=[]
    cluster=distances.argmin()
    tmp =(distances/distances.min() <1.5) & (distances/distances.min() > 1)
    totNeigh=sum(tmp)
    output.append(cluster)
    j=0
    for i in range(totNeigh): #adding close neighbors to output
        output.append((np.argwhere(tmp == np.max(tmp))[i][0]))
        j+=1
    
    return output,j+1
  
def nutritionList(vect):
    '''
    Creates list with text variables to be rendered into an html
    nutrition table (scaled according to 100 grams)
    '''
    nlist=[]
    nlist.append('Calories '+str(int(round(vect[0,3])))+'g') 
    nlist.append('Total Fat '+str(int(round(vect[0,1])))+'g')
    nlist.append(''+str(int(round(100*vect[0,1]/65)))+'%'+' ')
    nlist.append('Saturated Fat '+str(int(round(vect[0,8])))+'g')
    nlist.append(''+str(int(round(100*vect[0,8]/20)))+'%'+' ')
    nlist.append('Trans Fat '+str(int(round(vect[0,7])))+'g')
    nlist.append('Cholesterol '+str(int(round(vect[0,6]*1000)))+'mg')
    nlist.append(''+str(int(round(100*vect[0,6]/0.3)))+'%'+' ')
    nlist.append('Sodium '+str(int(round(vect[0,9]*1000)))+'mg') 
    nlist.append(''+str(int(round(100*vect[0,9]/2.4)))+'%'+' ')
    nlist.append('Total Carbohydrate '+str(int(round(vect[0,2])))+'g') 
    nlist.append(''+str(int(round(100*vect[0,2]/300)))+'%'+' ')
    nlist.append('Dietary Fiber '+str(int(round(vect[0,5])))+'g') 
    nlist.append(''+str(int(round(100*vect[0,5]/25)))+'%'+' ')
    nlist.append('Sugars '+str(int(round(vect[0,4])))+'g') 
    nlist.append('Protein '+str(int(round(vect[0,0])))+'g')
    return nlist

def cluster2table(clusterList):
    '''
    Cluster to html nutrition table map
    '''
    translator={1:[14,10,11],2:[3,4,15],3:[5],4:[6,7],
              5:[12,13],6:[8,9]}
    output=[]
    for i in clusterList:
        if i != 0:
            output.extend(translator[i])    
    return output

def decorations(nutList,tagList):
    '''
    color decorators for html nutrition table
    '''
    tagB={0:'<font color=#ff6347>',1:'<font color="red">',
      2:'<font color="red">',3:'<font color="red">',
      4:'<font color="red">',5:'<font color="red">',
      6:'<font color="red">',7:'<font color="red">',
      8:'<font color="red">',9:'<font color="red">',
      10:'<font color=#ff6347>',11:'<font color=#ff6347>',
      12:'<font color="green">',13:'<font color="green">',
      14:'<font color=#ff6347>',15:'<font color="green">'}
    for i in tagList:
        nutList[i]=tagB[i]+nutList[i]+'</font>'
    
    