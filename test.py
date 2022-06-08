
import DeliveryLogistics
import csv
import json

avg_unload_seconds_per_bag = 30
max_payload_big_truck = 330
input_file = "data_files/quick_test_data.csv"
distributionCenters = set([DeliveryLogistics.DistributionCenter('Dogwood Elementary School', '12300 Glade Dr, Reston, VA 20191, USA')])
    

if __name__ == "__main__":

    # load our list of customers
    customer_orders = set()
    with open(input_file,'rt',newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer_orders.add(DeliveryLogistics.DeliveryLocation('',row['address'],row['bags']))
    
    # load the google API key
    f = open('data_files/google_api_key.json',)
    data = json.load(f)
    google_api_key = data['google api key']
    f.close()

    print(google_api_key)

    # get the data from google maps 
    trips = DeliveryLogistics.GoogleMapsTripSetBuilder.build(google_api_key, customer_orders, distributionCenters)

    # instantiate a route planning object
    planner = DeliveryLogistics.RoutePlanner(trips)

    distribution_ctr = planner.distribution_centers().pop()

    # calculate the delivery routes
    for route in planner.single_truck(distribution_ctr, 0, 330, 330, 30):
        DeliveryLogistics.open_route_in_browser(route['Customers'])
    

