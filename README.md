# RoadScanner
This UC Berkeley Master of Information in Data Science capstone project was developed by
[Spyros Garyfallos](mailto:spiros.garifallos@berkeley.edu), [Sergio Ferro](mailto:sm.ferro54@ischool.berkeley.edu), 
[Kaitlin Swinnerton](mailto:kswinnerton@ischool.berkeley.edu) and [Arjun Chakraborty](archakra@ischool.berkeley.edu)

## Product Concept
Our goal is to improve the way people make decisions about how and where to travel. Current routing algorithms are missing 
an entire category of information when evaluating possible routes: the aesthetic beauty and quality of the drive. 
This is where Road Scanner comes in. Our purpose is to leverage state of the art machine learning
techniques to enable travelers to optimize their travel experience by providing a qualitative rating of a route’s beauty.  


## Our Vision
We will use Google Street View images to train a neural network to classify a route based on scenic quality.  
Then, in order to account for the different conditions travelers might encounter on their trips, we will use GAN networks 
to generate predictive images of the route aesthetic under different conditions. We will then be able to take a single
street view image and generate predictions of what that scene would like at dusk, at night, and in the winter. 
Finally, our website will take a user specified google maps route and display the route’s scenic rating along with 
example images showing what the route would look like under each potential travel condition. 
This will allow the user to identify the most enjoyable route for their trip, so they can fill their soul with beauty
instead of crushing it with concrete.  

## Under the Hood 

### Our Data

To train our models, we downloaded google street view images from known scenic and non-scenic routes in California. 
We chose California for a few reasons: the first being that we are UC Berkeley students and we wanted to honor our 
university’s state. We also have two team members who currently live in California, and one who has lived in California 
her whole life - both in northern and southern California. Our Californians are able to leverage their experiences 
from driving all over the state in every stage of this process: from product concept, to route classification, to data QA. 
You can call them domain experts in driving around California. But finally and most importantly, California offers a large 
diversity of terrain. Our scenic routes include views of mountains, lakes, oceans, deserts, rolling hills, and even wine 
country. The variability of the terrain will allow us to train a model that can generalize to other locations across the 
globe using pictures from just one state. 


So specifically, 24 scenic routes were identified from the website, 
[www.myscenicdrives.com](https://www.myscenicdrives.com), and the non-scenic routes were identified by our team’s local 
Californians. 

### Our Tech
1. **Scenic vs. non-scenic classification**

    We then began the first step of our model development by training networks to classify images as scenic vs non-scenic. 
We trained 11 different architectures on a V100 GPU and 64 RAM GB cloud server. The best performing model was a VGG19 
with an attention layer. It yielded a validation accuracy of 94% and was able to run inference on a batch of hundreds of 
images in under a second. 

    Training Results                 |  Attention maps
    :-------------------------------:|:-----------------------------:
    <img src="/example_images/tb.png" width="300"> | <img src="/example_images/attMap.png" width="300">

    We confirmed the validity of the model by rendering the attention layer maps for some 
high-confidence samples. We found that that the network learned to confidently detect the non-scenic pictures by the 
fact that the sky starts where the road ends, which is an indication of low interest features or generally featureless 
pictures.  

    Scenic Route Example             | Non-Scenic Route Example
    :-------------------------------:|:-----------------------------:
    <img src="/example_images/mendocino_original.jpg" width="300"> | <img src="/example_images/bakersfield_original.jpg" width="300">


2. **Seasonality Compensation**  

    The second step was to expand the generalizability of the model. Most of the Google Street View images are shot 
    in spring or summer, but in reality, people travel every day throughout the year and want to know what to expect 
    at any given moment. 
    We ended up training three CycleGANs to generate the missing pictures. CycleGANS are based on pix2pix, an image 
    to image translation network architecture, but with the difference of not requiring paired training data. Over 
    time, our CycleGANs learned to map the latent space between the two training domais.
    
    CycleGAN: Zebra/horse mapping example
    
    <img src='/example_images/horse2zebra.gif' align="center" width=500>
    
    
        
    Therefore, in order to give accurate scenic ratings of a route traveled in say, December, 
    we trained a cycle GAN network to transform the images from summer to winter. The model is able to adjust the 
    lighting and texture of the image to produce a representation of what the view from the car would look like in 
    the winter.   
    
    Examples  
    
    Original Photo                   |  Winter Transformation
    :-------------------------------:|:-----------------------------:
    <img src="/example_images/big_sur_original.jpg" width="300"> | <img src="/example_images/big_sur_winter.jpg" width="300">
    

    
    
    
3. **Time of Day Compensation**  

     Our third step was to account for the fact that not every trip is made during daylight hours. We trained two more 
     CycleGAN networks to transform the pictures from day to dusk and from day to night.  
     
     
    Examples  

    Original Photo                   |  Dusk Transformation          | Night Transformation
    :-------------------------------:|:-----------------------------:|:-----------------------------:
    <img src="/example_images/tahoe_original.jpg" width="200"> | <img src="/example_images/tahoe_dusk.jpg" width="200">| <img src="/example_images/tahoe_night.jpg" width="200">  

        


## Our website
We built a website to display scenic scoring and example images for a given Google Maps route. The demo is [here](http://people.ischool.berkeley.edu/~sm.ferro54/w209/)
