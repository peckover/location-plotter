import os
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Georgia'
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import re
import numpy as np

CSV_FOLDER = 'siteLocationCsvFile'
CSV_FILENAME = 'locations.csv'
OUTPUT_IMAGE = 'uk_artwork_map.png'
DPI = 300
MAP_EXTENT = [-8, 3, 49.5, 54]  # Cropped UK extent

def dms_to_dd(dms_str, index):
    dms_regex = r"(\d+)[°º]\s*(\d+)'?\s*([\d\.]+)\"?\s*([NSEW])"
    match = re.match(dms_regex, dms_str.strip())
    if not match:
        raise ValueError(f"Index:{index}, Invalid DMS format: {dms_str}")
    degrees, minutes, seconds, direction = match.groups()
    dd = float(degrees) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        dd = -dd
    return dd

def get_locations_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    locations = []
    for idx, row in df.iterrows():
        index = row['INDEX']
        lat_str = str(row['LATITUDE'])
        lon_str = str(row['LONGITUDE'])
        try:
            lat = dms_to_dd(lat_str, index)
            lon = dms_to_dd(lon_str, index)
        except Exception as e:
            print(f"Error parsing DMS for row {index} ({lat_str , lon_str}): {e}")
            continue
        locations.append({'index': index, 'lat': lat, 'lon': lon})
    print(f"index: {index} lat: {lat}, lon: {lon}")
    return locations

def filterNonUKLocations(locations):
    # Filter out locations outside the UK extent
    
    minExtentLon = MAP_EXTENT[0]
    maxExtentLon = MAP_EXTENT[1]
    minExtentLat = MAP_EXTENT[2]
    maxExtentLat = MAP_EXTENT[3]
    
    return [
        loc for loc in locations
        if (minExtentLon <= loc['lon'] <= maxExtentLon) and
           (minExtentLat <= loc['lat'] <= maxExtentLat)
    ]


locationsWithDistictLabels=['108', '46', '109', '53', '16', '48', '54', '45', '113', '71', '128', '130', '34', '112', '129', '37', '33', '38', '35', '1', '107', '147', '19', '150', '89', '67', '75', '39', '32', '26']

