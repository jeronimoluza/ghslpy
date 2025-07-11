import numpy as np
import xarray as xr
import scipy.ndimage as ndimage
from skimage import measure, filters, morphology
from typing import Optional, Union, Tuple, List


def population_density(pop_data: xr.DataArray, pixel_area_km2: float = 0.01) -> xr.DataArray:
    """
    Convert raw population counts to density (people per km²) using 100m x 100m pixels.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population count data array
    pixel_area_km2 : float, optional
        Area of a pixel in km², by default 0.01 (100m x 100m)
        
    Returns
    -------
    xr.DataArray
        Population density in people per km²
    """
    density = pop_data / pixel_area_km2
    density.attrs['units'] = 'people/km²'
    density.attrs['long_name'] = 'Population density'
    return density


def absolute_population_change(pop_data: xr.DataArray, time_dim: str = 'time') -> xr.DataArray:
    """
    Calculate absolute population change between consecutive time periods.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array with a time dimension
    time_dim : str, optional
        Name of the time dimension, by default 'time'
        
    Returns
    -------
    xr.DataArray
        Absolute population change between consecutive periods
    """
    # Shift the data along the time dimension to calculate differences
    pop_shifted = pop_data.shift({time_dim: -1})
    change = pop_shifted - pop_data
    
    # Drop the last time period which will be NaN after the shift
    change = change.isel({time_dim: slice(0, -1)})
    
    change.attrs['units'] = 'people'
    change.attrs['long_name'] = 'Absolute population change'
    return change


def relative_population_change(pop_data: xr.DataArray, time_dim: str = 'time', 
                             min_pop: float = 1.0) -> xr.DataArray:
    """
    Calculate relative (percentage) population change between consecutive time periods.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array with a time dimension
    time_dim : str, optional
        Name of the time dimension, by default 'time'
    min_pop : float, optional
        Minimum population threshold to avoid division by zero, by default 1.0
        
    Returns
    -------
    xr.DataArray
        Relative population change (percentage)
    """
    # Calculate absolute change
    abs_change = absolute_population_change(pop_data, time_dim)
    
    # Get the base population for each period (avoiding division by zero)
    base_pop = pop_data.isel({time_dim: slice(0, -1)})
    base_pop = xr.where(base_pop < min_pop, min_pop, base_pop)
    
    # Calculate percentage change
    rel_change = (abs_change / base_pop) * 100
    
    rel_change.attrs['units'] = '%'
    rel_change.attrs['long_name'] = 'Relative population change'
    return rel_change


def population_momentum(pop_data: xr.DataArray, time_dim: str = 'time') -> xr.DataArray:
    """
    Calculate population momentum as the direction and magnitude of change vector.
    This is a composite metric that combines both direction and magnitude of change.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array with a time dimension
    time_dim : str, optional
        Name of the time dimension, by default 'time'
        
    Returns
    -------
    xr.DataArray
        Population momentum (positive values indicate growth momentum,
        negative values indicate decline momentum, magnitude indicates strength)
    """
    # Calculate absolute change
    abs_change = absolute_population_change(pop_data, time_dim)
    
    # Calculate the rate of change of the change (acceleration)
    change_shifted = abs_change.shift({time_dim: -1})
    acceleration = change_shifted - abs_change
    
    # Drop the last time period which will be NaN after the shift
    acceleration = acceleration.isel({time_dim: slice(0, -1)})
    
    # Combine the direction of change with its acceleration to get momentum
    # We use the sign of the change multiplied by the magnitude of acceleration
    base_change = abs_change.isel({time_dim: slice(0, -1)})
    momentum = xr.where(
        base_change == 0,
        acceleration,  # If no change, momentum is just acceleration
        np.sign(base_change) * np.abs(acceleration)  # Otherwise, direction * magnitude
    )
    
    momentum.attrs['units'] = 'people/time²'
    momentum.attrs['long_name'] = 'Population momentum'
    return momentum


def change_detection_flag(pop_data: xr.DataArray, threshold: float = 10.0, 
                         relative: bool = True, time_dim: str = 'time') -> xr.DataArray:
    """
    Create a binary indicator of significant population change using thresholds.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array with a time dimension
    threshold : float, optional
        Threshold for significant change, by default 10.0
        (10% if relative=True, 10 people if relative=False)
    relative : bool, optional
        Whether to use relative or absolute change, by default True
    time_dim : str, optional
        Name of the time dimension, by default 'time'
        
    Returns
    -------
    xr.DataArray
        Binary flag indicating significant change (1) or not (0)
    """
    if relative:
        change = relative_population_change(pop_data, time_dim)
        # Flag significant change in either direction
        flag = xr.where(np.abs(change) >= threshold, 1, 0)
    else:
        change = absolute_population_change(pop_data, time_dim)
        # Flag significant change in either direction
        flag = xr.where(np.abs(change) >= threshold, 1, 0)
    
    flag.attrs['units'] = 'binary'
    flag.attrs['long_name'] = 'Significant population change flag'
    flag.attrs['threshold'] = f"{threshold}{'%' if relative else ' people'}"
    return flag


def high_density_areas(pop_data: xr.DataArray, threshold: float = 1000.0) -> xr.DataArray:
    """
    Create a binary mask of pixels exceeding a density threshold.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array
    threshold : float, optional
        Density threshold in people/km², by default 1000.0
        
    Returns
    -------
    xr.DataArray
        Binary mask (1 for high density, 0 for low density)
    """
    # Convert to density first
    density = population_density(pop_data)
    
    # Create binary mask
    mask = xr.where(density >= threshold, 1, 0)
    
    mask.attrs['units'] = 'binary'
    mask.attrs['long_name'] = 'High density areas'
    mask.attrs['threshold'] = f"{threshold} people/km²"
    return mask


