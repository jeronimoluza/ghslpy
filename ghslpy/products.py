"""
Product definitions and metadata for GHSL products.
"""

# Define available products and their metadata
PRODUCTS = {
    "GHS-BUILT-S": {
        "description": "Global Human Settlement Built-Up Surface",
        "epochs": [1975, 1980, 1985, 1990, 1995, 2000, 2015, 2018, 2020, 2025, 2030],
        "resolutions": ["100m", "1000m"],
        "classifications": ["RES+NRES", "NRES"],
        "default_resolution": "100m",
        "default_classification": "RES+NRES",
        "normalized_name": "GHS_BUILT_S",
        "url_pattern": {
            "RES+NRES": "{product}_E{epoch}",  # Default, no suffix needed
            "NRES": "{product}_NRES_E{epoch}"  # Add NRES suffix
        }
    },
    "GHS-BUILT-H": {
        "description": "Global Human Settlement Built-Up Height",
        "epochs": [2018],
        "resolutions": ["100m"],
        "classifications": ["AGBH", "ANBH"],
        "default_resolution": "100m",
        "default_classification": "AGBH",
        "normalized_name": "GHS_BUILT_H",
        "url_pattern": {
            "AGBH": "{product}_{classification}_E{epoch}",  # Always include classification
            "ANBH": "{product}_{classification}_E{epoch}"   # Always include classification
        }
    },
    "GHS-BUILT-V": {
        "description": "Global Human Settlement Built-Up Volume",
        "epochs": [1975, 1980, 1985, 1990, 1995, 2000, 2015, 2020, 2025, 2030],
        "resolutions": ["100m", "1000m"],
        "classifications": ["RES+NRES", "NRES"],
        "default_resolution": "100m",
        "default_classification": "RES+NRES",
        "normalized_name": "GHS_BUILT_V",
        "url_pattern": {
            "RES+NRES": "{product}_E{epoch}",  # Default, no suffix needed
            "NRES": "{product}_NRES_E{epoch}"  # Add NRES suffix
        }
    },
    "GHS-POP": {
        "description": "Global Human Settlement Population",
        "epochs": [1975, 1980, 1985, 1990, 1995, 2000, 2015, 2020, 2025, 2030],
        "resolutions": ["100m", "1000m"],
        "classifications": None,
        "default_resolution": "100m",
        "default_classification": None,
        "normalized_name": "GHS_POP",
        "url_pattern": {
            None: "{product}_E{epoch}"  # Standard pattern with no classification
        }
    },
    "GHS-SMOD": {
        "description": "Global Human Settlement Settlement Model",
        "epochs": [1975, 1980, 1985, 1990, 1995, 2000, 2015, 2020, 2025, 2030],
        "resolutions": ["1000m"],
        "classifications": None,
        "default_resolution": "1000m",
        "default_classification": None,
        "normalized_name": "GHS_SMOD",
        "url_pattern": {
            None: "{product}_E{epoch}"  # Standard pattern with no classification
        },
        "class_values": {
            30: "Urban Centre grid cell",
            23: "Dense Urban Cluster grid cell",
            22: "Semi-dense Urban Cluster grid cell",
            21: "Suburban or per-urban grid cell",
            13: "Rural cluster grid cell",
            12: "Low Density Rural grid cell",
            11: "Very low density rural grid cell",
            10: "Water grid cell"
        },
        "domains": {
            30: "Urban domain",
            23: "Urban domain",
            22: "Urban domain",
            21: "Urban domain",
            13: "Rural domain",
            12: "Rural domain",
            11: "Rural domain",
            10: "Rural domain"
        }
    },
    "GHS-BUILT-C": {
        "description": "Global Human Settlement Built-up Characteristics",
        "epochs": [2018],
        "resolutions": ["10m"],
        "classifications": ["MSZ", "FUN"],
        "default_resolution": "10m",
        "default_classification": "MSZ",
        "normalized_name": "GHS_BUILT_C",
        "url_pattern": {
            "MSZ": "{product}_{classification}_E{epoch}",  # Always include classification
            "FUN": "{product}_{classification}_E{epoch}"   # Always include classification
        },
        "class_values": {
            1: "MSZ, open spaces, low vegetation surfaces NDVI <= 0.3",
            2: "MSZ, open spaces, medium vegetation surfaces 0.3 < NDVI <= 0.5",
            3: "MSZ, open spaces, high vegetation surfaces NDVI > 0.5",
            4: "MSZ, open spaces, water surfaces LAND < 0.5",
            5: "MSZ, open spaces, road surfaces",
            11: "MSZ, built spaces, residential, building height <= 3m",
            12: "MSZ, built spaces, residential, 3m < building height <= 6m",
            13: "MSZ, built spaces, residential, 6m < building height <= 15m",
            14: "MSZ, built spaces, residential, 15m < building height <= 30m",
            15: "MSZ, built spaces, residential, building height > 30m",
            21: "MSZ, built spaces, non-residential, building height <= 3m",
            22: "MSZ, built spaces, non-residential, 3m < building height <= 6m",
            23: "MSZ, built spaces, non-residential, 6m < building height <= 15m",
            24: "MSZ, built spaces, non-residential, 15m < building height <= 30m",
            25: "MSZ, built spaces, non-residential, building height > 30m",
            
        },
    }
}

def get_product_info(product):
    """
    Get information about a specific product.
    
    Args:
        product (str): Product name (e.g., "GHS-BUILT-S")
        
    Returns:
        dict: Product metadata
        
    Raises:
        ValueError: If product is not supported
    """
    if product not in PRODUCTS:
        available_products = ", ".join(PRODUCTS.keys())
        raise ValueError(f"Product '{product}' not supported. Available products: {available_products}")
    
    return PRODUCTS[product]

def validate_product_options(product, epoch, resolution=None, classification=None):
    """
    Validate product options and return normalized values.
    
    Args:
        product (str): Product name (e.g., "GHS-BUILT-S")
        epoch (int): Year of the data
        resolution (str, optional): Resolution of the data
        classification (str, optional): Classification type
        
    Returns:
        tuple: (normalized_product_name, epoch, resolution, classification)
        
    Raises:
        ValueError: If any option is invalid
    """
    product_info = get_product_info(product)
    
    # Validate epoch
    if epoch not in product_info["epochs"]:
        available_epochs = ", ".join(map(str, product_info["epochs"]))
        raise ValueError(f"Epoch {epoch} not available for {product}. Available epochs: {available_epochs}")
    
    # Validate and set default resolution if needed
    if resolution is None:
        resolution = product_info["default_resolution"]
    elif resolution not in product_info["resolutions"]:
        available_resolutions = ", ".join(product_info["resolutions"])
        raise ValueError(f"Resolution '{resolution}' not available for {product}. Available resolutions: {available_resolutions}")
    
    # Validate and set default classification if needed
    if product_info["classifications"] is not None:
        if classification is None:
            classification = product_info["default_classification"]
        elif classification not in product_info["classifications"]:
            available_classifications = ", ".join(product_info["classifications"])
            raise ValueError(f"Classification '{classification}' not available for {product}. Available classifications: {available_classifications}")
    else:
        # Product doesn't support classifications
        if classification is not None:
            raise ValueError(f"Product {product} does not support classifications")
        classification = None
    
    return product_info["normalized_name"], epoch, resolution, classification
