import ghslpy

region = ghslpy.utils.find_region(
    ["Ciudad Autónoma de Buenos Aires"]
)

# region = ghslpy.utils.wkt_as_gdf(
#     "POLYGON((-59.9 -33.83, -57.28 -33.83, -57.28 -35.25, -59.9 -35.25, -59.9 -33.83))"
#     )

epochs = [1990, 2025]
data = ghslpy.download(
    products=["GHS-BUILT-S", "GHS-POP"],
    epoch=epochs,
    resolution="100m",
    region=region,
)

from ghslpy.metrics.pixelwise import built_up_growth_rate, population_growth_rate, decoupling_index
pop_growth = population_growth_rate(data['GHS_POP'])
built_growth = built_up_growth_rate(data['GHS_BUILT'])
decoupling = decoupling_index(data['GHS_BUILT'], data['GHS_POP'])


ghslpy.vectorize(pop_growth.to_dataset(name="pop_growth"))
ghslpy.vectorize(built_growth.to_dataset(name="built_growth"))
ghslpy.vectorize(decoupling.to_dataset(name="decoupling"))
# from ghslpy.metrics.pixelwise import population_density
# clusters = population_density(data["GHS_POP"].isel(time=0))
# vector = ghslpy.vectorize(clusters.to_dataset(name='population_density'))

# print(vector)
