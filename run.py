import ghslpy
from shapely import wkt

region = wkt.loads(
    # "POLYGON((-59.1168 -34.2511, -57.88 -34.2511, -57.88 -35.0306, -59.1168 -35.0306, -59.1168 -34.2511))"
    "POLYGON((-58.9959 -34.247, -58.7996 -34.247, -58.7996 -34.4268, -58.9959 -34.4268, -58.9959 -34.247))"
)

epochs = [2015, 2020]
data = ghslpy.download(
    product="GHS-BUILT-S",
    epoch=epochs,
    resolution="100m",
    #   classification="AGBH",
    region=region,  # if not region, means that global=True
)

vector = ghslpy.vectorize(data)
vector.to_csv("test.csv")
