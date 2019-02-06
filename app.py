#!/usr/bin/env python

from flask import Flask,render_template, request
from util import *


app = Flask(__name__)

#@app.template_filter('nl2br')
#def nl2br(s):
#	return s.replace("\n", "<br />")

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
   return render_template("index.html")                

@app.route('/calculate', methods=['GET'])
def calculate():
   if request.method == 'GET':
      codes=request.args.get('barcodes')
      lookFor=request.args.get('nutrient')
      lookFor=adjectives(lookFor) #qualify nutrient
      nutritionVect=parsero(codes,'',True)[0]#rescaled for distance computations
      contents,title,best=parsero(codes,lookFor,False) #rescaled for 100g/html table
      #distances from centroids
      distances=np.zeros((len(contents),len(centroids)))
      for i in range(len(contents)):
          distances[i,:]=np.apply_along_axis(distance, 1,
                    centroids,nutritionVect.iloc[i].values)
      neighbors,nClust=classifierInt(distances)
      nutList=nutritionList(contents) #nutrition strings for html table
      decorations(nutList,cluster2table(neighbors))#color warning decorations
      
      if len(title)>1:
          best=title[best]
      else:
          best='' #not going to be used anyway
      lookFor=adjectives(lookFor,True) #convert output string for html  
   return render_template('calculate.html.j2',
                          nutrients=nutList,
                          clusters=nClust,names=title,lookFor=lookFor,
                          span=len(title),best=best)
   
if __name__ == '__main__':
    #app.run(host='0.0.0.0',debug=False)
    app.run(debug=True)
