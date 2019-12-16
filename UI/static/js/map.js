var map;
const segments = 10;
const proc_folders = ['original/','dusk/','night/','winter/'];
const sw_positions = [0.8,0.6,0.4,0.2];
const v_size = 0.175;
const h_size = 0.125;
const west_pos = 0.8;
var origins_and_destinations = {
	'Kings':{origin:'Kings Beach, California, USA',destination:'Camp Richardson, California 96150, USA'},
	'Mendocino':{origin:'Mendocino, California, USA',destination:'Bodega Bay, California 94923, USA'},
	'Death':{origin:'Death Valley Junction, California 92328, USA',destination:'CA-190, California, USA'},
	'origin=1415':{origin:'1415 Summit Rd, Berkeley, CA 94708, USA',destination:'Grizzly Peak Blvd Overlook, 4348 Grizzly Peak Blvd, Berkeley, CA 94705, United States'},
	'Sand':{origin:'Sand City, California, USA',destination:'Gorda, California 93920, USA'}
};
var color = d3.scaleLinear()
	.domain([0,0.5,1])
	.range(["red","yellow","green"]);

function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
          center: new google.maps.LatLng(37.8715, -122.2730),
          zoom: 8
	});
};

// Create a state object for directions.
var DirectionsState = function() {
	this.origin = '';
	this.destination = '';
	this.travelMode = 'DRIVING';
	this.provideRouteAlternatives = false; //true for getting many routes.
	this.folder = '';
	
	DirectionsState.prototype.reset = function() {
		this.origin = '';
		this.destination = '';
	};
	
	// Build a directions request from the global state.
	// @returns an object suitable to be fed to the 
	// DirectionsService.route() method as per
	// https://developers.google.com/maps/documentation/javascript/directions
	
	DirectionsState.prototype.buildDirectionsRequest = function() {
		// Build the directions request from state.
		var request = {};
		request.origin = this.origin;
		request.destination = this.destination;
		request.travelMode = this.travelMode;
		request.provideRouteAlternatives = this.provideRouteAlternatives;
		return request;
	};
};

