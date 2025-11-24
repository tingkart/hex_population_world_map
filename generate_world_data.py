import sqlite3
import pandas as pd
import h3
import json
import os
from shapely.geometry import shape
from multiprocessing import Pool, cpu_count, current_process

# Configuration
DB_PATH = 'kontur_population_20231101.gpkg'
GEOJSON_PATH = 'world_countries.geojson'
OUTPUT_DIR = 'public/data'
COUNTRIES_INDEX_FILE = 'public/countries.json'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_h3_resolution(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT h3 FROM population LIMIT 1")
    sample_h3 = cursor.fetchone()[0]
    resolution = h3.get_resolution(sample_h3)
    return resolution

def process_country(args):
    feature, resolution = args
    
    props = feature['properties']
    name = props.get('name', 'Unknown')
    iso_a3 = props.get('ISO3166-1-Alpha-3', 'UNK')
    
    # Handle missing ISO codes
    if iso_a3 == '-99' or iso_a3 is None:
        # Fallback to name-based ID or skip? 
        # Let's use a hash or just skip if truly unknown, but here we want to be safe.
        # We can't rely on index 'i' easily in parallel without passing it.
        # Let's just use a sanitized name.
        iso_a3 = name.replace(" ", "_").upper()

    output_file = os.path.join(OUTPUT_DIR, f"{iso_a3}.csv")
    if os.path.exists(output_file):
        return f"Skipped {name} ({iso_a3}) - exists"

    # Connect to DB in each process
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE ':memory:' AS filter_db")
        cursor.execute("CREATE TABLE filter_db.country_cells (h3_index TEXT)")
        
        geometry = feature['geometry']
        all_cells = set()
        
        polygons = []
        if geometry['type'] == 'Polygon':
            polygons.append(geometry['coordinates'])
        elif geometry['type'] == 'MultiPolygon':
            polygons.extend(geometry['coordinates'])
        
        for polygon_coords in polygons:
            if not polygon_coords: continue
            outer_ring = polygon_coords[0]
            lat_lng_poly = [(lat, lng) for lng, lat in outer_ring]
            poly = h3.LatLngPoly(lat_lng_poly)
            cells = h3.polygon_to_cells(poly, resolution)
            all_cells.update(cells)
            
        if not all_cells:
            conn.close()
            return f"No cells for {name}"
            
        cells_list = list(all_cells)
        cursor.executemany("INSERT INTO filter_db.country_cells (h3_index) VALUES (?)", [(c,) for c in cells_list])
        
        sql = """
            SELECT p.h3, p.population 
            FROM population p
            INNER JOIN filter_db.country_cells n ON p.h3 = n.h3_index
        """
        
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        if df.empty:
            msg = f"No population for {name}"
            # Create empty file to mark as processed
            with open(output_file, 'w') as f:
                pass
        else:
            # Optimization: Dynamic Resolution Scaling REMOVED
            # User requested native resolution (400x400m / Res 8) always.
            # We skip any aggregation.
            
            # df already has 'h3' and 'population' from the query at native resolution
            current_res = resolution
            msg = f"Generated {len(df)} cells for {name} (Native Res {current_res})"
            
            # Save as CSV (no header, index=False) to save space
            df.to_csv(output_file, index=False, header=False)
            
        return msg

    except Exception as e:
        return f"Error {name}: {e}"

def generate_country_data():
    print("Loading World GeoJSON...")
    with open(GEOJSON_PATH, 'r') as f:
        geojson_data = json.load(f)
    
    # Initial connection to get resolution
    conn = sqlite3.connect(DB_PATH)
    resolution = get_h3_resolution(conn)
    conn.close()
    print(f"H3 Resolution: {resolution}")

    features = geojson_data['features']
    total = len(features)
    
    # First pass: Collect metadata and save index
    print("Collecting metadata for all countries...")
    countries_metadata = []
    for i, feature in enumerate(features):
        props = feature['properties']
        name = props.get('name', 'Unknown')
        iso_a3 = props.get('ISO3166-1-Alpha-3', 'UNK')
        
        if iso_a3 == '-99' or iso_a3 is None:
            iso_a3 = name.replace(" ", "_").upper()
            
        geometry = feature['geometry']
        
        try:
            shapely_geom = shape(geometry)
            
            # For MultiPolygons, use the largest polygon for the bounding box
            # This avoids zooming out for distant small islands (e.g. Norway's Bouvet Island)
            if shapely_geom.geom_type == 'MultiPolygon':
                largest_poly = max(shapely_geom.geoms, key=lambda p: p.area)
                bbox = largest_poly.bounds
                centroid = largest_poly.centroid
            else:
                bbox = shapely_geom.bounds
                centroid = shapely_geom.centroid
            
            countries_metadata.append({
                "name": name,
                "code": iso_a3,
                "centroid": [centroid.x, centroid.y],
                "bbox": bbox
            })
        except Exception as e:
            print(f"Error processing metadata for {name}: {e}")

    # Save metadata immediately
    with open(COUNTRIES_INDEX_FILE, 'w') as f:
        json.dump(countries_metadata, f)
    print(f"Saved metadata for {len(countries_metadata)} countries to {COUNTRIES_INDEX_FILE}")

    print(f"Processing {total} countries with {cpu_count()} workers...")

    # Prepare args
    tasks = [(f, resolution) for f in features]
    
    with Pool(processes=cpu_count()) as pool:
        for i, result in enumerate(pool.imap_unordered(process_country, tasks)):
            print(f"[{i+1}/{total}] {result}")

if __name__ == "__main__":
    generate_country_data()