def inhabited_flag(pop_data: xr.DataArray, threshold: float = 1.0) -> xr.DataArray:
    """
    Create a binary classification of inhabited vs uninhabited areas.
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array
    threshold : float, optional
        Minimum population to consider a cell inhabited, by default 1.0
        
    Returns
    -------
    xr.DataArray
        Binary flag (1 for inhabited, 0 for uninhabited)
    """
    flag = xr.where(pop_data >= threshold, 1, 0)
    
    flag.attrs['units'] = 'binary'
    flag.attrs['long_name'] = 'Inhabited areas'
    flag.attrs['threshold'] = f"{threshold} people"
    return flag

def urban_fringe(pop_data: xr.DataArray, density_threshold: float = 300.0, 
                buffer_size: int = 1) -> xr.DataArray:
    """
    Identify pixels at the boundary of urban areas (urban fringe).
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array
    density_threshold : float, optional
        Density threshold to define urban areas, by default 300.0 people/km²
    buffer_size : int, optional
        Size of the buffer around urban areas to consider as fringe, by default 1 pixel
        
    Returns
    -------
    xr.DataArray
        Binary mask of urban fringe areas (1 for fringe, 0 otherwise)
    """
    # Create urban mask based on density threshold
    density = population_density(pop_data)
    urban_mask = (density >= density_threshold).values
    
    # Handle multidimensional arrays by operating on the 2D spatial dimensions only
    original_shape = urban_mask.shape
    spatial_dims = len(original_shape)
    
    # If we have more than 2 dimensions (e.g., time, lat, lon), we need to process each 2D slice
    if spatial_dims > 2:
        # Reshape to handle each 2D slice separately
        # Assuming the last two dimensions are spatial (e.g., lat, lon)
        n_slices = np.prod(original_shape[:-2])
        reshaped = urban_mask.reshape(n_slices, original_shape[-2], original_shape[-1])
        
        # Process each 2D slice
        dilated_slices = []
        for i in range(n_slices):
            # Create a flat structuring element for 2D
            selem = morphology.disk(buffer_size)
            # Dilate the 2D slice
            dilated_slice = morphology.binary_dilation(reshaped[i], selem)
            # Calculate fringe
            fringe_slice = dilated_slice & ~reshaped[i]
            dilated_slices.append(fringe_slice)
        
        # Combine results and reshape back to original dimensions
        fringe = np.array(dilated_slices).reshape(original_shape).astype(int)
    else:
        # For 2D data, process directly
        selem = morphology.disk(buffer_size)
        dilated = morphology.binary_dilation(urban_mask, selem)
        fringe = (dilated & ~urban_mask).astype(int)
    
    # Convert back to xarray with same coordinates
    result = xr.DataArray(
        fringe,
        coords=pop_data.coords,
        dims=pop_data.dims,
        attrs={
            'units': 'binary',
            'long_name': 'Urban fringe',
            'density_threshold': f"{density_threshold} people/km²",
            'buffer_size': f"{buffer_size} pixels"
        }
    )
    
    return result


def monocentric_polycentric_pattern(pop_data: xr.DataArray, 
                                  density_threshold: float = 300.0,
                                  search_radius: int = 50) -> xr.DataArray:
    """
    Classify areas based on spatial distribution pattern (monocentric vs. polycentric).
    
    Parameters
    ----------
    pop_data : xr.DataArray
        Population data array
    density_threshold : float, optional
        Density threshold to define urban centers, by default 300.0 people/km²
    search_radius : int, optional
        Search radius for identifying centers, by default 50 pixels
        
    Returns
    -------
    xr.DataArray
        Classification (0=rural, 1=monocentric, 2=polycentric)
    """
    # Calculate population density
    density = population_density(pop_data).values
    
    # Identify urban centers (high density areas)
    urban_centers = density >= density_threshold
    
    # Label urban centers
    labeled_centers = measure.label(urban_centers)
    num_centers = labeled_centers.max()
    
    # Calculate distance transform for each center
    distance_maps = []
    for i in range(1, num_centers + 1):
        center_mask = labeled_centers == i
        distance_maps.append(ndimage.distance_transform_edt(~center_mask))
    
    # If no centers found, return all rural
    if not distance_maps:
        result = xr.zeros_like(pop_data)
        result.attrs['units'] = 'pattern_class'
        result.attrs['long_name'] = 'Urban pattern classification'
        result.attrs['values'] = '0=rural, 1=monocentric, 2=polycentric'
        return result
    
    # Stack distance maps and find closest center for each pixel
    distance_stack = np.stack(distance_maps, axis=0)
    closest_center = np.argmin(distance_stack, axis=0) + 1
    min_distance = np.min(distance_stack, axis=0)
    
    # Classify based on distance and number of centers
    # 0 = rural (beyond search radius of any center)
    # 1 = monocentric (within radius of only one significant center)
    # 2 = polycentric (influenced by multiple centers)
    
    # Count number of centers within search radius for each pixel
    centers_in_radius = np.sum(distance_stack < search_radius, axis=0)
    
    # Create classification
    classification = np.zeros_like(min_distance, dtype=int)
    classification[min_distance < search_radius] = 1  # monocentric by default if within radius
    classification[centers_in_radius > 1] = 2  # polycentric if multiple centers in radius
    
    # Convert back to xarray with same coordinates
    result = xr.DataArray(
        classification,
        coords=pop_data.coords,
        dims=pop_data.dims,
        attrs={
            'units': 'pattern_class',
            'long_name': 'Urban pattern classification',
            'values': '0=rural, 1=monocentric, 2=polycentric',
            'density_threshold': f"{density_threshold} people/km²",
            'search_radius': f"{search_radius} pixels"
        }
    )
    
    return result