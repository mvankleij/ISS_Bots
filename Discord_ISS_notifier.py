import requests
from discord_webhook import DiscordWebhook
import json
import urllib
import time
from datetime import datetime
import configparser

# APIs used:
# https://api.sunrise-sunset.org
# https://wheretheiss.at/w/developer

# ToDo:
# - Check whether it is dark outside.

def loadConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def reverseGeo(latitude, longitude):
    geo_url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + latitude + "," + longitude + "&result_type=country&key=" + GoogleAPIKey
    reverse_geo = requests.get(geo_url)
    geo = reverse_geo.json()


    if (geo['status'] == "OK"):
        print(geo['results'][0]['formatted_address'])
        return geo['results'][0]['formatted_address']
    else:
        return "Ocean"

def getSunDown(minute, latitude, longitude):
    sun_url = "https://api.sunrise-sunset.org/json?lat=" + str(latitude) + "&lng="+ str(longitude) + "formatted=0"
    sun_request = requests.get(sun_url)
    sun = sun_request.json()
    #currenttime = time.ctime(time.time())
    utchour = datetime.utcnow().hour
    utcminute = datetime.utcnow().minute + minute

    currenttime = time.localtime()
    print("UTC time = " + str(utctime))
    print("Current time: " + str(currenttime))
    print("Sunset: " +  sun['results']['sunset'])
    return sun['results']['sunset']

def publishWebHook(message):
    webhook_message = DiscordWebhook(url=webhook_url, content=message)
    response = webhook_message.execute()


timestamp = str(int(time.time()))

# This for loop ensures that we check the position of the ISS for the next 20 minutes with a 2 minute interval.
# You can change these values as required, but ensure you have at most 10 timestamps as that's the API limit.
for i in range(2, 20, 2):
    time_add = 60*i
    new_time = int(time.time() + time_add)
    timestamp = timestamp + "," + str(new_time)

print (timestamp)
config = loadConfig()
GoogleAPIKey = config['API_Settings']['GoogleAPIKey']
webhook_url = config['Discord_Settings']['webhook_url']
lat_min = int(config['Map_Settings']['lat_min'])
lat_max = int(config['Map_Settings']['lat_max'])
long_min = int(config['Map_Settings']['long_min'])
long_max = int(config['Map_Settings']['long_max'])

future_url = "https://api.wheretheiss.at/v1/satellites/25544/positions?timestamps=" + timestamp + "&units=km"
future_request = requests.get(future_url)

future_json = future_request.json()

minute = 2
previousCountry = ""

for entry in future_json:
    latitude = entry['latitude']
    longitude = entry['longitude']
    visibility = entry['visibility']
    print(latitude)
    print(longitude)
    print(visibility)
    # The latitude and longitude numbers used in the if statement below refer to a box drawn around Europe (between Ireland in the west, Greece in the east. Denmark in the North and Spain in the south).
    # This is to limit the calls to Google's geo location API to a managable number, to prevent paying for the service.
    # If the visibility of the ISS is eclipsed it will not be visible. That's another reason not to call for the location as it's useless anyway.
    #getSunDown(minute,latitude,longitude)
    if ( (lat_min < latitude < lat_max) and ( long_min < longitude < long_max ) and visibility != "eclipsed"):
        country = reverseGeo(str(entry['latitude']), str(entry['longitude']))
        print("ISS is above Europe")
        if (country != "Ocean" and country != previousCountry):
            publishWebHook("ISS will be above " + country + " in " + str(minute) + " minutes.\r\nIt should be visible")
            previousCountry = country
            # If the country is the Netherlands or Belgium include a map link in the post.
            if (country == "Netherlands" or country == "Belgium"):
                publishWebHook("https://maps.google.com/maps?q=" + str(latitude) + "," + str(longitude))
    minute += 2
    # Short sleep time to prevent flooding of API requests.
    time.sleep(1)
