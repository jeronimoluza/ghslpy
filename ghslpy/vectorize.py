from geocube.vector import vectorize as geocube_vectorize
import xarray as xr

def vectorize(data: xr.Dataset, variable_name: str ):
    gdf = geocube_vectorize(data.to_array().squeeze().astype(float))
    gdf = gdf.rename(columns={"_data": variable_name})
    return gdf.to_crs("EPSG:4326")
