import geopandas as gpd
import pandas as pd

# Load the buffered walkshed GeoJSON file
buffered_walksheds = gpd.read_file('buffer.geojson')

# Load the amenities CSV file
amenities_df = pd.read_csv('ballotbox.csv')

# Convert the DataFrame to a GeoDataFrame using EPSG:4326 for geographic coordinates
gdf_amenities = gpd.GeoDataFrame(
   amenities_df,
   geometry=gpd.points_from_xy(amenities_df.xcoord, amenities_df.ycoord),
   crs="EPSG:4326" 
)

# If the buffered walksheds are truly in EPSG:32610, project amenities to match
gdf_amenities = gdf_amenities.to_crs(buffered_walksheds.crs)

# Spatial join to find reachable amenities (those that intersect with buffered walksheds)
reachable_amenities = gpd.sjoin(gdf_amenities, buffered_walksheds, how="inner", predicate='intersects')

# Find unreachable amenities by performing an outer join and filtering out those found in the inner join
all_amenities_with_join_flag = gpd.sjoin(gdf_amenities, buffered_walksheds, how="left", op='intersects')
unreachable_amenities = all_amenities_with_join_flag[all_amenities_with_join_flag.index_right.isnull()].copy()

# Drop the index_right column resulting from spatial joins
reachable_amenities.drop(columns=['index_right'], inplace=True)
unreachable_amenities.drop(columns=['index_right'], inplace=True)

# Export reachable and unreachable amenities to separate CSV files
reachable_amenities.to_csv('reachable_amenities.csv', index=False)
unreachable_amenities.to_csv('unreachable_amenities.csv', index=False)

print("Reachable and unreachable amenities exported successfully.")


