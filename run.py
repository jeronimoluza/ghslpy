import ghslpy

region = ghslpy.utils.find_region(
    ["Ciudad Autónoma de Buenos Aires"]
)

epochs = [2020, 2025]
data = ghslpy.download(
    products=["GHS-POP", "GHS-BUILT-S"],
    epoch=epochs,
    resolution="1000m",
    region=region,
)
# vector = ghslpy.vectorize(data)
# vector.to_csv("test.csv")

