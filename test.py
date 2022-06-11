
import DeliveryLogistics
import csv
import json

avg_unload_secs = 30
max_payload_big_truck = 330
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
    for route in planner.single_truck(distribution_ctr, 0, 330, 330, 30):
        DeliveryLogistics.open_route_in_browser(route['Customers'])
    

