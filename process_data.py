import sqlite3
import pandas as pd
import h3
from shapely.geometry import box, Polygon, mapping
import json

# Configuration
DB_PATH = 'kontur_population_20231101.gpkg'
OUTPUT_FILE = 'norway_population.json'

# Norway Bounding Box (Approximate)
# West: 4.0, South: 57.0, East: 32.0, North: 72.0
MIN_LON, MIN_LAT = 4.0, 57.0
MAX_LON, MAX_LAT = 32.0, 72.0

def get_norway_data():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    
    # The dataset uses H3 indices. We can filter by H3 index if we knew the resolution and prefixes,
    # but since we don't know the exact resolution without checking, we might need to iterate.
    # HOWEVER, the 'population' table has 'h3' column.
    
    # Let's first check one row to see the H3 resolution
    cursor = conn.cursor()
    cursor.execute("SELECT h3 FROM population LIMIT 1")
    sample_h3 = cursor.fetchone()[0]
    resolution = h3.get_resolution(sample_h3)
    print(f"Detected H3 resolution: {resolution}")

    # To be efficient, we should only query H3 indices that *could* be in Norway.
    # We can generate all H3 cells at this resolution that cover Norway's bounding box.
    # This might be a large list, but it's better than scanning the whole world.
    
    print("Loading Norway GeoJSON...")
    with open('norway.geojson', 'r') as f:
        geojson_data = json.load(f)
    
    # Extract the MultiPolygon coordinates
    # Structure: features[0].geometry.coordinates -> list of polygons
    # Each polygon is a list of rings (first ring is outer)
    # Each ring is a list of [lng, lat]
    
    print("Generating H3 cells for Norway polygons...")
    all_cells = set()
    try:
        for feature in geojson_data['features']:
            geometry = feature['geometry']
            geom_type = geometry['type']
            coordinates = geometry['coordinates']
            
            polygons = []
            if geom_type == 'Polygon':
                polygons.append(coordinates)
            elif geom_type == 'MultiPolygon':
                polygons.extend(coordinates)
            else:
                print(f"Skipping geometry type: {geom_type}")
                continue
                
            for polygon_coords in polygons:
                # polygon_coords is a list of rings. First ring is outer.
                if not polygon_coords:
                    continue
                    
                outer_ring = polygon_coords[0]
                
                # Convert to (lat, lng)
                lat_lng_poly = [(lat, lng) for lng, lat in outer_ring]
                
                # Create LatLngPoly
                poly = h3.LatLngPoly(lat_lng_poly)
                
                # Get cells
                cells = h3.polygon_to_cells(poly, resolution)
                all_cells.update(cells)

            
    except Exception as e:
        print(f"Error generating cells: {e}")
        import traceback
        traceback.print_exc()
        return

    cells = list(all_cells)
    print(f"Generated {len(cells)} potential H3 cells for Norway.")
        
    # Now we need to query these. 
    # If the list is huge (e.g. millions), 'IN (...)' clause will fail.
    # We can dump these into a temporary table in the sqlite db (or an attached in-memory db) 
    # and do a JOIN.
    
    print("Creating temporary table for filtering...")
    # Attach in-memory database
    cursor.execute("ATTACH DATABASE ':memory:' AS filter_db")
    cursor.execute("CREATE TABLE filter_db.norway_cells (h3_index TEXT)")
    
    # Insert cells in batches
    cursor.executemany("INSERT INTO filter_db.norway_cells (h3_index) VALUES (?)", [(c,) for c in cells])
    
    print("Querying matching population data...")
    sql = """
        SELECT p.h3, p.population 
        FROM population p
        INNER JOIN filter_db.norway_cells n ON p.h3 = n.h3_index
    """
    
    df = pd.read_sql_query(sql, conn)
    print(f"Found {len(df)} populated cells in Norway.")
    
    # Export to JSON
    # Format: [{"h3": "...", "pop": 123}, ...] or just a dictionary/list
    # To save space: [["h3", pop], ...]
    
    output_data = df.values.tolist()
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f)
        
    print(f"Saved to {OUTPUT_FILE}")
    return

if __name__ == "__main__":
    get_norway_data()
