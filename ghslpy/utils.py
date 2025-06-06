"""
Utility functions for ghslpy.
"""
from tabulate import tabulate
from .products import PRODUCTS


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
