import requests
import oauth2
import urllib
import urllib2
import json
from random import randint

url = 'https://api.uber.com/v1/products'
# OAuth credential placeholders that must be filled in by users. YELP
CONSUMER_KEY = 'z2cWmfBk_CT57_uubXyb8w'
CONSUMER_SECRET ='FEx_ENT2BWVOZBiHrVikBoTdMFw'
TOKEN = 'YTQZo202KD2RwFCwN2DI0rHyZT4LG4as'
TOKEN_SECRET = 'rcoqfwZeJ6LJr31cbWBdoty91J8'
API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

parameters = {
    'server_token': 'LrrQZVjHygsr0Km2wez9KcWHYkB1FoPP-x_PGr1x',
    'latitude': 37.775818,
    'longitude': -122.418028,
}

#response = requests.get(url, params=parameters)

#data = response.json()

def uberEstimate(start_lat, start_long, end_lat, end_long):
  parameters = {
    'server_token': 'LrrQZVjHygsr0Km2wez9KcWHYkB1FoPP-x_PGr1x',
    'start_latitude': start_lat,
    'start_longitude': start_long,
    'end_latitude': end_lat,
    'end_longitude': end_long,
  }
  response = requests.get('https://api.uber.com/v1/estimates/price', params=parameters)
  data = response.json()
  for i in data["prices"]:
    if i["display_name"] == 'uberX':
      return {'price':i["low_estimate"], 'duration': i['duration']}
  return {'price':0, 'duration':0}


# for Yelp
def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location, start_lat, start_long, radius_filter, sort):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'cll': str(start_lat)+","+str(start_long),
        'limit': 10,
        'sort': 0,
        'radius_filter': radius_filter,
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def business_ye(business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)

def yelpPlaces(location, start_lat, start_long, category):
    url_params = {
        'term': "",
        'location': location.replace(' ', '+'),
        'cll': str(start_lat)+","+str(start_long),
        'limit': 6,
        'sort': 0,
        'radius_filter': 40000,
        'category_filter': category,
    }
    data =  request(API_HOST, SEARCH_PATH, url_params=url_params)
    # implementa random len(data["businesses"])
    business_obj = data["businesses"][randint(0,len(data["businesses"]) - 1)]
    business_id = business_obj["id"]
    business = business_ye(business_id)
    output = {}
    if 'name' in business.keys():
      output['name'] = business["name"]
    if 'image_url' in business.keys():
      output['image_url'] = business["image_url"]
    if 'url' in business.keys():
      output['url'] = business["url"]
    if 'display_phone' in business.keys():
      output['display_phone'] = business["display_phone"]
    if 'snippet_text' in business.keys():
      output['snippet_text'] = business["snippet_text"]
    if 'location' in business.keys():
      output['location'] = business["location"]
    return output
# name, image_url, url, display_phone, snippet_text, location.display_address, location

def yelpFood(location, start_lat, start_long, term=""):
    data = search("food " + term, location, start_lat, start_long, 1000, 0)
    # implementa random len(data["businesses"])
    business_id = data["businesses"][randint(0,len(data["businesses"]) - 1)]["id"]
    return business_ye(business_id)

"""
print yelpPlaces("San Francisco",37.7833, 122.4167, "active")
print yelpPlaces("San Francisco",37.7833, 122.4167, "arts")
print yelpPlaces("San Francisco",37.7833, 122.4167, "nightlife")
print yelpPlaces("San Francisco",37.7833, 122.4167, "bars,danceclubs")
"""

def jsonOutput(start_location):
  output = []
  address = start_location
  coord = addressToCoord(start_location)
  business = yelpPlaces(address, coord['lat'], coord['lng'], "active")
  output.append(business)

  address = ', '.join(business['location']['display_address'])
  coord = {'lat': business['location']['coordinate']['latitude'], 'lng': business['location']['coordinate']['longitude']}
  business = yelpFood(address, coord['lat'], coord['lng'])
  output.append(business)

  address = ', '.join(business['location']['display_address'])
  coord = {'lat': business['location']['coordinate']['latitude'], 'lng': business['location']['coordinate']['longitude']}
  business = yelpPlaces(address, coord['lat'], coord['lng'], "arts")
  output.append(business)

  address = ', '.join(business['location']['display_address'])
  coord = {'lat': business['location']['coordinate']['latitude'], 'lng': business['location']['coordinate']['longitude']}
  business = yelpFood(address, coord['lat'], coord['lng'])
  output.append(business)

  address = ', '.join(business['location']['display_address'])
  coord = {'lat': business['location']['coordinate']['latitude'], 'lng': business['location']['coordinate']['longitude']}
  business = yelpPlaces(address, coord['lat'], coord['lng'], "nightlife")
  output.append(business)

  address = ', '.join(business['location']['display_address'])
  coord = {'lat': business['location']['coordinate']['latitude'], 'lng': business['location']['coordinate']['longitude']}
  business = yelpPlaces(address, coord['lat'], coord['lng'], "bars,danceclubs")
  output.append(business)

  return output

def addressToCoord(address):
  parameters = {
    'address': address.replace(' ', '+'),
    'key': 'AIzaSyA_SavtJzenBE3POK17vXexdnGsxs2Pm0g',
  }
  response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=parameters)
  data = response.json()
  return data['results'][0]['geometry']['location']

print jsonOutput("2580 El Camino Real Redwood")

# name, image_url, url, display_phone, snippet_text, location.display_address, location
