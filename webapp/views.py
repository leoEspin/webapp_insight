from webapp import app
from flask import render_template, request
from webapp.util import *



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
      code=request.args.get('statement1')
      nutritionVect=parsero(code,True)#rescaled for 100g and distance computations
      contents=parsero(code,False) #rescaled for 100g
      #distances from centroids
      distances=np.apply_along_axis(distance, 1, centroids,nutritionVect) 
      neighbors,nClust=classifierInt(distances)
      nutList=nutritionList(contents) #nutrition strings for html table
      decorations(nutList,cluster2table(neighbors))#color warning decorations
   return render_template('calculate.html.j2',
                          nutrients=nutList,
                          clusters=nClust)
