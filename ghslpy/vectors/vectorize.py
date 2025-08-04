from geocube.vector import vectorize as geocube_vectorize
import xarray as xr
import geopandas as gpd
import pandas as pd
from ..products import get_product_info

def vectorize(data: xr.Dataset):
    """
    Vectorize an xarray Dataset into a GeoDataFrame.
    
    Args:
        data (xr.Dataset): Dataset to vectorize
        
    Returns:
        geopandas.GeoDataFrame: Vectorized data with geometry and variable values
                               If the input has a time dimension, a 'date' column is added
                               If the data is GHS-SMOD, class values are converted to strings and a domain column is added
    """


    [var_name] = list(data.data_vars.keys())

    # Variable name for GHS_BUILT_C shows as GHS_BUILT
    if var_name == "GHS_BUILT":
        var_name = "GHS_BUILT_C"

    # Check if the dataset has a time dimension
    if 'time' in data.sizes and data.sizes['time'] > 1:
        # Initialize an empty list to store GeoDataFrames for each time slice
        gdfs = []
        
        # Process each time slice
        for time_val in data.time.values:
            # Extract the data for this time slice
            time_slice = data.sel(time=time_val)
            
            # Vectorize the time slice
            gdf = geocube_vectorize(time_slice.to_array().rename(var_name).squeeze().astype(float))
            
            # Add a date column with the time value
            date_str = pd.to_datetime(str(time_val)).strftime('%Y-%m-%d')
            gdf['date'] = date_str
            
            apply_classifications(gdf, var_name)
            
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
        
        apply_classifications(gdf, var_name)
        
        return gdf.to_crs("EPSG:4326")

def _apply_smod_classification(gdf):
    """
    Apply GHS-SMOD classification to a GeoDataFrame.
    Converts integer class values to string descriptions and adds a domain column.
    
    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame with GHS_SMOD values
    """
    # Get the GHS-SMOD product info
    smod_info = get_product_info("GHS-SMOD")
    
    # Create a copy of the original numeric values
    gdf['class_value'] = gdf['GHS_SMOD']
    
    # Map integer values to class descriptions
    class_mapping = smod_info.get("class_values", {})
    gdf['GHS_SMOD'] = gdf['GHS_SMOD'].map(lambda x: class_mapping.get(int(x), f"Unknown class {int(x)}"), na_action='ignore')
    
    # Add domain column (Urban domain or Rural domain)
    domain_mapping = smod_info.get("domains", {})
    gdf['domain'] = gdf['class_value'].map(lambda x: domain_mapping.get(int(x), "Unknown domain"), na_action='ignore')

def _apply_built_c_classification(gdf):
    """
    Apply GHS-BUILT-C classification to a GeoDataFrame.
    Converts integer class values to string descriptions.
    
    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame with GHS_BUILT_C values
    """
    # Get the GHS-BUILT-C product info
    built_c_info = get_product_info("GHS-BUILT-C")
    
    # Create a copy of the original numeric values
    gdf['class_value'] = gdf['GHS_BUILT_C']
    
    # Map integer values to class descriptions
    class_mapping = built_c_info.get("class_values", {})
    gdf['GHS_BUILT_C'] = gdf['GHS_BUILT_C'].map(lambda x: class_mapping.get(int(x), f"Unknown class {int(x)}"), na_action='ignore')

def apply_classifications(gdf, var_name):
    """
    Apply classifications to a GeoDataFrame based on the variable name.
    
    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame with variable values
        var_name (str): Name of the variable
    """
    # Handle GHS-SMOD classification if applicable
    if var_name == "GHS_SMOD":
        _apply_smod_classification(gdf)
    
    # Handle GHS-BUILT-C classification if applicable
    if var_name == "GHS_BUILT_C":
        _apply_built_c_classification(gdf)
