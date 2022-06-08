
import numpy as np
import sys
import googlemaps
import statistics
import webbrowser
from datetime import datetime
from itertools import permutations


class Location:

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address

    def __hash__(self) -> int:
        return hash(str(self.address))

    def __eq__(self, other) -> bool:
        return isinstance(other, Location) and self.address == other.address

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return self.__str__()


class DeliveryLocation(Location):

    def __init__(self, name: str, address: str, packages: int | str = 0):
        super().__init__(name, address)
        self.packages = int(packages)


class DistributionCenter(Location):

    def __init__(self, name: str, address: str, inventory: int | str = 0):
        super().__init__(name, address)
        self.inventory = int(inventory)


class Trip:

    def __init__(self, origin: Location, destination: Location, travelTime: int | str):

        if not isinstance(origin, Location) or not isinstance(destination, Location):
            raise TypeError('The first two args passed to Trip.__init__() must be Location objects.')

        if origin == destination:
            raise ValueError('Attempted to initialize an Trip object with customers having the same address.')

        try:
            self.travelTime = int(travelTime)
        except Exception as err:
            raise TypeError(f'travelTime arg passed to Trip.__init__() must be a string in integer format or an integer object, not a {type(travelTime)}.')

        self.origin = origin
        self.destination = destination

    def __hash__(self) -> int:
        return hash(str(self.origin) + str(self.destination))

    def __eq__(self, other) -> bool:
        return isinstance(other, Trip) and self.origin == other.origin and self.destination == other.destination and self.travelTime == other.travelTime

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        return self.__str__()


class TravelMatrix:
    '''An implementation of a directed, weighed adjacency matrix.'''

    def __init__(self, trips: set[Trip]):

        if not isinstance(trips, set):
            raise TypeError('trips must be a set type.')

        # initialize a set of all the locations
        locations = set()
        for t in trips:
            if not isinstance(t, Trip):
                raise TypeError('Expected a Trip object')
            locations.add(t.origin)
            locations.add(t.destination)

        # initialize the arrays of starting points and destinations
        self.__locations = np.array(list(locations), dtype=Location)

        # initialize the adjacency matrix of travel times with zeros
        self.__matrix = np.zeros((self.__locations.size, self.__locations.size), dtype=int)

        # initialize a dict to map customers to their array index
        index = {self.__locations[i]: i for i in range(self.__locations.size)}

        for t in trips:
            x = index[t.origin]
            y = index[t.destination]
            self.__matrix[x][y] = t.travelTime

    def location(self, index: int) -> Location:
        return self.__locations[index]

    def location_count(self) -> int:
        return self.__locations.size

    def travel_time(self, origin: int, destination: int) -> int:
        return self.__matrix[origin][destination]

    # Calculates the total travel time of a tour in seconds.
    def total_travel_time(self, locations: list[int]) -> int:
        return sum(self.__matrix[locations[x]][locations[x + 1]] for x in range(len(locations) - 1))

    # Calculates the sum of all packages to be delivered on a tour.
    def total_packages(self, locations: list[int]) -> int:
        return sum(self.__locations[x].packages for x in locations if hasattr(self.__locations[x], 'packages'))

    # This is a convenience function used to determine if a vertex meets the criteria to
    # be passed to self.__generate_tours(). Returns true if we can deliver to the customer.
    def is_deliverable(self, location: int, min_packages: int = 0, max_packages: int = sys.maxsize) -> bool:
        if min_packages > max_packages:
            raise ValueError('min_packages must be less than max_packages')
        loc = self.__locations[location]
        return True if isinstance(loc, DeliveryLocation) and loc.packages >= min_packages and loc.packages <= max_packages else False

    def delivery_locations(self, min_packages: int = 0, max_packages: int = sys.maxsize) -> list[int]:
        return [i for i in range(self.location_count()) if self.is_deliverable(i, min_packages, max_packages)]

    def has_inventory(self, location: int, min_inventory: int = 0, max_inventory: int = sys.maxsize) -> bool:
        if min_inventory > max_inventory:
            raise ValueError('min_inventory must be less than max_inventory')
        loc = self.__locations[location]
        return True if isinstance(loc, DistributionCenter) and loc.inventory >= min_inventory and loc.inventory <= max_inventory else False

    def distribution_centers(self, min_inventory: int = 0, max_inventory: int = sys.maxsize) -> list[int]:
        return [i for i in range(self.location_count()) if self.has_inventory(i, min_inventory, max_inventory)]

    def nearest_neighbor(self, origin: int, destinations: list[int] = []) -> tuple[int, int] | None:
        min_travelTime = sys.maxsize
        nearest = None
        for dst in destinations:
            if dst != origin:
                travelTime = self.travel_time(origin, dst)
                if travelTime < min_travelTime:
                    min_travelTime = travelTime
                    nearest = dst
        return None if nearest is None else (nearest, min_travelTime)

    def farthest_outlier(self, destinations: list[int] = []) -> int:
        outlier = -1
        max_avg = -1
        for y in destinations:
            avg = statistics.mean(self.travel_time(x, y) for x in destinations if x != y)
            if avg > max_avg:
                outlier = y
                max_avg = avg
        return outlier


