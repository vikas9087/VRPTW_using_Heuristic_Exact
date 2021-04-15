import data_model as dm
import math as math


class NearestNeighbor():

    def __init__(self, distances: dict, orders: dict, customers: list[int], travel_time: dict, service_time: dict):
        self.vehicle_arrival_time = {}
        self.route_distances = {}
        self.distances = distances
        self.orders = orders
        if dm.DEPOT['ZIP'] in self.orders:
            del self.orders[dm.DEPOT['ZIP']]
        self.customers = customers
        if dm.DEPOT['ZIP'] in self.customers:
            self.customers.remove(dm.DEPOT['ZIP'])
        self.total_distance = 0
        self.travel_time = travel_time
        self.service_time = service_time

    def solve(self):
        self.routes = self.__neighbor_search()
        self.__polish_solution()

    def __get_neighbor(self, node: int, node_exclude: list, nodes_select: list):
        """
        Returns the next nearest neighbor to the current node. This checks if some neighbor is not to be included
        :param node: node to which next nearest neighbor is to be checked
        :param node_exclude: any node if not to be included as neighbor
        :return: returns the next nearest node or None
        """
        neighbor: int = None
        best_distance = math.inf
        for key in self.distances:
            if key[1] != dm.DEPOT['ZIP'] and key[1] not in nodes_select:
                if node_exclude and key[1] not in node_exclude:
                    if key[0] == node and self.distances[key] < best_distance:
                        best_distance = self.distances[key]
                        neighbor = key[1]
                elif key[0] == node and self.distances[key] < best_distance:
                    best_distance = self.distances[key]
                    neighbor = key[1]

        return neighbor

    def __neighbor_search(self):
        routes = []
        iteration = 0
        nodes_selected = []

        while self.customers:
            flag = True
            sub_route = []
            start_node = dm.DEPOT['ZIP']
            capacity_remaining = dm.VEHICLE_CAPACITY
            node_exclude = []
            arrival_time = dm.TIME_START_WINDOW
            sub_iteration = 0
            while flag > 0:
                neighbor = self.__get_neighbor(start_node, node_exclude, nodes_selected)
                if neighbor:
                    demand = self.orders[neighbor]
                    unload_time = self.service_time[neighbor]
                    if demand > dm.VEHICLE_CAPACITY:
                        raise Exception('The demand of customer with ZIP ID {} exceeds capacity'.format(neighbor))
                    elif demand > capacity_remaining:
                        node_exclude.append(neighbor)
                        continue
                    else:
                        capacity_remaining -= demand
                        end_node = neighbor
                    if arrival_time + self.travel_time[(start_node, end_node)] + unload_time > dm.TIME_END_WINDOW:
                        end_node = dm.DEPOT['ZIP']
                        sub_route.append((start_node, end_node))
                        flag = False
                    elif capacity_remaining <= 0 or (0 < capacity_remaining < demand):
                        start_node = end_node
                        nodes_selected.append(end_node)
                        self.customers.remove(end_node)
                        end_node = dm.DEPOT['ZIP']
                        sub_route.append((start_node, end_node))
                        flag = False
                    else:
                        self.customers.remove(end_node)
                        nodes_selected.append(end_node)
                        self.vehicle_arrival_time[neighbor] = arrival_time
                        node_pair = (start_node, end_node)
                        arrival_time += self.travel_time[node_pair] + unload_time
                        start_node = end_node
                        sub_route.append(node_pair)
                    sub_iteration += 1
                elif sub_route:
                    break
            iteration += 1
            routes.append(sub_route)

        return routes

    def __polish_solution(self):
        for i in range(len(self.routes)):
            route_distance = 0
            if len(self.routes[i]) == 1:
                start = self.routes[i][0][0]
                end = self.routes[i][0][1]
                self.routes[i].append((end, start))
            for key in self.routes[i]:
                route_distance += self.distances[key]
            self.route_distances['Route_{}'.format(i)] = route_distance