def assign_labels_custom(locations, extent):
    
    rightLonThreshold = -1.9
    leftLonThreshold = -3.4
    latThreshold = 51.3
    
    """
    Custom grouping and ordering:
    - Right: lon >= {rightLonThreshold} (ordered by increasing lat)
    - Left: lon <= {leftLonThreshold} (ordered by increasing lat)
    - Top: {leftLonThreshold} < lon < {rightLonThreshold} and lat >= {latThreshold} (ordered by increasing lon)
    - Bottom: {leftLonThreshold} < lon < {rightLonThreshold} and lat < {latThreshold} (ordered by increasing lon)
    """
    groups = {'right': [], 'left': [], 'top': [], 'bottom': [], 'distinct': []}
    
    # for loc in locations:
    #     lat = loc['lat']
    #     lon = loc['lon']
    #     if  lon >= rightLonThreshold:
    #         groups['right'].append(loc)
    #     elif lon <= leftLonThreshold:
    #         groups['left'].append(loc)
    #     elif leftLonThreshold < lon < rightLonThreshold and lat >= latThreshold:
    #         groups['top'].append(loc)
    #     elif leftLonThreshold < lon < rightLonThreshold and lat < latThreshold:
    #         groups['bottom'].append(loc)
    #     else:
    #         print('OOPS')
    #         groups['right'].append(loc)  # fallback, shouldn't happen
    
    distinct_ids = {str(i) for i in locationsWithDistictLabels}
    distinctLocations = [loc for loc in locations if str(loc['index']) in distinct_ids]
    locationsWithoutDistinctLabels = [loc for loc in locations if str(loc['index']) not in distinct_ids]
    print(f"locationsWithoutDistinctLabels: {len(locationsWithoutDistinctLabels)} locations: {len(locations)}")
    
    
    veryTopMost = sorted(locationsWithoutDistinctLabels, key=lambda l: l['lat'], reverse=True)[:0]
    locationsWithoutExtremes = [loc for loc in locationsWithoutDistinctLabels if loc not in veryTopMost]
    print(f"veryTopMost: {len(veryTopMost)} locationsWithoutDistinctLabels: {len(locationsWithoutDistinctLabels)}")
        
    rightMost = sorted(locationsWithoutExtremes, key=lambda l: l['lon'], reverse=True)[:0]
    locationsWithoutExtremes = [loc for loc in locationsWithoutExtremes if loc not in rightMost]
    print(f"rightMost: {len(rightMost)} locationsWithoutExtremes: {len(locationsWithoutExtremes)}")
    
    leftMost = sorted(locationsWithoutExtremes, key=lambda l: l['lon'])[:0]
    locationsWithoutExtremes = [loc for loc in locationsWithoutExtremes if loc not in leftMost]
    print(f"leftMost: {len(leftMost)} locationsWithoutExtremes: {len(locationsWithoutExtremes)}")
    
    topMost = sorted(locationsWithoutExtremes, key=lambda l: l['lat'], reverse=True)[:25]
    locationsWithoutExtremes = [loc for loc in locationsWithoutExtremes if loc not in topMost]
    print(f"topMost: {len(topMost)} locationsWithoutExtremes: {len(locationsWithoutExtremes)}")
    
    bottomMost = sorted(locationsWithoutExtremes, key=lambda l: l['lat'])[:28]
    locationsWithoutExtremes = [loc for loc in locationsWithoutExtremes if loc not in bottomMost]
    print(f"bottomMost: {len(bottomMost)} locationsWithoutExtremes: {len(locationsWithoutExtremes)}")
    
    
    locationsWithoutExtremes = [loc for loc in locationsWithoutExtremes if loc not in topMost and loc not in bottomMost and loc not in rightMost and loc not in leftMost]
    print(f"locationsWithoutExtremes: {len(locationsWithoutExtremes)}")
    
    medianLat = np.median([loc['lat'] for loc in locationsWithoutExtremes])
    medianLon = np.median([loc['lon'] for loc in locationsWithoutExtremes])
        
    for loc in locationsWithoutExtremes:
        lat = loc['lat']
        lon = loc['lon']
        if  lon >= (medianLon):
            groups['right'].append(loc)
        elif lon < (medianLon):
            groups['left'].append(loc)
        elif lat >= medianLat:
            groups['top'].append(loc)
        elif lat < medianLat:
            groups['bottom'].append(loc)
        else:
            print('OOPS')
            groups['right'].append(loc)  # fallback, shouldn't happen
    
    groups['right'].extend(rightMost)
    groups['left'].extend(leftMost)
    groups['top'].extend(topMost)
    groups['top'].extend(veryTopMost)
    groups['bottom'].extend(bottomMost)
    groups['distinct'].extend(distinctLocations)
    groups['isolated'] = []  # New group for isolated clusters
            
    print(f"right: {len(groups['right'])}")
    print(f"left: {len(groups['left'])}")
    print(f"top: {len(groups['top'])}")
    print(f"bottom: {len(groups['bottom'])}")
    print(f"distinct: {len(groups['distinct'])}")

    cluster_id = 1
    def sort_by_coordinate_then_index(locations, coord_key, tolerance=0.02, reverse=True):
        nonlocal cluster_id
        sorted_by_coord = sorted(locations, key=lambda loc: loc[coord_key])
        clusters = []
        for loc in sorted_by_coord:
            if not clusters:
                clusters.append([loc])
                continue
            last_cluster = clusters[-1]
            if abs(loc[coord_key] - last_cluster[-1][coord_key]) <= tolerance:
                last_cluster.append(loc)
            else:
                clusters.append([loc])

        def index_sort_key(loc):
            try:
                return (0, int(loc['index']))
            except (ValueError, TypeError):
                return (1, str(loc['index']))

        sorted_clusters = []
        for cluster in clusters:
            if len(cluster) > 1:
                sorted_cluster = sorted(cluster, key=index_sort_key)
                label_values = []
                for loc in sorted_cluster:
                    try:
                        label_values.append(str(int(loc['index'])))
                    except (ValueError, TypeError):
                        label_values.append(str(loc['index']))
                cluster_label = ', '.join(label_values)
                for loc in sorted_cluster:
                    loc['cluster_id'] = cluster_id
                    loc['cluster_label'] = cluster_label
                cluster_id += 1
                sorted_clusters.append(sorted_cluster)
            else:
                sorted_clusters.append(cluster)

        result = [loc for cluster in sorted_clusters for loc in cluster]
        if reverse:
            result.reverse()
        return result
    
    distinctClustersByLabel = {}

    groups['right'] = sort_by_coordinate_then_index(groups['right'], 'lon', 0.03)
    groups['left'] = sort_by_coordinate_then_index(groups['left'], 'lon', 0.03)
    groups['top'] = sort_by_coordinate_then_index(groups['top'], 'lat', 0.02, False)
    groups['bottom'] = sort_by_coordinate_then_index(groups['bottom'], 'lat', 0.02, False)
    
    # Identify and move isolated clusters
    def extract_isolated_clusters(groups, isolation_threshold=0.5):
        """Extract clusters that are isolated from other clusters/locations"""
        all_locs = groups['right'] + groups['left'] + groups['top'] + groups['bottom']
        
        # Build a map of cluster IDs to their locations
        cluster_map = {}
        for loc in all_locs:
            cluster_id = loc.get('cluster_id')
            if cluster_id is not None:
                if cluster_id not in cluster_map:
                    cluster_map[cluster_id] = []
                cluster_map[cluster_id].append(loc)
        
        # Calculate centroid for each cluster
        def get_centroid(locs):
            lat_avg = np.mean([loc['lat'] for loc in locs])
            lon_avg = np.mean([loc['lon'] for loc in locs])
            return lat_avg, lon_avg
        
        # Calculate great-circle distance in degrees (approximate)
        def distance_degrees(lat1, lon1, lat2, lon2):
            return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        
        # Identify isolated clusters
        isolated_cluster_ids = set()
        for cluster_id, cluster_locs in cluster_map.items():
            centroid_lat, centroid_lon = get_centroid(cluster_locs)
            
            # Find nearest neighbor (any other location or cluster)
            min_distance = float('inf')
            for loc in all_locs:
                if loc.get('cluster_id') != cluster_id:
                    dist = distance_degrees(centroid_lat, centroid_lon, loc['lat'], loc['lon'])
                    min_distance = min(min_distance, dist)
            
            # If no nearby neighbors, mark as isolated
            if min_distance > isolation_threshold:
                isolated_cluster_ids.add(cluster_id)
        
        # Move isolated clusters to isolated group
        for edge in ['right', 'left', 'top', 'bottom']:
            isolated_locs = [loc for loc in groups[edge] 
                           if loc.get('cluster_id') in isolated_cluster_ids]
            groups[edge] = [loc for loc in groups[edge] 
                          if loc.get('cluster_id') not in isolated_cluster_ids]
            groups['isolated'].extend(isolated_locs)
        
        print(f"Isolated clusters: {len(isolated_cluster_ids)}")
    
    extract_isolated_clusters(groups, isolation_threshold=1)
    
    print(groups)
    
    return groups
    
    """
    Ideal:
        right: 34
        left: 34
        top: 33
        bottom: 36
    """
  

