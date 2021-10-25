import discord
import requests
import json

# This bot needs a lot of work to make it manageable. Sorry for that :-)

client = discord.Client()

def getISSLocation():
    request = requests.get("http://api.open-notify.org/iss-now.json")
    obj = (request.json())
    location_message = "Current ISS location; Latitude: " + obj['iss_position']['latitude'] + ", Longitude: " + obj['iss_position']['longitude']
    map_message = "https://maps.google.com/maps?q=" + obj['iss_position']['latitude'] + "," + obj['iss_position']['longitude']

    geo_url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + obj['iss_position']['latitude'] +"," + obj['iss_position']['longitude'] +"&result_type=country&key=<google API key>"
    reverse_geo = requests.get(geo_url)
    geo = reverse_geo.json()

    output = location_message + "\r\n" + map_message

    if (geo['status'] == "OK"):
        print(geo['results'][0]['formatted_address'])
        output = output + "\r\n That's above: " + geo['results'][0]['formatted_address']


    return output

def getPeopleinSpace():
   request = requests.get("http://api.open-notify.org/astros.json")
   obj = (request.json())

   output = "Current number of people above the Karman Line is: " + str(obj['number'])

   return output

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$iss_location'):
        await message.channel.send(getISSLocation())

    if message.content.startswith('$peopleinspace'):
        await message.channel.send(getPeopleinSpace())

client.run('Discord bot key')
