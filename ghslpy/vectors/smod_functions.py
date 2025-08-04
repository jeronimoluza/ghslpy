import geopandas as gpd
import pandas as pd

def smod_year_of_transition(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Transform GHS-SMOD already vectorized data into a GeoDataFrame with year of transition
    """
    gdf = gdf[gdf.GHS_SMOD == 'Urban Centre grid cell']
    gdf['year'] = pd.to_datetime(gdf['date']).dt.year
    yearly = gdf.dissolve(by='year')
    yearly = yearly.sort_index()

    new_geometries = []
    past_union = None

    for year, row in yearly.iterrows():
        current_geom = row.geometry

        if past_union is not None:
            new_geom = current_geom.difference(past_union)
        else:
            new_geom = current_geom
        new_geometries.append({'year': year, 'geometry': new_geom})

        past_union = current_geom if past_union is None else past_union.union(current_geom)

    incremental_gdf = gpd.GeoDataFrame(new_geometries, crs=gdf.crs)
    return incremental_gdf