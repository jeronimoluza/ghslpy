from geocube.vector import vectorize as geocube_vectorize
import xarray as xr
import geopandas as gpd
import pandas as pd

def vectorize(data: xr.Dataset):
    """
    Vectorize an xarray Dataset into a GeoDataFrame.
    
    Args:
        data (xr.Dataset): Dataset to vectorize
        
    Returns:
        geopandas.GeoDataFrame: Vectorized data with geometry and variable values
                               If the input has a time dimension, a 'date' column is added
    """
    # Check if the dataset has a time dimension
    if 'time' in data.sizes and data.sizes['time'] > 1:
        # Initialize an empty list to store GeoDataFrames for each time slice
        gdfs = []
        
        # Process each time slice
        for time_val in data.time.values:
            # Extract the data for this time slice
            time_slice = data.sel(time=time_val)
            
            [var_name] = list(time_slice.data_vars.keys())
            # Vectorize the time slice
            gdf = geocube_vectorize(time_slice.to_array().rename(var_name).squeeze().astype(float))
            
            # Add a date column with the time value
            date_str = pd.to_datetime(str(time_val)).strftime('%Y-%m-%d')
            gdf['date'] = date_str
            
            gdfs.append(gdf)
        
        # Combine all GeoDataFrames
        if gdfs:
            combined_gdf = pd.concat(gdfs, ignore_index=True)
            return combined_gdf.to_crs("EPSG:4326")
        else:
            raise ValueError("No valid data found for vectorization")
    else:
        # Original behavior for datasets without time dimension
        gdf = geocube_vectorize(data.to_array().rename(var_name).squeeze().astype(float))
        return gdf.to_crs("EPSG:4326")
