
import DeliveryLogistics
import csv
import argparse

epilog = 'Thank you for using the DeliveryLogistics Python Module!'
description="Welcome to Delivery Logistics, a program to calculate efficient delivery routes and display them in Google Maps in a browser."
dist_ctr = '''
The name (or description) and full address of the distribution center.
The address must be a complete and valid address.
Be sure to enclose the name/description in quotation marks if it contains spaces. The address should also be enclosed in quotation marks.
'''

if __name__ == "__main__":

    parser = argparse.ArgumentParser(epilog=epilog, description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-d', '--dist_ctr', help=dist_ctr, nargs=2, metavar=('[name or description]','[full address]'), type=str, action='extend')
    parser.add_argument('-f', '--from_file', help='Calculate routes using a local file instead of using googlemaps.', metavar=('[File name and path]'), type=str, action='store')
    parser.add_argument('-k', '--key', help='Google api key. Only include this option if not including the -f option.', metavar=('[Google API Key]'), type=str, action='store')
    parser.add_argument('-c', '--cust_orders', help='Path and filename for a list of customer orders in CSV format.', metavar=('[File name and path]'), type=str, action='store')
    parser.add_argument('-u', '--avg_unload_secs', default=11, help='The average amount of time (in seconds) that it takes to unload a single item from the delivery truck.', metavar=('[Avg no. of seconds]'), type=int, action='store')
    parser.add_argument('-m', '--max_payload', default=330, help='The maximum payload of the delivery truck.', metavar=('[Maximum payload]'), type=int, action="store")
    parser.add_argument('-o', '--output_file', help='The path and filename of the file to which to save the trips data after downloading with the googlemaps module.', metavar=('[File name and path]'), type=int, action='store')
    args = parser.parse_args()

    if args.from_file:

        trips = DeliveryLogistics.read_trips_from_json(args.from_file)
    
    # get the trips data from googlemaps
    else:

        # get the distribution center passed in by the user
        if args.dist_ctr:
            distributionCenters = set([DeliveryLogistics.DistributionCenter(args.dist_ctr[0], args.dist_ctr[1])])
        else:
            raise ValueError('Expected "-d [distribution center name] [distribution center address]" as command line parameters.')

        # load our list of customers
        if args.cust_orders:
            customer_orders = set()
            with open(args.cust_orders,'rt',newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customer_orders.add(DeliveryLogistics.DeliveryLocation('',row['address'],row['bags']))
        else:
            raise ValueError('Expected -c [customer sales orders file path and name] as a command line paramter.')
        
        # get the google API key
        if args.key:
            google_api_key = args.key
        else:
            raise ValueError('Expected -k [google api key] as a command line parameter.')

        # get the data from google maps 
        trips = DeliveryLogistics.GoogleMapsTripSetBuilder.build(google_api_key, customer_orders, distributionCenters)

        # save the trips to a file if that's what the user wants
        if args.output_file:
            DeliveryLogistics.write_trips_to_json(trips, args.output_file)
    
    # instantiate a route planning object
    planner = DeliveryLogistics.RoutePlanner(trips)

    # get the distribution center
    distribution_ctr = planner.distribution_centers().pop()

    # calculate the delivery routes
    routes = planner.single_payload_and_dist(distribution_ctr, 0, args.max_payload, args.max_payload, args.avg_unload_secs)
    
    # print the summary stats
    print('Total Packages', routes['Total Packages'])
    print('Total Travel Time', round(routes['Total Travel Time']/3600,1), 'hours')
    print('Total Unload Time', round(routes['Total Unload Time']/3600,1), 'hours')
    print('Total Delivery Time', round(routes['Total Delivery Time']/3600,1), 'hours')

    # display the routes in google maps via the browser
    for route in routes['Routes']:
        DeliveryLogistics.open_route_in_browser(route['Delivery Locations'])
    

