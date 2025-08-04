"""
Utility functions for ghslpy.
"""
from tabulate import tabulate
from .products import PRODUCTS
import osmnx as ox
import pandas as pd
import geopandas as gpd
import shapely


def list_products():
    """
    Print a table of available products and their options.
    """
    headers = ["Product", "Description", "Available Epochs", "Available Resolutions", "Classifications"]
    rows = []
    
    for product_name, info in PRODUCTS.items():
        epochs = ", ".join(map(str, info["epochs"]))
        resolutions = ", ".join(info["resolutions"])
        classifications = ", ".join(info["classifications"]) if info["classifications"] else "N/A"
        
        rows.append([
            product_name,
            info["description"],
            epochs,
            resolutions,
            classifications
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    
def list_product_options(product):
    """
    Print detailed information about a specific product.
    
    Args:
        product (str): Product name (e.g., "GHS-BUILT-S")
    """
    from .products import get_product_info
    
    try:
        info = get_product_info(product)
        
        print(f"Product: {product}")
        print(f"Description: {info['description']}")
        print(f"Available epochs: {', '.join(map(str, info['epochs']))}")
        print(f"Available resolutions: {', '.join(info['resolutions'])}")
        
        if info["classifications"]:
            print(f"Available classifications: {', '.join(info['classifications'])}")
        else:
            print("Classifications: N/A")
            
        print(f"Default resolution: {info['default_resolution']}")
        
        if info["default_classification"]:
            print(f"Default classification: {info['default_classification']}")
    
    except ValueError as e:
        print(f"Error: {e}")

def find_region(query: str | list) -> gpd.GeoDataFrame:
    """
    Find the boundary of a region using OpenStreetMap.

    Parameters:
    - query (str | list): The query to search for the region.

    Returns:
    - gpd.GeoDataFrame: The boundary of the region.
    """
    if isinstance(query, list):
        gdf = gpd.GeoDataFrame(
            pd.concat(
                [ox.geocode_to_gdf(query=region) for region in query],
                ignore_index=True,
            ),
            geometry="geometry",
        )
        return gdf
    else:
        gdf = ox.geocode_to_gdf(query=query)
        return gdf

def download_gadm(iso3_code: str, adm_level: int = 0):
    """
    Download GADM data for a specific country and administrative level.

    Parameters:
    - iso3_code (str): ISO 3 code of the country.
    - adm_level (int): Administrative level (0 for country, 1 for province, 2 for district).

    Returns:
    - gpd.GeoDataFrame: The GADM data for the specified country and administrative level.
    """
    return gpd.read_file(
        f"https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{iso3_code}.gpkg",
        layer=f"ADM_ADM_{adm_level}",
    )

def wkt_as_gdf(wkt: str) -> gpd.GeoDataFrame:
    """
    Convert a WKT string to a GeoDataFrame.
    """
    return gpd.GeoDataFrame(
        geometry=[shapely.wkt.loads(wkt)],
        crs="EPSG:4326",
    )

def load_csv(csv_path: str, kwargs: dict = {}) -> gpd.GeoDataFrame:
    """
    Load a CSV file into a GeoDataFrame.
    """
    df = pd.read_csv(csv_path, **kwargs)
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)
    return gpd.GeoDataFrame(df, geometry='geometry')
    