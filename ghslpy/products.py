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
        }
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
