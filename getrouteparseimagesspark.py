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
from os import path

from PIL import Image
import numpy as np
import shutil

filename=''
origin='24 Willie Mays Plaza'
destination='1000 S Prairie Ave'
apikey=''
waypoints=['']
def make_lat_long_file(origin,destination,waypoints):
    
    bk = apikey
    BASE_URL_DIRECTIONS = 'https://maps.googleapis.com/maps/api/directions/json?'
    origin = 'origin=%s' %(('+').join(origin.split(' ')))
    destination = 'destination=%s' %(('+').join(destination.split(' ')))
    #waypoints = 'waypoints=via:CA-29'
    waymap=[('+').join(item) for item in waypoints]
    waypoints = 'waypoints=%s' %(('|').join([item for item in waymap]))#&waypoints=Charlestown,MA|via:Lexington,MA
    key = '&key=' + bk
    global url
    url = BASE_URL_DIRECTIONS + origin + '&' + destination + waypoints + key
    global r
    r = requests.get(url)
    
    lat_lng = []
    distance = 0
    for i in range(len(r.json()['routes'][0]['legs'])):
        #print('big',r.json()['routes'][0]['legs'][i]['end_location']) #These are included in the steps
        #print('big',r.json()['routes'][0]['legs'][i]['start_location']) #These are included in the steps
        for j in range(len(r.json()['routes'][0]['legs'][i]['steps'])):
            distance += r.json()['routes'][0]['legs'][i]['steps'][j]['distance']['value']
            end = r.json()['routes'][0]['legs'][i]['steps'][j]['end_location']
            start = r.json()['routes'][0]['legs'][i]['steps'][j]['start_location']
            lat_lng += [(start['lat'],start['lng']),(end['lat'],end['lng'])]
            
    def get_int_coords_from_json(r):
        lat_lng = []
        distance = 0
        for i in range(len(r.json()['routes'][0]['legs'])):
            for j in range(len(r.json()['routes'][0]['legs'][i]['steps'])):
                distance += r.json()['routes'][0]['legs'][i]['steps'][j]['distance']['value']
                end = r.json()['routes'][0]['legs'][i]['steps'][j]['end_location']
                start = r.json()['routes'][0]['legs'][i]['steps'][j]['start_location']
                lat_lng += [(start['lat'],start['lng']),(end['lat'],end['lng'])]
        up = list(set(lat_lng))
        n = round((distance/300)/len(unique_points_original))
        upi = []
        for i in range(len(up)-1):
            upi += list(map(tuple,np.linspace(unique_points_original[i],unique_points_original[i+1],interpolator_n)))
        upi = sorted(list(set(upi)),key = lambda x: x[0])
        return upi
    
    unique_points_original = list(set(lat_lng))
    interpolator_n = round((distance/300)/len(unique_points_original)) #one picture every 300 mts
    global unique_points_interpol
    unique_points_interpol = []
    for i in range(len(unique_points_original)-1):
        unique_points_interpol += list(map(tuple,np.linspace(unique_points_original[i],unique_points_original[i+1],interpolator_n)))
    
    unique_points_interpol = sorted(list(set(unique_points_interpol)),key = lambda x: x[0])
    
    unique_points_interpol
    
    def create_path(points):
        path = 'path='
        for i in points:
            path += str(i[0]) + ',' + str(i[1]) + '|'
        return path[:-1] #remove last '|'
    def get_coords(r,points):
        for i in r.json()['snappedPoints']:
            points += [(i['location']['latitude'],i['location']['longitude'])]
        return points
    
    BASE_URL_SNAP = 'https://roads.googleapis.com/v1/snapToRoads?'
    interpolate = '&interpolate=true'
    points = []
    k = 0
    coords_list = []
    
    while k <= len(unique_points_interpol)-1:
        coords_list += [unique_points_interpol[k]]
        if (len(coords_list)%100==0) or (k+1==len(unique_points_interpol)): #When we have 100 points or we reach the end of the list.
            path = create_path(coords_list)
            url = BASE_URL_SNAP + path + interpolate + key
            r = requests.get(url)
            points += get_coords(r,points)
            coords_list = []
        k += 1
        
    with open('route.txt','w') as f:
        json.dump({'route':list(set(points))},f)

make_lat_long_file(origin,destination,waypoints)


##downloading images now

with open('route.txt','r') as f:
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

org_dest_string='%s-%s' %(origin,destination)

if org_dest_string not in os.listdir(os.getcwd())[0]:
    os.system('rm ./*')
    def create_image(x):
        
        for heading in range(0,4):
            lat=x[1]
            long=x[2]
            location=x[3]
            heading=str(90*heading)
            query='https://maps.googleapis.com/maps/api/streetview?size=400x400&location=%s,%s&fov=90&heading=%s&pitch=10&key=%s' % (str(lat),str(long),heading,apikey)
            page=requests.get(query)
            filename='%s-%s-%s-%s-%s-%s.jpg' %(origin,destination,str(x[0]),str(lat),str(long),location.replace('/','-'))
            if not path.exists(filename+".txt") or os.path.getsize(filename)<5*10^3:
                f = open(filename,'wb')
                f.write(page.content)    
                f.close()
    
    f1.map(create_image).collect()