class TreeBuilder:

    class Node:
        '''A basic tree note object containing a value and an array of children.'''
        def __init__(self, value: object):
            self.value = value
            self.children = []

        def preorder_traversal(self):
            '''A generator that yields each node of the tree in preorder.'''
            stack = [self]
            while len(stack):
                node = stack.pop()
                stack.extend(node.children)
                yield node

    @staticmethod
    def minimum_spanning_tree(matrix: TravelMatrix, root_location: int, undelivered_locations: set[int], max_payload: int = sys.maxsize) -> Node:
        '''
        Builds a minimum spanning tree consisting of vertexes (Locations) in the graph (TravelMatrix). This method is used by a RoutePlanner
        object when calculating delivery routes. 

        Parameters
        ----------
        matrix: TravelMatrix
            An adjacency matrix in the form of a TravelMatrix object.

        root_location: int
            The index of a location (vertex) in the TravelMatrix object that serves as the root, or staring point, for building the tree.
            root_location must be a valid index in matrix.
        
        undelivered_locations: set[int]
            A list of indexes of locations (vertexes) in the TravelMatrix object, which are all candidates for inclusion in the tree. This is
            is typically a subset of all locations in the TravelMatrix object.
        
        max_payload: int = sys.maxsize
            The maximum payload (or capacity) of the delivery vehicle used to delivery packages. This method will stop building the tree when
            the sum of all packages in the tree exceeds this value.
        
        Returns
        -------
        TreeBuilder.Node
            The root node of the minimum spanning tree.
        '''
        # create the root node
        root_node = TreeBuilder.Node(root_location)

        # make a list of all locations that we haven't delivered to yet
        remaining_locations = [i for i in undelivered_locations if i != root_location]

        # initiate the number of packages with that of the root node
        num_packages = matrix.location(root_location).packages if isinstance(matrix.location(root_location), DeliveryLocation) else 0

        # keep going until no vertices remain
        while len(remaining_locations) > 0:

            nearest_neighbor = (None, None, sys.maxsize)

            # traverse the tree in preorder
            for node in root_node.preorder_traversal():

                destination, travel_time = matrix.nearest_neighbor(node.value, remaining_locations)
                if travel_time < nearest_neighbor[2]:
                    nearest_neighbor = (node, destination, travel_time)

            # accumulate the number of packages
            num_packages += matrix.location(nearest_neighbor[1]).packages if isinstance(matrix.location(nearest_neighbor[1]), DeliveryLocation) else 0

            # if we've delivered too many packages, then return to the caller
            if num_packages > max_payload:
                break

            # otherwise add nearest_neighbor to the tree
            nearest_neighbor[0].children.append(TreeBuilder.Node(nearest_neighbor[1]))

            # and remove the best edge from the list of remaining vertices
            remaining_locations.remove(nearest_neighbor[1])

        # return the root of the minimum spanning tree
        return root_node


