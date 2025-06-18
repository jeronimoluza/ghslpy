import ghslpy
from shapely import wkt

region = wkt.loads(
    # "POLYGON((-59.1168 -34.2511, -57.88 -34.2511, -57.88 -35.0306, -59.1168 -35.0306, -59.1168 -34.2511))"
    # "POLYGON((-58.9959 -34.247, -58.7996 -34.247, -58.7996 -34.4268, -58.9959 -34.4268, -58.9959 -34.247))"
    "POLYGON((-58.875014 -34.375579, -58.678708 -34.375579, -58.678708 -34.555167, -58.875014 -34.555167, -58.875014 -34.375579))"
)

epochs = [2018]
data = ghslpy.download(
    product="GHS-BUILT-C",
    epoch=epochs,
    resolution="10m",
    region=region,  # if not region, means that global=True
)
vector = ghslpy.vectorize(data)
vector.to_csv("test.csv")
