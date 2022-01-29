# ThreeFold Grid Node Map

This is a small Python 3 program which queries data about nodes on the ThreeFold Grid and generates an html map based on geolocation data.

## Dependencies

Two Python libraries are required: `requests-futures` for concurrent http requests and `gql[requests]` for GraphQL queries. Both can be installed with `pip`.

## Run

Simply run `python node-map.py` and the generated `nodemap.html` will appear in the same folder.

## Mapping and Tiles

Mapping is done with the Leaflet Javascript library and the Leaflet.markercluster plugin. Here we use map tiles from Esri which are freely available.
