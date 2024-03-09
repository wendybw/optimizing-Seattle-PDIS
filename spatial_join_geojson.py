import geopandas as gpd

# Load the buffered walkshed GeoJSON file
buffered_walksheds = gpd.read_file('buffer.geojson')

# Load your amenities GeoJSON file
gdf_amenities = gpd.read_file('clinic.geojson')

# Ensure the CRS for amenities matches that of the buffered walksheds, reproject if necessary
if gdf_amenities.crs != buffered_walksheds.crs:
    gdf_amenities = gdf_amenities.to_crs(buffered_walksheds.crs)

# Perform spatial joins for reachable and unreachable amenities
reachable_amenities = gpd.sjoin(gdf_amenities, buffered_walksheds, how="inner", predicate='intersects')
unreachable_amenities = gpd.sjoin(gdf_amenities, buffered_walksheds, how="left", predicate='intersects')
unreachable_amenities = unreachable_amenities[unreachable_amenities.index_right.isnull()]

# Cleanup before exporting
reachable_amenities.drop(columns=['index_right'], inplace=True)
unreachable_amenities.drop(columns=['index_right'], inplace=True)

# Export results to GeoJSON
if not reachable_amenities.empty:
    reachable_amenities.to_file('reachable_clinic.geojson', driver='GeoJSON')
else:
    print("No reachable amenities found.")

if not unreachable_amenities.empty:
    unreachable_amenities.to_file('unreachable_clinic.geojson', driver='GeoJSON')
else:
    print("No unreachable amenities found.")

print("Reachable and unreachable amenities exported successfully.")
