import gpxpy
import json
import os

def generate_gpx_json():
    routes_dir = 'routes'
    output_file = 'routes.json'
    results = []

    if not os.path.exists(routes_dir):
        print(f"Error: Folder '{routes_dir}' not found.")
        return

    for filename in os.listdir(routes_dir):
        if filename.lower().endswith('.gpx'):
            filepath = os.path.join(routes_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    gpx = gpxpy.parse(f)
                    
                    if gpx.tracks and gpx.tracks[0].segments:
                        track = gpx.tracks[0]
                        first_point = track.segments[0].points[0]
                        
                        # Distance calculation (3D accounts for elevation changes)
                        distance_meters = track.length_3d()
                        
                        # Elevation Gain (Total Uphill)
                        uphill, downhill = track.get_uphill_downhill()
                        
                        # Link extraction
                        author_website = gpx.author_link if gpx.author_link else ""
                        route_link = track.link if track.link else ""

                        results.append({
                            "name": track.name or gpx.name or filename.replace('.gpx', ''),
                            "author": gpx.author_name or "",
                            "author_website": author_website,
                            "description": gpx.description or "",
                            "link": gpx.link if gpx.link else "",
                            "route_link": route_link,
                            "date": gpx.time.strftime("%Y-%m-%d") if gpx.time else None,
                            "type": track.type or "cycling",
                            "coords": [first_point.latitude, first_point.longitude],
                            "distance_km": round(distance_meters / 1000, 2),
                            "elevation_gain_m": round(uphill, 0),
                            "gpx": filename
                        })
                        print(f"Processed: {filename} ({round(distance_meters/1000, 1)}km)")
            except Exception as e:
                print(f"Could not process {filename}: {e}")

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nSuccess! {len(results)} routes saved to {output_file}")

if __name__ == '__main__':
    generate_gpx_json()
