import pandas as pd
from geopy.distance import great_circle
import matplotlib.pyplot as plt
import plotly.express as px

__orders = pd.read_csv('orders.csv', index_col='ORDERID', skiprows=[1], dtype={'CUBE': int})
__locations = pd.read_csv('location.csv')

# All the times are based on minutes
MAX_DRIVING_HOURS: float = 11*60
MAX_DRIVER_SHIFT_HOURS: float = 14*60
BREAK_HOURS: float = 10*60
UNLOAD_TIME: float = 0.50*60
TIME_START_WINDOW = 8*60
TIME_END_WINDOW = 18*60

# Vehicle speed in mph
VEHICLE_SPEED: int = 40
# Unloading rate is in minute/cubic feet
UNLOAD_RATE: float = 0.030
# Vehicle capacity in cubic feet
VEHICLE_CAPACITY: int = 3600

DEPOT = {'ZIPID': 20, 'ZIP': 1887, 'latitude': 42.54555556, 'longitude': -71.17555556}
days = __orders['DayOfWeek'].unique()


def __distance_dict(zip_ids: list[int]):
    distances = {}
    location_coordinates = __locations[__locations['ZIP'].isin(zip_ids)].reset_index(drop=True)
    for zip_a in location_coordinates['ZIP']:
        for zip_b in location_coordinates['ZIP']:
            if zip_a != zip_b:
                source = (location_coordinates[location_coordinates['ZIP'] == zip_a]['X'].values[0],
                          location_coordinates[location_coordinates['ZIP'] == zip_a]['Y'].values[0])
                destination = (location_coordinates[location_coordinates['ZIP'] == zip_b]['X'].values[0],
                               location_coordinates[location_coordinates['ZIP'] == zip_b]['Y'].values[0])
                distance = round(great_circle(source, destination).miles, ndigits=0)
                distances[(zip_a, zip_b)] = distances[(zip_b, zip_a)] = distance
    return distances


def get_day_orders_distances(day: str):
    columns = ['TOZIP', 'CUBE']
    sliced_orders_data = __orders[__orders['DayOfWeek'] == day]
    zip_ids = sliced_orders_data['TOZIP'].values.tolist()

    zip_ids.append(DEPOT['ZIP'])
    res = {'orders': pd.Series(sliced_orders_data[columns[1]].values, index=sliced_orders_data[columns[0]]).to_dict(),
           'distances': __distance_dict(zip_ids)}
    res['orders'][DEPOT['ZIP']] = 0
    return res


def get_unloading_times(orders: dict):
    unload_time = {}
    for key in orders:
        unload_time[key] = max(UNLOAD_TIME, round(orders[key] * UNLOAD_RATE, ndigits=2))

    return unload_time


def get_travel_times(distances: dict):
    travel_time = {}
    for key in distances:
        travel_time[key] = round(distances[key]*60/VEHICLE_SPEED, ndigits=2)

    return travel_time
