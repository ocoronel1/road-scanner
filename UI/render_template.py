from flask import Flask, render_template, jsonify, request
import random
import numpy as np
import requests
import json 

#Get google key
with open('./static/js/config.js') as dataFile:
	data = dataFile.read()
	k = '&key=' + data[data.find('\'') : data.rfind('\'')+1].replace('\'','')
	
app = Flask(__name__)

@app.route('/get_score', methods=['GET', 'POST'])
def get_score():
	if request.method == 'POST':
		r = request.get_json(force=True)
		# print(r, flush = True)
		upi = interpolate_coordinates(get_total_distance(r),get_lat_lng(r),k)
		print(upi, flush = True)
		# download pictures here (arjun)
		####
		#inference here
		####
		#score = something
		return 'OK', 200
	else:
		score = round(random.random(),1)
		message = {"score" : score}
		return jsonify(message)


@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)
	
@app.route('/test')
def test():
	return render_template('test.html')
	
def get_total_distance(routes_obj):
	return routes_obj['legs'][0]['distance']['value']
	
def get_lat_lng(routes_obj):
	lat_lng = []
	steps = routes_obj['legs'][0]['steps']
	for step in steps:
		for lalo in step['lat_lngs']:
			lat_lng += [(lalo['lat'],lalo['lng'])]
	return lat_lng
	
def interpolate_coordinates(distance, lat_lng, k, separation_mts = 300):
	unique_points = list(set(lat_lng))
	n = max([1,round((distance/separation_mts)/len(unique_points))])
	unique_points_interpolated = []
	for i in range(len(unique_points)-1):
		unique_points_interpolated += list(map(tuple,np.linspace(unique_points[i],unique_points[i+1],n)))
	unique_points_interpolated = sorted(list(set(unique_points_interpolated)), key = lambda x: x[0])
	if n > 1: #If we have any new points to snap. 
		results = get_snapped_points(unique_points_interpolated,k)
		return results
	else:
		return unique_points_interpolated
	
def create_path(points):
    path = 'path='
    for i in points:
        path += str(i[0]) + ',' + str(i[1]) + '|'
    return path[:-1] #remove last '|'
	
def get_coords(r,points):
	print(r.json())
	for i in r.json()['snappedPoints']:
		points += [(i['location']['latitude'],i['location']['longitude'])]
	return points
	
def get_snapped_points(unique_points_interpolated,key,BASE_URL_SNAP = 'https://roads.googleapis.com/v1/snapToRoads?',interpolate = '&interpolate=true'):
	points = []
	k = 0
	coords_list = []
	while k <= len(unique_points_interpolated)-1:
		coords_list += [unique_points_interpolated[k]]
		if (len(coords_list)%100==0) or (k==len(unique_points_interpolated)): #When we have 100 points or we reach the end of the list.
			path = create_path(coords_list)
			url = BASE_URL_SNAP + path + interpolate + key
			r = requests.get(url)
			points += get_coords(r,points)
			coords_list = []
		k += 1
	return(points)