// Event handler using the DirectionsState object.
var DirectionsTool = function() {
	var DirectionsResults = [];
	var state = new DirectionsState();
	var dir_service = new google.maps.DirectionsService();
	
	DirectionsTool.prototype.PolyOptionsBuilder = async function(route,segment,folder) {
		var polylineOptions = {}; 
		polylineOptions.path = route;
		identifier = {};
		identifier.segment = segment;
		identifier.folder = folder;
		let get_score = await fetch('/get_score', {
			method: 'POST_ID',
			body: JSON.stringify(identifier)
		}).then(function(response){
					return response.text();
			}).then(function(text){
				payload = JSON.parse(text);
				score = payload.score;
				picture = payload.picture;
				// polylineOptions.strokeOpacity = JSON.parse(text).score;
				// polylineOptions.strokeColor = d3.interpolateCool(score); 
				polylineOptions.strokeColor = color(score);
			})
		return polylineOptions;
	};
	
	MapRelativeToCoordinates = function(n,setting,sw,ne) {
		if (setting === 'vertical') {
			vertical_range = ne.lat() - sw.lat();
			lat_point = sw.lat() + n*vertical_range;
			return lat_point;
		}else{
			horizontal_range = ne.lng() - sw.lng();
			lng_point = sw.lng() + n*horizontal_range;
			return lng_point
		};
	};
	
	ImageBoundsBuilder = function(sw_position) {
		imageBounds = {};
		var bounds = map.getBounds();
		var southWest = bounds.getSouthWest();
		var northEast = bounds.getNorthEast();
		imageBounds.north = MapRelativeToCoordinates(sw_position + v_size,'vertical',southWest,northEast);
		imageBounds.south = MapRelativeToCoordinates(sw_position,'vertical',southWest,northEast);
		imageBounds.west = MapRelativeToCoordinates(west_pos,'horizontal',southWest,northEast);
		imageBounds.east = MapRelativeToCoordinates(west_pos + h_size,'horizontal',southWest,northEast);
		return imageBounds;
	};
	
	GetOverlayImages = function(pic,folder,subfolder,sw_position) {
		url = './static/images/' + folder + '/' + subfolder + pic;
		console.log(url);
		imageBounds = ImageBoundsBuilder(sw_position);
		Overlay = new google.maps.GroundOverlay(url,imageBounds);
		Overlay.setMap(map);
	};
		
	DrawPolyline = async function(path,lines,id) {
		// break into segments
		chunk = Math.ceil(path.length/segments)
		lines[id] = {};
		for (i=0; i<path.length; i+=chunk) {
			path_piece = path.slice(i,Math.min(i+chunk,path.length));
			f = state.folder
			dt = new DirectionsTool()
			j = i/chunk
			dt.PolyOptionsBuilder(path_piece,j,f).then(function(result){
				options = result;
				return options;
			}).then(async function(options){
				lines[id][j] = {};
				lines[id][j] = await new google.maps.Polyline(options);
				return lines[id][j];
			}).then(async function(){
				lines[id][j].setMap(map);
				window["lines_" + id + "_" + j] = lines[id][j];
				window["lines_" + id + "_" + j]['score'] = score;
				window["lines_" + id + "_" + j]['segment'] = j;
				window["lines_" + id + "_" + j]['pic'] = picture;
				eval(google.maps.event.addListener(window["lines_" + id + "_" + j], 'click',function() {
					midpoint = this.getPath().getArray()[Math.floor(this.getPath().getArray().length/2)]; // this works and window[lines...] doesn't due to Necromancy, probably. 
					var infoWindow = new google.maps.InfoWindow();
					latlngobj = new google.maps.LatLng(midpoint.lat(),midpoint.lng());
					infoWindow.setPosition(latlngobj);
					infoWindow.setContent('Score: ' + this.score);
					infoWindow.open(map);
					pic = this.pic;
					for (i=0;i<proc_folders.length;i++) {
						GetOverlayImages(pic,f,proc_folders[i],sw_positions[i]);
					};
				})); // eval needed, otherwise the listener won't be added until we click the object. 
			}).then(function(){
				j += 1;
			});
				
				// var infoWindow = new google.maps.InfoWindow();
				// midpoint = line.getPath().getArray()[Math.floor(line.getPath().getArray().length/2)];
				// latlngobj = new google.maps.LatLng(midpoint.lat(),midpoint.lng());
				// infoWindow.setPosition(latlngobj);
				// infoWindow.setContent('Score: ' + String(score));
				// infoWindow.open(map);
			//});
		};
	};
	
	ComputeScores = async function(route_obj) {
		// console.log(JSON.stringify(route_obj));
		let compute_score = await fetch('/get_score', {
			method: 'POST',
			body: JSON.stringify(route_obj)
		}).then(function(response){
			return response.text();
		}).then(function(text){
			console.log('POST response: ');
			console.log(text);
		});
	};
	
	DirectionsTool.prototype.handleDirectionsResponse = async function(results, status) {
		if (status === "OK"){
			// here we could use a parallel version if we have one.
			lines = {};
			for (var i = 0; i < results.routes.length; i++) {
				await DrawPolyline(results.routes[i].overview_path,lines,i);				
			};
			var bounds = new google.maps.LatLngBounds();
			var points = await results.routes[0].overview_path;
			for (var i = 0; i < points.length; i++){
				bounds.extend(points[i]);
			}
			map.fitBounds(bounds);
		}
	}
	
	// Send a request to the directions service.
	
	DirectionsTool.prototype.GetDirectionsFromState = function() {
		var request = state.buildDirectionsRequest();
		// console.log('Directions: ' + JSON.stringify(request));
		dir_service.route(request, this.handleDirectionsResponse);
	};
	
	// DirectionsTool.prototype.updateStateFromSearchControl = function() {
		// state.reset();
		// state.origin = document.getElementById('start-input').value;
		// state.destination = document.getElementById('end-input').value;
		// this.GetDirectionsFromState();
	// };
	
	DirectionsTool.prototype.updateStateFromFolderName = function(folder_name) {
		state.reset();
		state.folder = folder_name;
		state.origin = origins_and_destinations[folder_name].origin;
		state.destination = origins_and_destinations[folder_name].destination;
		this.GetDirectionsFromState();
	}
}

var get_route = function(folder_name) {
	tool = new DirectionsTool
	tool.updateStateFromFolderName(folder_name)
	// if (document.getElementById('start-input').value.length > 0) {		
        // //Routing
        // if(document.getElementById('end-input').value.length > 0) {
			// tool = new DirectionsTool();
			// tool.updateStateFromSearchControl();
    	// };
    // };
};

// const node1 = document.getElementById('end-input');

// node1.addEventListener('keyup', function (event) {
	// if (event.keyCode === 13) {
		// get_route();
	// };
// });

