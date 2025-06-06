import ghslpy
from shapely import wkt

region = wkt.loads(
  "POLYGON((-59.1168 -34.2511, -57.88 -34.2511, -57.88 -35.0306, -59.1168 -35.0306, -59.1168 -34.2511))"
)

data = ghslpy.download(
  product="GHS-POP",
  epoch=2020,
  resolution="100m",
#   classification="AGBH",
  region=region # if not region, means that global=True
)

vector = ghslpy.vectorize(data, "population")
vector.to_csv('test.csv')