# See the Google Directions API Developer Guide located at
#    https://developers.google.com/maps/documentation/directions/start
#
# According to the develper guide:
#    "legs[] contains an array which contains information about a leg
#    of the route, between two locations within the given route.
#    A separate leg will be present for each waypoint or destination
#    specified. (A route with no waypoints will contain exactly one
#    leg within the legs array.) Each leg consists of a series of steps."
#
# Our data should not contain any waypoints. Therefore, each file
# should only contain one leg.
class GoogleMapsTripSetBuilder:

    @staticmethod
    def build(google_api_key: str, customer_orders: set[DeliveryLocation], distribution_centers: set[DistributionCenter]) -> set[Trip]:

        if not isinstance(google_api_key, str):
            raise TypeError('google_api_key must be a string type.')

        if not isinstance(customer_orders, set):
            raise TypeError('customer_orders must be a set[DeliveryLocation] type.')

        if not isinstance(distribution_centers, set):
            raise TypeError('distributionCenter must be a DistributionCenter type.')

        # establish a few needed variables/objects
        locations = set()
        for c in customer_orders:
            if not isinstance(c, DeliveryLocation):
                raise ValueError('customer_orders contains an object that is not of type DeliveryLocation')
            locations.add(c)

        for d in distribution_centers:
            if not isinstance(d, DistributionCenter):
                raise ValueError('distribution_centers contains an object that is not of type DistributionCenter')
            locations.add(d)

        length = len(locations)
        num_trips = (length * length) - length
        #counter = 0
        trips = set()

        # ask the user to be patient because the download process takes time.
        print("Querying google maps for directions between each of", length, "locations.", file=sys.stderr)
        print("Please be patient. There are", num_trips, "combinations to download.", file=sys.stderr)

        # get our google maps client
        gmaps = googlemaps.Client(key=google_api_key)

        # iterate over every pair of customer addresses (no loops allowed!) and get the data from google maps
        # for src, dst in ((s, d) for s in locations for d in locations if s != d):
        prev_percent = 0.0
        for n, trip in enumerate(((s, d) for s in locations for d in locations if s != d), 1):
            directions = gmaps.directions(trip[0].address, trip[1].address, mode='driving', departure_time=datetime.now())
            travel_time = 0
            legs = directions[0]['legs']
            for leg in legs:
                travel_time += int(leg['duration']['value'])
            #travel_time = sum(int(leg['duration']['value']) for leg in directions[0]['legs'])
            trips.add(Trip(trip[0], trip[1], travel_time))
            #counter += 1
            curr_percent = round(n / num_trips * 100, 1)
            if curr_percent > prev_percent:
                print('\rDownloading directions from google.com/maps... ', curr_percent, '% complete', end='', file=sys.stderr)
            prev_percent = curr_percent

        print('', file=sys.stderr)

        return trips