def get_evenly_spaced_positions(edge, n, extent, buffer=0.4, spacing=0.25):
    left, right, bottom, top = extent
    if n == 0:
        return []
    # Labels are now *inside* the plot
    if edge in ['top', 'bottom']:
        if n > 1:
            xs = np.linspace(left + buffer*1.5, right - buffer*1.5, n)
        else:
            xs = np.array([(left + right)/2])
        ys = np.full(n, top - buffer/2) if edge == 'top' else np.full(n, bottom + buffer/2)
        return list(zip(xs, ys))
    elif edge in ['left', 'right']:
        if n > 1:
            ys = np.linspace(bottom + buffer, top - buffer, n)
        else:
            ys = np.array([(bottom + top)/2])
        xs = np.full(n, left + buffer) if edge == 'left' else np.full(n, right - buffer)
        return list(zip(xs, ys))
    else:
        raise ValueError(f"Unknown edge: {edge}")

def plot_uk_map(locations, output_path, dpi=300):
    fig = plt.figure(figsize=(18, 21))  # Large map size
    ax = plt.axes(projection=ccrs.Mercator())
    extent = MAP_EXTENT  # [left, right, bottom, top] in lat/lon
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    #ax.gridlines(draw_labels=True)

    # Key UK cities (lat, lon)
    cities = {
        'London': (51.5074, -0.1278, -0.05),
        'Birmingham': (52.4862, -1.8904, 0.025),
        'Cardiff': (51.4816, -3.1791, -0.05),
        'Bristol': (51.4545, -2.5879, 0),
        'Exeter': (50.7260, -3.5275, 0),
        'Cambridge': (52.1951, 0.1313, -0.05),
        'Taunton': (51.0153, -3.1068, -0.05),
        'Plymouth': (50.3755, -4.1427, -0.025),
        'Portsmouth': (50.8198, -1.0880, 0),
        'Oxford': (51.7520, -1.2577, -0.05),
        'Aberystwyth': (52.4153, -4.0829, -0.05),
        'Mablethorpe': (53.3409, 0.2611, -0.05)
    }
    for city, (lat, lon, labelLat) in cities.items():
        ax.plot(lon, lat, 's', color='red', markersize=3, transform=ccrs.PlateCarree())
        ax.text(
            lon+0.075, lat+labelLat, city, fontsize=10, color='#544C4A', transform=ccrs.PlateCarree(),
            bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.75),
            zorder=4
        )

    # Assign labels to custom edges
    edge_labels = assign_labels_custom(locations, extent)

    # Get label positions for each edge, now with spacing and inside edge
    label_infos = []
    for edge in ['top', 'right', 'bottom', 'left']:
        locs = edge_labels[edge]
        grouped_locs = []
        seen_cluster_ids = set()
        for loc in locs:
            cluster_id = loc.get('cluster_id')
            if cluster_id is not None:
                if cluster_id in seen_cluster_ids:
                    continue
                seen_cluster_ids.add(cluster_id)
            grouped_locs.append(loc)

        positions = get_evenly_spaced_positions(edge, len(grouped_locs), extent, buffer=0.4, spacing=0.3)
        for loc, (lx, ly) in zip(grouped_locs, positions):
            label = loc.get('cluster_label', str(loc['index']))
            label_infos.append({'loc': loc, 'lx': lx, 'ly': ly, 'label': label})

    # Plot markers for all locations on the edge
    for edge in ['top', 'right', 'bottom', 'left']:
        for loc in edge_labels[edge]:
            ax.plot(loc['lon'], loc['lat'], 'bo', markersize=3, transform=ccrs.PlateCarree())

    # Plot leader lines and labels
    for info in label_infos:
        loc = info['loc']
        lx, ly = info['lx'], info['ly']
        label = info['label']
        ax.plot([loc['lon'], lx], [loc['lat'], ly], color='#BDB7AB', alpha=0.7, linewidth=1, zorder=1, transform=ccrs.PlateCarree())
        ax.text(
            lx, ly, label,
            fontsize=10, color='#544C4A', weight='bold',
            ha='center', va='center', zorder=3,
            bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.75),
            transform=ccrs.PlateCarree()
        )

    # Draw isolated cluster labels directly on the map
    for loc in edge_labels['isolated']:
        ax.plot(loc['lon'], loc['lat'], 'bo', markersize=3, transform=ccrs.PlateCarree())
        label = loc.get('cluster_label', str(loc['index']))
        ax.text(
            loc['lon'] + 0.02, loc['lat'] + 0.02, label,
            fontsize=10, color='#544C4A', weight='bold',
            ha='left', va='bottom', zorder=3,
            bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.75),
            transform=ccrs.PlateCarree()
        )

    # Draw distinct labels next to their markers instead of on the edges
    for loc in edge_labels['distinct']:
        ax.plot(loc['lon'], loc['lat'], 'bo', markersize=3, transform=ccrs.PlateCarree())
        ax.text(
            loc['lon'] + 0.00, loc['lat'] + 0.02, str(loc['index']),
            fontsize=10, color='#544C4A', weight='bold',
            ha='left', va='bottom', zorder=3,
            bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.75),
            transform=ccrs.PlateCarree()
        )

    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"Map saved to {output_path}")

def main():
    csv_path = os.path.join(CSV_FOLDER, CSV_FILENAME)
    print(f"Reading locations from {csv_path}...")
    locations = get_locations_from_csv(csv_path)
    filtered_locations = filterNonUKLocations(locations)
    print(f"Locations count: {len(locations)}")
    print(f"Filtered locations count: {len(filtered_locations)}")
    print("Plotting map...")
    plot_uk_map(filtered_locations, OUTPUT_IMAGE, dpi=DPI)
    print("index 99 coordinates are incorrect")

if __name__ == '__main__':
    main()