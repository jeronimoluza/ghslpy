import os
import tempfile
import zipfile
import urllib.request
from pathlib import Path
import geopandas as gpd
import xarray as xr
import rioxarray
import numpy as np
from .products import validate_product_options


BASE_URL = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL"
FILL_VALUE = -200


def download(
    products, epoch, resolution=None, classification=None, region=None
):
    """
    Download GHSL products for a single epoch or multiple epochs.

    Args:
        products (str or list): GHSL product name(s) (e.g., "GHS-BUILT-S" or ["GHS-BUILT-S", "GHS-POP"])
        epoch (int or list): Year(s) of the data (e.g., 2020 or [1975, 1990, 2000, 2015])
        resolution (str, optional): Resolution of the data (e.g., "100m").
        classification (str, optional): Classification type (e.g., "RES+NRES").
        region (shapely.geometry.Polygon, optional): Region of interest. If None, global data is downloaded.

    Returns:
        xarray.Dataset: Dataset containing the downloaded data, with a time dimension if epoch is a list
                        and data from all requested products as separate variables
    """
    # Convert products to list if it's a string
    if isinstance(products, str):
        products = [products]
    
    if isinstance(epoch, list):
        # Download data for each epoch and each product
        all_datasets = []
        for e in epoch:
            epoch_datasets = []
            for product in products:
                ds = download_single(
                    product, e, resolution, classification, region
                )
                # Add time coordinate using the epoch year
                time_coord = f"{e}-01-01"  # Format as YYYY-MM-DD
                ds = ds.expand_dims({"time": [time_coord]})
                epoch_datasets.append(ds)
            
            # Merge all products for this epoch
            if epoch_datasets:
                merged_epoch_ds = xr.merge(epoch_datasets)
                all_datasets.append(merged_epoch_ds)
            else:
                raise ValueError(
                    f"Failed to download data for epoch: {e}"
                )

        # Merge all datasets along the time dimension
        if all_datasets:
            merged_ds = xr.concat(all_datasets, dim="time")
            return merged_ds
        else:
            raise ValueError(
                f"Failed to download data for any of the epochs: {epoch}"
            )
    else:
        # Download data for each product for a single epoch
        product_datasets = []
        for product in products:
            ds = download_single(
                product, epoch, resolution, classification, region
            )
            time_coord = f"{epoch}-01-01"  # Format as YYYY-MM-DD
            ds = ds.expand_dims({"time": [time_coord]})
            product_datasets.append(ds)
        
        # Merge all products
        if product_datasets:
            merged_ds = xr.merge(product_datasets)
            return merged_ds
        else:
            raise ValueError(
                f"Failed to download data for epoch: {epoch}"
            )


def download_single(
    product, epoch, resolution=None, classification=None, region=None
):
    """
    Download GHSL products.

    Args:
        product (str): GHSL product name (e.g., "GHS-BUILT-S")
        epoch (int): Year of the data (e.g., 2020)
        resolution (str, optional): Resolution of the data (e.g., "100m").
                                   If not provided, uses the default for the product.
        classification (str, optional): Classification type (e.g., "RES+NRES").
                                      If not provided, uses the default for the product if applicable.
        region (shapely.geometry.Polygon, optional): Region of interest. If None, global data is downloaded.

    Returns:
        xarray.Dataset: Dataset containing the downloaded data
    """
    # Validate and normalize product options
    product_normalized, epoch, resolution, classification = (
        validate_product_options(product, epoch, resolution, classification)
    )

    # Set default projection to Mollweide (54009)
    projection = "54009"

    # Handle resolution (remove 'm' if present)
    resolution_value = resolution.replace("m", "")

    # Construct version string (currently hardcoded to V1-0)
    version = "V1-0"

    # Determine if we need global or tiled data
    if region is None:
        # Global download
        return _download_global(
            product_normalized,
            epoch,
            projection,
            resolution_value,
            version,
            classification,
        )
    else:
        # Tiled download based on region
        return _download_tiles(
            product_normalized,
            epoch,
            projection,
            resolution_value,
            version,
            region,
            classification,
        )


