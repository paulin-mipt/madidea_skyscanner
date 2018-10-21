// Credit goes to @ryancatalani
// URL: https://gist.github.com/ryancatalani/6091e50bf756088bf9bf5de2017b32e6#file-leaflet-bezier-curve-js

function addBezierTrip(a_lat, a_lon, b_lat, b_lon, cost, url, color='rgba(255,0,0,0.9)', weight=2, animate=false) {
    var latlngs = [];

    var latlng1 = [a_lat, a_lon],
        latlng2 = [b_lat, b_lon];

    var offsetX = latlng2[1] - latlng1[1],
        offsetY = latlng2[0] - latlng1[0];

    var r = Math.sqrt( Math.pow(offsetX, 2) + Math.pow(offsetY, 2) ),
        theta = Math.atan2(offsetY, offsetX);

    var thetaOffset = (3.14/10);

    var r2 = (r/2)/(Math.cos(thetaOffset)),
        theta2 = theta + thetaOffset;

    var midpointX = (r2 * Math.cos(theta2)) + latlng1[1],
        midpointY = (r2 * Math.sin(theta2)) + latlng1[0];

    var midpointLatLng = [midpointY, midpointX];

    latlngs.push(latlng1, midpointLatLng, latlng2);

    var pathOptions = {
        color: color,
        weight: weight
    }

    if (animate && typeof document.getElementById('map-container').animate === "function") { 
        var durationBase = 2000;
        var duration = Math.sqrt(Math.log(r + 1)) * durationBase;
        // Scales the animation duration so that it's related to the line length
        // (but such that the longest and shortest lines' durations are not too different).
           // You may want to use a different scaling factor.
          pathOptions.animate = {
            duration: duration,
            iterations: 1,
            easing: 'ease-in-out',
            direction: 'alternate'
        }
    }

    popup = '<a href="' + url.toString() + '">Book on Skyscanner!</a><br />' + cost.toString() + '\u20AC';

    var curvedPath = L.curve(
        [
            'M', latlng1,
            'Q', midpointLatLng,
                 latlng2
    ], pathOptions).addTo(map).bindPopup(popup.toString());
}
