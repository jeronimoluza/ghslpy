import ghslpy

region = ghslpy.utils.find_region(
    ["Provincia de Buenos Aires", "Ciudad Autónoma de Buenos Aires"]
)

epochs = [2025]
data = ghslpy.download(
    product="GHS-SMOD",
    epoch=epochs,
    resolution="1000m",
    region=region,  # if not region, means that global=True
)
vector = ghslpy.vectorize(data)
vector.to_csv("test.csv")

