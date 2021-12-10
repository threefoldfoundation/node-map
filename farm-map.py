import requests, time
from requests_futures.sessions import FuturesSession

r = requests.get('https://explorer.grid.tf/api/v1/nodes')
pages = int(r.headers['Pages'])
nodes = r.json()

session = FuturesSession(max_workers=50)
futures = []
for i in range(pages - 1):    
    f = session.get('https://explorer.grid.tf/api/v1/nodes?page=' + str(i + 2))
    futures.append(f)

for f in futures:
    r = f.result()
    nodes += r.json()


nodes = [n for n in nodes if not time.time() - n['updated'] > 60 * 60 * 24]


print(str(len(nodes)) + " nodes")

f = open("nodemap.html", "w")

f.write(
'''
<!DOCTYPE html>
<html>
<head>
	
	<title>ThreeFold Nodes</title>

	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	
	<link rel="shortcut icon" type="image/x-icon" href="docs/images/favicon.ico" />

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>

	<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
	<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
	<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster-src.js"></script>
	
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
    f.write('<!-- {} -->\n'.format(n['location']['country']))
    f.write('markers.addLayer(L.marker([{}, {}]));\n'.format(n['location']['latitude'], n['location']['longitude']))

f.write(
'''
map.addLayer(markers);
</script>



</body>
</html>
'''
)