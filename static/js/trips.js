var map = L.map('map-container').setView([20, 0], 2);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
  maxZoom: 18,
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  id: 'mapbox.streets'
}).addTo(map);

for (var i = 0; i < flights.length; i++) {
    flight = flights[i];
    addBezierTrip(
        flight['a_lat'], flight['a_lon'],
        flight['b_lat'], flight['b_lon'],
        flight['cost'], 
        color='rgba(0,0,0,0.2)',
        weight=2
      )

    addBezierTrip(
        flight['a_lat'], flight['a_lon'],
        flight['b_lat'], flight['b_lon'],
        flight['cost'], 
        color='rgba(255,0,0,0.9)',
        weight=3, animate=true
      )
    // var latlngs = [
    //     [flight['a_lat'], flight['a_lon']],
    //     [flight['b_lat'], flight['b_lon']]
    // ];
    // L.polygon(latlngs, {color: 'red'}).addTo(map)
    //     .bindPopup(flight['cost'].toString());
}