#!/usr/bin/env python
from flask import Flask, redirect, render_template, request, session, url_for
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from util import *

app = Flask(__name__)
dropzone = Dropzone(app)
app.config['SECRET_KEY'] = 'aVukl8HGGKn4i7V0nG00qwvc'

# Dropzone settings
app.config.update(
    DROPZONE_UPLOAD_MULTIPLE=True,
    #DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_REDIRECT_VIEW= 'calculate2',
    DROPZONE_MAX_FILE_SIZE=4,#4 MB image
    DROPZONE_MAX_FILES=5,
    DROPZONE_DEFAULT_MESSAGE='Drop <b>barcode images</b> here or click to upload.</br> (1 MB or less, unrelated images will be ignored)',
    #DROPZONE_UPLOAD_ON_CLICK=True,
    #DROPZONE_UPLOAD_ACTION='calculate2',  # URL or endpoint
    #DROPZONE_UPLOAD_BTN_ID='submit',
)

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

@app.route('/demo', methods=['GET'])
def demo():
   return render_template("demo.html")                

@app.route('/calculate', methods=['GET'])
def calculate():
   if request.method == 'GET':
      codes=request.args.get('barcodes')
      lookFor=''#request.args.get('nutrient')
      #lookFor=adjectives(lookFor) #qualify nutrient
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
          best='' #title[best]
      else:
          best='' #not going to be used anyway
      #lookFor=adjectives(lookFor,True) #convert output string for html  
   return render_template('calculate.html.j2',
                          nutrients=nutList,
                          clusters=nClust,names=title,lookFor=lookFor,
                          span=len(title),best=best)
   
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # set session for image results
    if 'bcode_urls' not in session:
        session['bcode_urls'] = []
    # list to hold our uploaded image urls
    bcode_urls = session['bcode_urls']
    # handle image upload from Dropszone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename    
            )
            # append image urls
            code=findBarcodes(Image.open('uploads/'+file.filename))
            if code != None:
                bcode_urls.append(code)

            os.remove('uploads/'+file.filename)

        session['bcode_urls'] = bcode_urls
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('index.html')

@app.route('/calculate2')
def calculate2():
    # redirect to home if no images to display
    if 'bcode_urls' not in session or session['bcode_urls'] == []:
        return redirect(url_for('index'))
        
    # set the file_urls and remove the session variable
    codes = session['bcode_urls']
    session.pop('bcode_urls', None)
    
    #if request.method == 'GET':
    lookFor='fiber'#request.args.get('nutrient')
    lookFor=adjectives(lookFor) #qualify nutrient
    nutritionVect=parsero2(codes,'',True)[0]#rescaled for distance computations
    contents,title,best=parsero2(codes,lookFor,False) #rescaled for 100g/html table
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
    #caca
    return render_template('calculate.html.j2',
                           nutrients=nutList,
                           clusters=nClust,names=title,lookFor=lookFor,
                           span=len(title),best=best)

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)
    #app.run(debug=True)
