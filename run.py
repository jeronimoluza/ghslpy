import ghslpy
from shapely import wkt

region = wkt.loads(
  "POLYGON((-58.716652 -34.416379, -58.188198 -34.416379, -58.188198 -34.787519, -58.716652 -34.787519, -58.716652 -34.416379))"
)

data = ghslpy.download(
  product="GHS-BUILT-S",
  epoch=2020,
  resolution="100m",
  classification="RES+NRES",
  region=region # if not region, means that global=True
)

vector = ghslpy.vectorize(data, "built")