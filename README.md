# My Insight webapp repo
![alt text](static/logo.png "www.smartfoodchoice.info")

In the U.S. it is a know problem that [food labels are often difficult to interpret](https://www.npr.org/sections/thesalt/2019/01/24/688042266/grocery-shoppers-dont-always-know-what-s-best-for-them-can-better-food-labeling). In order to help customers make healthier food choices I add product-tailored visual cues to food labels to try to simplify their interpretation.

I used an *unsupervised learning* algorithm, K-means clustering, for creating a labeling system that highlights the most salient information of a given food product. In my webapp, the user inputs smartphone photos of the barcodes of the products of interest and the webapp will download the nutrient information and render the nutrition labels with selected  information highlighted.

You can test the webapp by cloning this repo, then building an image by running

`docker build -t smartfoodchoice .`

and then instantiating a container with 

`docker run --rm -p 5000:5000 smartfoodchoice`

Navigate to `http://0.0.0.0:5000/` to see the webapp in action.