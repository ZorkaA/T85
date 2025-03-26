import requests
import csv
import time
from tqdm import tqdm

bbox = "40.513643113618144,-74.24357049486149,40.96850354217733,-73.64963881441679"

#remap
node_types = {
    "amenity=school": "school",
    "amenity=hospital": "hospital",
    "amenity=pharmacy": "pharmacy",
    "shop=supermarket": "supermarket",
    "amenity=restaurant": "restaurant",
    "amenity=cafe": "cafe",
    "leisure=park": "park",
    "public_transport=station": "public transport",
    "station=subway": "subway",
    "station=train": "train",
    "highway=bus_stop": "bus",
    "amenity=gym": "gym",
    "amenity=library": "library",
    "amenity=childcare": "childcare",
    "amenity=police": "police",
    "amenity=fire_station": "fire",
    "amenity=post_office": "post office",
    "amenity=bank": "bank",
    "amenity=atm": "atm",
    "amenity=theatre": "theater",
    "tourism=museum": "museum",
    "historic=monument": "monument",
    "natural=beach": "beach",
    "aeroway=aerodrome": "airport",
    "tourism=camp_site": "campsite",
    "tourism=hotel": "hotel",
    "amenity=place_of_worship": "place of worship",
    "shop=grocery": "grocery",
    "shop=clothes": "clothes",
    "shop=furniture": "furniture",
    "shop=bookshop": "bookshop",
    "shop=bakery": "bakery",
    "shop=butcher": "butcher",
    "shop=chemist": "chemist",
    "shop=convenience": "convenience",
    "shop=deli": "deli"
}

#overpass
query_parts = []
for k, v in node_types.items():
    key, value = k.split("=")  # Ensures the format is correct
    query_parts.append(f'node["{key}"="{value}"]({bbox});')

query = f"""
[out:json][timeout:300];
(
    {' '.join(query_parts)}
);
out body;
"""

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

print("Querying Overpass API...")
response = requests.post(OVERPASS_URL, data=query)
if response.status_code != 200:
    print("Error fetching data:", response.text)
    exit(1)

data = response.json()

nodes = []
elements = data.get("elements", [])

print(f"Processing {len(elements)} nodes...")
for element in tqdm(elements, desc="Processing Nodes", unit="node"):
    if element["type"] == "node":
        # Extract node type and map to common name
        node_tags = element.get("tags", {})
        nodetype = next(
            (node_types.get(f"{k}={v}", "unknown") for k, v in node_tags.items() if f"{k}={v}" in node_types),
            "unknown")

        nodes.append([
            element["id"], nodetype, element["lat"], element["lon"]
        ])

csv_filename = "osm_nodes.csv"
with open(csv_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["nodeID", "nodetype", "lat", "lon"])
    writer.writerows(nodes)

print(f"CSV saved: {csv_filename} (Total nodes: {len(nodes)})")
