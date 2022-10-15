# DeliveryLogistics

A python module that calculates efficient delivery routes and displays them in Google Maps so you can review, edit, print, and share them with delivery truck drivers.

## License

*DeliveryLogistics* is licensed under the Apache License. Version 2.0, January 2004. Please see the attched LICENSE.txt file.

## Installation

The first step to installing and running _DeliveryLogistics_ is to be sure that Python 3 is installed on your computer. If you are planning to use this program on your work computer, then please consult your system administrator or IT department for assistance installing Python 3.

To determine if Python 3 is already installed on your computer, open a command line terminal, type the following, and press _Enter_:

```
python3 --version
```
If Python 3 is already installed then you will see the following displayed (the actual numbers may be different, depending upon the version of Python that is installed on your computer):
```
Python 3.10.6
```
Otherwise, please proceed to https://www.python.org/downloads/ to download a copy of Python 3 and obtain installation instructions for Python.

Once Python is installed on your computer you can download _DeliveryLogistics_ by navitating to this repository https://github.com/herrsmitty8128/DeliveryLogistics, clicking on the green _Code_ drop-down menu, and then clicking on _Download Zip_. 

![How to download DeliveryLogistics](https://github.com/herrsmitty8128/DeliveryLogistics/blob/main/img/download_menu.png)

Then download the zip file to a local directory of your choosing, where you should then extract everything in the zip file. Once the files are extracted and Python 3 is installed. You should proceed to the _Dependencies_ section below.


## Dependencies

Most of the Python modules required by _DeliveryLogistics_ are included with Python. However, there is a short list of exceptions below:

- numpy (see https://pypi.org/project/numpy/ for more information)
- googlemaps (see https://pypi.org/project/googlemaps/ for more information)

These modules must be installed to use _DeliveryLogistics_. You can install these packages by opening a command line terminal, typing the following command, and pressing _Enter_:

```
python3 -m pip install numpy googlemaps
```

On Linux, if you are not logged in as a root user then be sure to prepend the commands above with _sudo_.

## Instructions for use

_DeliveryLogistics_ is designed to be used in one of two ways:

1. Obtain distances and drive times from the Google Maps API and calculate efficient routes.
2. Recalculate drive times from a previously saved file.

### Step 1: Obtain a Google API Key.

_DeliveryLogistics_ uses Google Maps to obtain the driving time between every combination of delivery location and distribution center(s). In order for the program to access the Google Maps API online, you must give it your Google Maps API Key. If you do not already have one, then you can obtain one here https://developers.google.com/maps/documentation/javascript/get-api-key.

### Step 2: Make a list of customer orders in CSV file format.

In order to calculate efficient delivery routes, _DeliveryLogistics_ must know the full address and number of packages for each customer. This information is provided to the program at run-time through the use of a file in CSV format. The CSV file must contain all of the following fields:

- "address": The customer's full delivery address. The address must be surrounded by quotation marks.
- "bags": The number of packages to deliver to the customer's address. Quotation marks are not needed.

An example of a properly formated CSV file is below. Most popular spreadsheet applications support CSV format and can be used to create the file.

```CS
address,bags
"123 Main Street, City Name, State 12345", 15
"321 Maple Lane, City Name, State 09384", 5
"4321 My Street, City Name, State 54321", 9
```