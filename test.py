
import DeliveryLogistics
import csv
import sys

# default values
avg_unload_secs = 11
big_truck_payload = 330
#customer_file = 'data_files/2022_orders.csv'
#api_key_file = 'data_files/google_api_key.json'
#distributionCenters = set([DeliveryLogistics.DistributionCenter('Dogwood Elementary School', '12300 Glade Dr, Reston, VA 20191, USA')])
    

if __name__ == "__main__":

    if '-from_google' in sys.argv:

        # get the distribution center passed in by the user
        if '-d' in sys.argv:
            i = sys.argv.index('-d')
            n = sys.argv[i+1]
            d = sys.argv[i+2]
            distributionCenters = set([DeliveryLogistics.DistributionCenter(n, d)])
        else:
            raise ValueError('Expected "-d [distribution center name] [distribution center address]" as command line parameters.')

        # load our list of customers
        if '-c' in sys.argv:
            i = sys.argv.index('-c')
            f = sys.argv[i+1]
            customer_orders = set()
            with open(f,'rt',newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customer_orders.add(DeliveryLogistics.DeliveryLocation('',row['address'],row['bags']))
        else:
            raise ValueError('Expected -c [sales orders file path and name] as a command line paramter.')
        
        # get the google API key
        if '-k' in sys.argv:
            i = sys.argv.index('-k')
            google_api_key = sys.argv[i+1]
        else:
            raise ValueError('Expected -k [google key] as a command line parameter.')
        
        if '-max_payload' in sys.argv:
            i = sys.argv.index('-max_payload') + 1
            big_truck_payload = int(sys.argv[i])
        
        if '-unload_time' in sys.argv:
            i = sys.argv.index('-unload_time') + 1
            avg_unload_secs = int(sys.argv[i])

        # get the data from google maps 
        trips = DeliveryLogistics.GoogleMapsTripSetBuilder.build(google_api_key, customer_orders, distributionCenters)

        # save the trips to a file if that's what the user wants
        if '-o' in sys.argv:
            i = sys.argv.index('-o')
            f = sys.argv[i+1]
            DeliveryLogistics.write_trips_to_json(trips, f)

    elif '-from_file' in sys.argv:

        i = sys.argv.index('-from_file') + 1
        f = sys.argv[i]
        
        if '-max_payload' in sys.argv:
            i = sys.argv.index('-max_payload') + 1
            big_truck_payload = int(sys.argv[i])
        
        if '-unload_time' in sys.argv:
            i = sys.argv.index('-unload_time') + 1
            avg_unload_secs = int(sys.argv[i])
        
        trips = DeliveryLogistics.read_trips_from_json(f)
    
    else:
        raise ValueError('Expected either "-from_file" or "-from_google" as a command line arg.')
    
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

    # display the routes in google maps via the browser
    for route in routes['Routes']:
        DeliveryLogistics.open_route_in_browser(route['Delivery Locations'])
    