def _download_global(
    product, epoch, projection, resolution, version, classification=None
):
    """
    Download global GHSL data.
    """
    # Get product info to determine URL pattern
    from .products import get_product_info

    product_info = get_product_info(product.replace("_", "-"))

    # Get the appropriate URL pattern based on classification
    url_pattern = product_info["url_pattern"].get(
        classification, product_info["url_pattern"].get(None)
    )

    # Format the base product name using the pattern
    base_product_name = url_pattern.format(
        product=product, epoch=epoch, classification=classification
    )

    # Construct URL for global file
    url_parts = [
        BASE_URL,
        f"{product}_GLOBE_R2023A",
        f"{base_product_name}_GLOBE_R2023A_{projection}_{resolution}",
        version,
        f"{base_product_name}_GLOBE_R2023A_{projection}_{resolution}_{version.replace('-', '_')}.zip",
    ]

    url = "/".join(url_parts)

    # Download and process the data
    return _download_and_process_zip(url)


def _download_tiles(
    product,
    epoch,
    projection,
    resolution,
    version,
    region,
    classification=None,
):
    """
    Download GHSL data tiles that intersect with the given region.
    """
    # Get product info to determine URL pattern
    from .products import get_product_info

    product_info = get_product_info(product.replace("_", "-"))

    # Get the appropriate URL pattern based on classification
    url_pattern = product_info["url_pattern"].get(
        classification, product_info["url_pattern"].get(None)
    )

    # Format the base product name using the pattern
    base_product_name = url_pattern.format(
        product=product, epoch=epoch, classification=classification
    )

    # Load the tiles GeoJSON
    tiles_path = Path(__file__).parent.parent / "assets" / "ghsl_tiles.geojson"
    tiles_gdf = gpd.read_file(tiles_path)

    if not isinstance(region, gpd.GeoDataFrame):
        region_gdf = gpd.GeoDataFrame(geometry=[region], crs="EPSG:4326")
    else:
        region_gdf = region

    # Find tiles that intersect with the region
    intersecting_tiles = tiles_gdf[
        tiles_gdf.intersects(region_gdf.union_all())
    ]

    if len(intersecting_tiles) == 0:
        raise ValueError(
            "The provided region does not intersect with any GHSL tiles"
        )

    # Download each tile and merge them
    datasets = []
    for _, tile in intersecting_tiles.iterrows():
        tile_id = tile["tile_id"]

        # Construct URL for the tile
        url_parts = [
            BASE_URL,
            f"{product}_GLOBE_R2023A",
            f"{base_product_name}_GLOBE_R2023A_{projection}_{resolution}",
            version,
            "tiles",
            f"{base_product_name}_GLOBE_R2023A_{projection}_{resolution}_{version.replace('-', '_')}_{tile_id}.zip",
        ]

        url = "/".join(url_parts)

        # Clip to the region of interest
        # Convert region to the same CRS as the data
        region_gdf = region_gdf.to_crs(f"ESRI:{projection}")
        # Download and process the tile
        try:
            ds = _download_and_process_zip(url, region_gdf)
            datasets.append(ds)
        except Exception as e:
            print(f"Warning: Failed to download tile {tile_id}: {e}")

    if not datasets:
        raise ValueError(
            "Failed to download any tiles for the provided region"
        )

    # Merge all datasets
    merged_ds = xr.merge(datasets)
    # merged_ds = merged_ds.fillna(FILL_VALUE)  # ADDRESS THIS

    return merged_ds


def _download_and_process_zip(url, region_gdf):
    """
    Download a zip file from URL, extract it, and load the data as an xarray Dataset.
    """
    # Create a temporary directory for downloading and extracting files

    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the zip file
        zip_path = os.path.join(temp_dir, "download.zip")
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, zip_path)

        # Extract the zip file
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find all TIF files in the extracted directory
        tif_files = []
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(".tif"):
                    tif_files.append(os.path.join(root, file))

        if not tif_files:
            raise ValueError(
                f"No TIF files found in the downloaded zip from {url}"
            )

        # Load the TIF files as xarray Dataset
        datasets = []
        fillvalues = []

        for tif_file in tif_files:
            ds = rioxarray.open_rasterio(tif_file)
            # Convert to a dataset with a meaningful variable name based on the filename
            tif_name = os.path.basename(tif_file).split(".")[0]
            var_name = "_".join(tif_name.split("_")[:2])
            # Clip the merged dataset to the region
            ds = ds.rio.clip(
                region_gdf.geometry,
                region_gdf.crs,
            )
            fillvalues.append(ds._FillValue)
            ds = ds.fillna(ds._FillValue)
            ds = ds.where(ds != ds._FillValue)
            ds = ds.to_dataset(name=var_name)
            datasets.append(ds)

        assert (
            np.mean(fillvalues) == fillvalues[0]
        ), "Fill values change between files"
        fill_value = fillvalues[0]

        # Merge all datasets
        if len(datasets) > 1:
            return xr.merge(datasets, fill_value=fill_value)
        else:
            return datasets[0]
