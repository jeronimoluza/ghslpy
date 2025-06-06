import ghslpy
from shapely import wkt

region = wkt.loads(
  "POLYGON((-60.049 -34.0998, -57.88 -34.0998, -57.88 -35.1815, -60.049 -35.1815, -60.049 -34.0998))"
)

data = ghslpy.download(
  product="GHS-BUILT-S",
  epoch=2020,
  resolution="100m",
  classification="RES+NRES",
  region=region # if not region, means that global=True
)

vector = ghslpy.vectorize(data, "built")