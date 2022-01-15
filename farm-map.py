import requests, time
from requests_futures.sessions import FuturesSession

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


# Use unified explorer, by default queries all Grid 2 nets
explorer = 'https://explorer.threefold.io/api/nodes?network=all'

nodes2 = []

r = requests.get(explorer)
try:
	pages = int(r.headers['Pages'])
except KeyError:
	pages = 1

nodes2 += r.json()

session = FuturesSession(max_workers=50)
futures = []
for i in range(pages - 1):    
	f = session.get(explorer + '?page=' + str(i + 2))
	futures.append(f)

for f in futures:
	r = f.result()
	nodes2 += r.json()

# Include all nodes online in the last hour
nodes2 = [n for n in nodes2 if not time.time() - n['updated'] > 60 * 60 * 1]

# Retrieve Grid 3 nodes from grid proxy

nodes3 = []
proxies = ['https://gridproxy.dev.grid.tf/', 'https://gridproxy.test.grid.tf/', 'https://gridproxy.grid.tf/']

subnets = ['.dev', '.test', '']
proxy_base = 'https://gridproxy{}.grid.tf/nodes'
gql_base = 'https://graphql{}.grid.tf/graphql'

query = """
query MyQuery {{
  nodes(where: {{nodeId_in: {}}}, limit: {}) {{
    location {{
      latitude
      longitude
    }}
	nodeId
  }}
}}
"""

for net in subnets:
	proxy = proxy_base.format(net)
	nodes = []

	r = requests.get(proxy)
	page = 2
	while r.json():
		nodes += r.json()
		r = requests.get(proxy + '?page=' + str(page))
		page += 1

	nodes = [n for n in nodes if n['status'] == 'up']
	node_ids = [n['nodeId'] for n in nodes]

	# Use GraphQL to retrieve location data, not provided by grid proxy
	transport = RequestsHTTPTransport(url=gql_base.format(net), verify=True, retries=3)

	client = Client(transport=transport, fetch_schema_from_transport=True)
	result = client.execute(gql(query.format(node_ids, len(node_ids))))

	for n in result['nodes']:
		for o in nodes:
			if n['nodeId'] == o['nodeId']:
				o['location'] = n['location']
				o['location']['country'] = o['country']

	nodes3 += nodes


print(str(len(nodes2 + nodes3)) + " nodes")

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

<h1>ThreeFold Node Map</h1>
'''
)

f.write(
'''
<strong>Grid 2:</strong> {} | <strong>Grid 3:</strong> {} | <strong>Total:</strong> {}
'''.format(len(nodes2), len(nodes3), len(nodes2 + nodes3)))

f.write(
'''
<br><br>
<div id="map" style="height: 600px;"></div>
<script>

	var map = L.map('map').setView([51.505, -0.09], 2);

	var tiles = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Sources: Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, &copy OpenStreetMap contributors, and the GIS User Community'
	}).addTo(map);

var markers2 = L.markerClusterGroup({
spiderfyOnMaxZoom: false,
showCoverageOnHover: true,
zoomToBoundsOnClick: true,
maxClusterRadius: 30
});

var markers3 = L.markerClusterGroup({
spiderfyOnMaxZoom: false,
showCoverageOnHover: true,
zoomToBoundsOnClick: true,
maxClusterRadius: 30
});

'''
)

for n in nodes2 + nodes3:
    f.write('<!-- {} -->\n'.format(n['location']['country']))
    f.write('markers2.addLayer(L.marker([{}, {}]));\n'.format(n['location']['latitude'], n['location']['longitude']))

for n in nodes3:
    f.write('<!-- {} -->\n'.format(n['location']['country']))
    f.write('markers3.addLayer(L.marker([{}, {}]));\n'.format(n['location']['latitude'], n['location']['longitude']))

f.write(
'''
var markers = {
    "Grid 2": markers2,
    "Grid 3": markers3
};

map.addLayer(markers2);
map.addLayer(markers3);

L.control.layers(null, markers, {collapsed: false}).addTo(map);
</script>



</body>
</html>
'''
)