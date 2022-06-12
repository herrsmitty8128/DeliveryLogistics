
import DeliveryLogistics
import csv
import json

avg_unload_secs = 11
big_truck_payload = 330
customer_file = 'data_files/2022_orders.csv'
api_key_file = 'data_files/google_api_key.json'
distributionCenters = set([DeliveryLogistics.DistributionCenter('Dogwood Elementary School', '12300 Glade Dr, Reston, VA 20191, USA')])
    

if __name__ == "__main__":

    # load our list of customers
    customer_orders = set()
    with open(customer_file,'rt',newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer_orders.add(DeliveryLogistics.DeliveryLocation('',row['address'],row['bags']))
    
    # load the google API key
    f = open(api_key_file,)
    data = json.load(f)
    google_api_key = data['google api key']
    f.close()

    # get the data from google maps 
    #trips = DeliveryLogistics.GoogleMapsTripSetBuilder.build(google_api_key, customer_orders, distributionCenters)
    #DeliveryLogistics.write_trips_to_json(trips, 'trips.json')

    trips = DeliveryLogistics.read_trips_from_json('trips.json')
    
    # instantiate a route planning object
    planner = DeliveryLogistics.RoutePlanner(trips)

    # get the distribution center
    distribution_ctr = planner.distribution_centers().pop()

    # calculate the delivery routes
    routes = planner.single_payload_and_dist(distribution_ctr, 0, 330, big_truck_payload, avg_unload_secs)
    
    # print the summary stats
    print('Total Packages', routes['Total Packages'])
    print('Total Travel Time', round(routes['Total Travel Time']/3600,1), 'hours')
    print('Total Unload Time', round(routes['Total Unload Time']/3600,1), 'hours')
    print('Total Delivery Time', round(routes['Total Delivery Time']/3600,1), 'hours')

    # display the routes in google maps
    for route in routes['Routes']:
        DeliveryLogistics.open_route_in_browser(route['Delivery Locations'])
    

