#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 16:47:23 2019

@author: achakrab
"""

import requests
import os
import sys

from pyspark import SparkContext
import json
import os
import pandas as pd
import numpy as np

with open('coordinates.txt','r') as f:
    content1=f.readlines()
    
content1[0]=eval(content1[0])
    
#content[0]=eval(content[0])

content=content1[0]

for item in content:
    if item==list(content.keys())[0]:
        file=pd.concat((pd.DataFrame(data=np.asarray([item]*len(content[item]))),pd.DataFrame(np.asarray(content[item]))),axis=1)
    else:
        file=pd.concat((file,pd.concat((pd.DataFrame(data=np.asarray([item]*len(content[item]))),pd.DataFrame(np.asarray(content[item]))),axis=1)))
        
file.columns=['place','lat','long']

#filename='coordinatesascsv.txt'

file.to_csv('coordinatesascsv.csv') 

sc=SparkContext()

f=sc.textFile("smalllistofcoordinates.txt")

def mapf(x):
    words=x.split(',')
    return (words[0],words[1],words[2],words[3])

f1=f.map(mapf).filter(lambda x: x[0]!='')



os.chdir('picturess360')


def create_image(x):

    for heading in range(0,4):
        lat=x[1]
        long=x[2]
        location=x[3]
        heading=str(90*heading)
        query='https://maps.googleapis.com/maps/api/streetview?size=400x400&location=%s,%s&fov=90&heading=%s&pitch=10&key=AIzaSyD5auFkLCc2ywVruc-U5OtwfY5n-fkAe64' % (str(lat),str(long),heading)
        page=requests.get(query)
        filename='%s-%s-%s-%s.jpg' %(str(x[0]),str(lat),str(long),location.replace('/','-'))
        f = open(filename,'wb')
        f.write(page.content)    
        f.close()

f1.map(create_image).collect()