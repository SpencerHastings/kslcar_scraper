from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
import sys
import html5lib
import requests
from xml.etree import ElementTree as ET
from jinja2 import Environment, FileSystemLoader
from time import sleep

def do_geocode(address):
    geolocator = Nominatim(user_agent="Car_Finder")
    try:
        sleep(1)
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        return do_geocode(address)



pageAdd = "page/"
url = sys.argv[1]
listings=[]
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
page = requests.get(url, headers=headers)
content = page.text
soup = BeautifulSoup(content, features='html5lib')

numResults = int(soup.find('meta', attrs={'name':'description'}).get('content').split(' ', 1)[0])
numPages = (numResults // 24) + 1

print("Getting Listings from " + str(numPages) + " pages")

for i in range(numPages):
    print("Page " + str(i + 1))
    newURL = url + pageAdd + str(i)
    newPage = requests.get(newURL, headers=headers)
    page_content = newPage.text
    page_soup = BeautifulSoup(page_content, features="html5lib")
    #for results in page_soup.findAll('div', attrs={'class':'listing-group'}):
    for listing in page_soup.findAll('div', attrs={'class':'listing'}):
        data = json.loads(listing.get("data-listing"))
        link = "https://cars.ksl.com" + listing.find('a', attrs={'class':'link'}).get("href")
        location = listing.findAll('div', attrs={'class':'listing-detail-line'})[2].text[17:].split('|', 1)[0].rstrip()
        image = listing.find('img').get('src')
        if image.startswith("/images/no"):
            image = "https://cars.ksl.com" + image
        else:
            image = "https:" + image
        listings.append({"data":data,"link":link, "location":location, "image":image})

listingsLoc = {}
locData = {}
numListings = len(listings)
print("Getting Locations of " + str(numListings) + " Listings")
current = 0
print("Listing " + str(current) + "/" + str(numListings))
currentLocs = {}
for listing in listings:
    locString = listing["location"]
    if locString in currentLocs:
        location = currentLocs[locString]
    else:
        location = do_geocode(locString)
        currentLocs[locString] = location
        
    listingsLoc.setdefault(location.address, [])
    listingsLoc[location.address].append(listing)
    if location.address not in locData:
        locData[location.address] = location
    current += 1
    print("Listing " + str(current) + "/" + str(numListings))

def sortListings(listing):
    global locData
    key = listing[0]
    value = listing[1]
    latitude = locData[key].latitude
    return latitude
    
sortedListings = sorted(listingsLoc.items(), key=sortListings, reverse=True)

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('template.html.j2')
output = template.render(listingsItems=list(sortedListings), length=len(sortedListings))
text_file = open("output.html", "w")
text_file.write(output)
text_file.close()