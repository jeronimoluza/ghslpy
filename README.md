# ghslpy
A Python toolkit for downloading and processing data from the Global Human Settlement Layer (GHSL).

## Getting Started

GHSLPy allows you to download products from the [Global Human Settlements Layer site](https://human-settlement.emergency.copernicus.eu/download.php?):

```python
import ghslpy
from shapely import wkt


region = wkt.loads(
  "POLYGON((-58.716652 -34.416379, -58.188198 -34.416379, -58.188198 -34.787519, -58.716652 -34.787519, -58.716652 -34.416379))"
)

data = ghslpy.download(
  product="GHS-BUILT-S",
  epoch=2020,
  resolution="100m",
  region=region
)
```

The `data` variable is `xarray.Dataset`.

```python
print(data)
```

