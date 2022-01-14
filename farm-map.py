import requests, time
from requests_futures.sessions import FuturesSession


# Use unified explorer, by default queries all Grid 2 nets
explorer = 'https://explorer.threefold.io/api/nodes?network=all'

nodes = []

r = requests.get(explorer)
try:
	pages = int(r.headers['Pages'])
except KeyError:
	pages = 1

nodes += r.json()

session = FuturesSession(max_workers=50)
futures = []
for i in range(pages - 1):    
	f = session.get(explorer + '?page=' + str(i + 2))
	futures.append(f)

for f in futures:
	r = f.result()
	nodes += r.json()

# Include all nodes online in the last hour
nodes = [n for n in nodes if not time.time() - n['updated'] > 60 * 60 * 2]


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

<h1>ThreeFold Grid 2 Nodes</h1>
'''
)

f.write('Showing {} nodes that were online in the last hour, across mainnet, testnet, and devnet.'.format(len(nodes)))

f.write(
'''
<br><br>
<div id="map" style="height: 600px;"></div>
<script>

	var map = L.map('map').setView([51.505, -0.09], 2);

	var tiles = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Sources: Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, &copy OpenStreetMap contributors, and the GIS User Community'
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