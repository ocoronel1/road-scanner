var map;

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
	this.provideRouteAlternatives = true;
	
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
	
	DirectionsTool.prototype.PolyOptionsBuilder = async function(route) {
		var polylineOptions = {}; 
		polylineOptions.path = route;
		polylineOptions.strokeColor = '#FF00FF'; //Fuchsia, Teal
		let get_score = await fetch('/get_score')
			.then(function(response){
					return response.text();
			}).then(function(text){
				console.log(JSON.parse(text).score)
				polylineOptions.strokeOpacity = JSON.parse(text).score;
			})
		return polylineOptions;
	};
		
	DrawPolyline = async function(path) {
		var route = path;
		dt = new DirectionsTool()
		dt.PolyOptionsBuilder(route).then(function(result){
			options = result;
			return options
		}).then(async function(options){
			line = new google.maps.Polyline(options)
			await line.setMap(map);
			var bounds = new google.maps.LatLngBounds();
			var points = line.getPath().getArray();
			for (var n = 0; n < points.length ; n++){
				bounds.extend(points[n]);
			}
			map.fitBounds(bounds);

			var infoWindow = new google.maps.InfoWindow();
			midpoint = line.getPath().getArray()[Math.floor(line.getPath().getArray().length/2)];
			latlngobj = new google.maps.LatLng(midpoint.lat(),midpoint.lng());
			infoWindow.setPosition(latlngobj);
			infoWindow.setContent('Score: ' + String(options.strokeOpacity));
			infoWindow.open(map);
		});
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
			res =  results;
			for (var i = 0; i < results.routes.length; i++) {
				await ComputeScores(results.routes[i]);
				await DrawPolyline(results.routes[i].overview_path);				
			};
			// dir_renderer.setDirections(results)
			// Open the InfoWindow on mouseover:
			
			
		}
	}
	
	// Send a request to the directions service.
	
	DirectionsTool.prototype.GetDirectionsFromState = function() {
		var request = state.buildDirectionsRequest();
		// console.log('Directions: ' + JSON.stringify(request));
		dir_service.route(request, this.handleDirectionsResponse);
	};
	
	DirectionsTool.prototype.updateStateFromSearchControl = function() {
		state.reset();
		state.origin = document.getElementById('start-input').value;
		state.destination = document.getElementById('end-input').value;
		this.GetDirectionsFromState();
	};
}

var get_route = function() {
	if (document.getElementById('start-input').value.length > 0) {		
        // Routing
        if(document.getElementById('end-input').value.length > 0) {
			tool = new DirectionsTool();
			tool.updateStateFromSearchControl();
    	};
    };
};

const node1 = document.getElementById('end-input');

node1.addEventListener('keyup', function (event) {
	if (event.key === "Enter") {
		get_route();
	};
});

