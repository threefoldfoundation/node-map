import requests, time

nodes = []
r = requests.get('https://explorer.grid.tf/api/v1/nodes')
pages = int(r.headers['Pages'])

for i in range(pages):
    nodes += r.json()
    r = requests.get('https://explorer.grid.tf/api/v1/nodes?page=' + str(i + 2))

for i, n in enumerate(nodes):
    if time.time() - nodes[i]['updated'] > 900:
        nodes.pop(i)


print(len(nodes) + " nodes")

f = open("nodemap.html", "w")

f.write(
'''
<!DOCTYPE html>
<html>
<head>
	
	<title>Quick Start - Leaflet</title>

	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	
	<link rel="shortcut icon" type="image/x-icon" href="docs/images/favicon.ico" />

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>
	
</head>
<body>

<div id="map" style="width: 1200px; height: 800px;"></div>
<script>

	var map = L.map('map').setView([51.505, -0.09], 2);

	var tiles = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox/streets-v11',
		tileSize: 512,
		zoomOffset: -1
	}).addTo(map);

var markers = L.markerClusterGroup({
spiderfyOnMaxZoom: false,
showCoverageOnHover: true,
zoomToBoundsOnClick: true,
maxClusterRadius: 30
});

'''
)

for n in nodes:
    f.write('markers.addLayer(L.marker([{}, {}]).addTo(map));\n'.format(n['location']['latitude'], n['location']['longitude']))

f.write(
'''
map.addLayer(markers);
</script>



</body>
</html>
'''
)