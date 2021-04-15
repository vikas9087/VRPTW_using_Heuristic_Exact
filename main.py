import nearest_neighbor as nn
import create_model as cm
import data_model as dm

model = cm.BuildModel(day='Mon')
nearest_neighbor = nn.NearestNeighbor(model.distances, model.orders, model.customers, model.travel_time, model.unload_time)
nearest_neighbor.solve()
print(nearest_neighbor.routes)
print(nearest_neighbor.route_distances)
print(nearest_neighbor.vehicle_arrival_time)
