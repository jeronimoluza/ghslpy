import ghslpy

region = ghslpy.utils.find_region(
    ["Ciudad Autónoma de Buenos Aires"]
)

# region = ghslpy.utils.wkt_as_gdf(
#     "POLYGON((-59.9 -33.83, -57.28 -33.83, -57.28 -35.25, -59.9 -35.25, -59.9 -33.83))"
#     )

epochs = 2025
data = ghslpy.download(
    products=["GHS-BUILT-S", "GHS-POP"],
    epoch=epochs,
    resolution="100m",
    region=region,
)

from ghslpy.metrics.pixelwise import built_up_area_per_capita
pop_per_built = built_up_area_per_capita(data["GHS_BUILT"], data["GHS_POP"])

ghslpy.vectorize(pop_per_built.to_dataset(name="built_up_area_per_capita")).to_csv("test.csv")

# from ghslpy.metrics.pixelwise import population_density
# clusters = population_density(data["GHS_POP"].isel(time=0))
# vector = ghslpy.vectorize(clusters.to_dataset(name='population_density'))

# print(vector)
