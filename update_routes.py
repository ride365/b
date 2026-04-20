import gpxpy
import json
import os
import re
from collections import defaultdict

def generate_gpx_json():
    routes_dir = 'routes'
    output_file = 'routes.json'
    clusters = defaultdict(lambda: defaultdict(list))
    grid_step = 0.00225 

    for filename in os.listdir(routes_dir):
        if filename.lower().endswith('.gpx'):
            filepath = os.path.join(routes_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    gpx = gpxpy.parse(f)
                    if not (gpx.tracks and gpx.tracks[0].segments): continue
                    
                    track = gpx.tracks[0]
                    start = track.segments[0].points[0]
                    display_name = track.name or filename.replace('.gpx', '')

                    # --- CLEANING THE NAMES ---
                    # This splits into: [Base Name, Variant Name]
                    # E.g. "Stone Circle - 100km" -> ["Stone Circle", "100km"]
                    parts = re.split(r' - | \(', display_name, 1)
                    base_name = parts[0].strip()
                    
                    # If there's a second part, clean up the trailing bracket if it exists
                    if len(parts) > 1:
                        variant_label = parts[1].replace(')', '').strip()
                    else:
                        variant_label = display_name

                    # 250m Proximity Snapping
                    snap_lat = round(start.latitude / grid_step) * grid_step
                    snap_lon = round(start.longitude / grid_step) * grid_step
                    loc_key = f"{snap_lat:.5f},{snap_lon:.5f}"

                    clusters[loc_key][base_name].append({
                        "variant_label": variant_label, # Now just "100km" or "Epic"
                        "distance_km": round(track.length_3d() / 1000, 2),
                        "elevation_gain_m": round(track.get_uphill_downhill()[0], 0),
                        "author": gpx.author_name or "",
                        "author_website": gpx.author_link if gpx.author_link else "",
                        "description": gpx.description or "",
                        "strava_link": track.link if track.link else "",
                        "original_route": gpx.link if gpx.link else "",
                        "activity_type": track.type or "cycling",
                        "date": gpx.time.strftime("%Y-%m-%d") if gpx.time else None,
                        "surface": next((ext.text for ext in track.extensions if 'surface' in ext.tag), "unknown"),
                        "gpx": filename
                    })
                    print(f"Processed: {filename}")
            except Exception as e:
                print(f"Could not process {filename}: {e}")

    # Build final JSON
    final_output = []
    for loc_key, events_dict in clusters.items():
        coords = [float(x) for x in loc_key.split(',')]
        event_list = []
        for name, variants in events_dict.items():
            variants.sort(key=lambda x: x['distance_km'])
            
            min_dist = variants[0]['distance_km']
            max_dist = variants[-1]['distance_km']
            # Only show a range if there is more than one variant
            dist_range = f"{min_dist}km - {max_dist}km" if len(variants) > 1 else f"{min_dist}km"

            event_list.append({
                "event_name": name,
                "distance_range": dist_range, # Store for easy display
                "variants": variants
            })
        final_output.append({"coords": coords, "events": event_list})

    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=4)

if __name__ == '__main__':
    generate_gpx_json()
