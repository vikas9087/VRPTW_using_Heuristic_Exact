import gurobipy as gp
from gurobipy import GRB
import data_model as dm
import math as math


class BuildModel():

    def __init__(self, day: str):
        self.model = gp.Model('VRPTW')
        __res_dist_orders = dm.get_day_orders_distances(day)
        self.distances: dict = __res_dist_orders['distances']
        self.orders: dict = __res_dist_orders['orders']
        self.travel_time = dm.get_travel_times(self.distances)
        self.unload_time = dm.get_unloading_times(self.orders)
        self.__get_vehicles()
        self.indexes = [(v, n) for v in self.vehicles for n in self.distances.keys()]
        self.customers = list(self.orders.keys())
        self.__create_select_index()

    def build(self):
        self.__create_variables()
        self.__create_objective()
        self.__create_constraints()
        self.model.setParam('MIPGap', 0.10)
        self.model.update()


    def __create_variables(self):
        self.visit_var = self.model.addVars(self.indexes, vtype=GRB.BINARY, name='ArcVisitVar')
        self.time_var = self.model.addVars(self.customers, lb=dm.TIME_START_WINDOW, ub=dm.TIME_END_WINDOW,
                                           vtype=GRB.CONTINUOUS, name='CustomerVisitTime')

    def __create_objective(self):
        self.model.setObjective(gp.quicksum(self.distances[key[1]] * self.visit_var[key] for key in self.indexes),
                                sense=GRB.MINIMIZE)

    def __create_constraints(self):
        self.model.addConstrs(
            gp.quicksum(self.visit_var[(v, k)] for k in self.indexes_depot_start) == 1 for v in self.vehicles)
        self.model.addConstrs(
            gp.quicksum(self.visit_var[(v, k)] for k in self.indexes_depot_end) == 1 for v in self.vehicles)
        self.model.addConstrs(
            gp.quicksum(self.orders[k[0]]*self.visit_var[(v,k)] for k in self.distances) <= dm.VEHICLE_CAPACITY for v in self.vehicles)
        for v in self.vehicles:
            for j in self.customers:
                self.model.addConstr(
                    gp.quicksum(self.visit_var[(v,(i,j))]*(self.time_var[i]+self.unload_time[i]+self.travel_time[(i,j)])
                                for i in self.customers if i != j) <= self.time_var[j])
                self.model.addConstr(
                    gp.quicksum(self.visit_var[(v,(i,j))] - self.visit_var[(v,(j, i))] for i in self.customers if i != j) == 0)
        pass

    def __create_select_index(self):
        depot = dm.DEPOT['ZIP']
        self.indexes_depot_start = []
        self.indexes_depot_end = []
        self.index_customer_pairs = []

        for key in self.distances.keys():
            if key[0] == depot:
                self.indexes_depot_start.append(key)
            if key[1] == depot:
                self.indexes_depot_end.append(key)
            if depot not in key:
                self.index_customer_pairs.append(key)

    def __get_vehicles(self):
        total_orders = sum(self.orders.values())
        min_vehicles = math.ceil((total_orders / dm.VEHICLE_CAPACITY))
        self.vehicles = list(range(math.ceil((min_vehicles * 1.5))))