class RoutePlanner(TravelMatrix):
    '''
    '''

    def __init__(self, trips: set[Trip]):
        super().__init__(trips)
    
    def brute_force_optimize(self, tour: list[int], distribution_center: int) -> list[int]:
        best_tour = [x for x in tour]
        best_tour.insert(0, distribution_center)
        best_tour.append(distribution_center)
        for combo in permutations(tour, len(tour)):
            temp = [x for x in combo]
            temp.insert(0, distribution_center)
            temp.append(distribution_center)
            if self.total_travel_time(temp) < self.total_travel_time(best_tour):
                best_tour = temp
        return best_tour
    
    def triangle_optimize(self, tour: list[int], distribution_center: int) -> list[int]:
        best_tour = [x for x in tour]
        best_tour.insert(0, distribution_center)
        best_tour.append(distribution_center)
        # iterate over each adjacent triplet in the tour
        # if we go past the second to get the the third, then swap them.
        for i in range(len(best_tour) - 3):
            # get the length of all three sides of the "triangle"
            a, b, c = best_tour[i:i + 3]
            x = self.travel_time(a, b)
            y = self.travel_time(b, c)
            z = self.travel_time(a, c)
            # if z is not the hypotenuse, then swap b and c
            if z != max(x, y, z):
                best_tour[i + 1], best_tour[i + 2] = best_tour[i + 2], best_tour[i + 1]
        return best_tour
    
    def routes_starting_at_each(self, distribution_center: int, delivery_locations: set[int], max_payload: int = sys.maxsize) -> list[list[int]]:
        '''
        Returns a list of delivery routes containing one route with each location in
        undelivered_locations as the starting point. Each route is limited by max_payload.

        Parameters
        ----------
        distribution_center: int
            The index of the distribution center in the travel matrix.

        delivery_locations: set[int]
            A set containing the indexes of the the delivery locations to include the delivery routes.

        max_payload: int = sys.maxsize
            The maximum payload of the delivery truck.
        
        Returns
        -------
        list[list[int]]
            A list of delivery routes, each of which is a list of indexes in the travel matrix.
        '''

        if not isinstance(distribution_center, int) or not isinstance(self.location(distribution_center), DistributionCenter):
            raise ValueError('distribution_center must be an index of a DistributionCenter object in the adjacency matrix')

        routes = []

        # iterate thru all the indexes in undelivered
        for location in delivery_locations:

            # create a minimmum spanning tree
            rootNode = TreeBuilder.minimum_spanning_tree(self, location, delivery_locations, max_payload)

            # build a tour by iterating over the minimum spanning tree in preorder
            tour = [node.value for node in rootNode.preorder_traversal()]

            # try to improve the tour before yielding it to the caller
            if len(tour) < 9:
                tour = self.brute_force_optimize(tour, distribution_center)
            elif len(tour) >= 2:
                tour = self.triangle_optimize(tour, distribution_center)

            routes.append(tour)

        routes.sort(key=lambda t: self.total_travel_time(t) / self.total_packages(t))
        
        return routes
    
    def single_truck(self, distribution_center: int, min_packages: int, max_packages: int, max_payload: int, avg_unload_time: int = 0):

        # create a list of delivery locations
        undelivered = set(self.delivery_locations(min_packages, max_packages))

        while len(undelivered):

            #tours = [t for t in self.routes_starting_at_each(distribution_center, undelivered, max_payload)]
            #tours = self.routes_starting_at_each(distribution_center, undelivered, max_payload)

            # sort the set of tours in ascending order by the average delivery time per package
            for tour in self.routes_starting_at_each(distribution_center, undelivered, max_payload): #sorted(tours, key=lambda t: self.matrix.total_travel_time(t) / self.matrix.total_packages(t)):
                s = set(tour[1:len(tour) - 1])
                if undelivered.issuperset(s):
                    undelivered = undelivered.difference(s)
                    totalPackages = self.total_packages(tour)
                    yield {
                        'Travel Time': self.total_travel_time(tour),
                        'Total Bags': totalPackages,
                        'Delivery Time': totalPackages * avg_unload_time,
                        'Customers': [self.location(i) for i in tour]
                    }
    
    def large_and_small_truck(self, distribution_center: int, large_max_payload: int, small_max_payload: int, avg_unload_time: int = 0) -> list[list[int]]:
        routes = []
        undelivered = set(self.delivery_locations())
        while len(undelivered):
            tours = self.routes_starting_at_each(distribution_center, undelivered, large_max_payload)
            tour = tours[0]
            # remove from the list
            tours = self.routes_starting_at_each(distribution_center, undelivered, small_max_payload)
            tour = tours[-1]


def open_route_in_browser(route: list[Location]) -> None:
    '''Opens a new tab in a web browser and displays the delivery route in Google Maps.'''
    url = 'https://www.google.com/maps/dir/'
    for location in route:
        url += location.address.replace(' ', '+') + '/'
    webbrowser.open(url)
