from math import sin, cos, sqrt, atan2, radians, degrees
from collections import namedtuple
import json

Restaurant = namedtuple('Restaurant', ['name', 'lat', 'lon'])

# https://gist.github.com/jeromer/2005586
def compass_bearing(pointA, pointB):
    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])

    diffLong = radians(pointB[1] - pointA[1])

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1)
            * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def world_dist(pointA, pointB):
    R = 6373.0
    dlat = radians(pointB[0]) - radians(pointA[0])
    dlon = radians(pointB[1]) - radians(pointA[1])
    a = sin(dlat / 2)**2 + cos(pointA[0]) * cos(pointB[0]) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def read_restaurants():
    with open('restaurants.json', 'r') as restaurants_file:
        restaurants = []
        restaurants_raw = json.loads(restaurants_file.read())
        for restaurant in restaurants_raw['results']:
            loc = restaurant['geometry']['location']
            restaurants.append(Restaurant(name = restaurant['name'],
                                          lat = loc['lat'],
                                          lon = loc['lng']))
        return restaurants

def round_to(x, b):
        return int(b * round(float(x)/b))

def get_delta(yaw, restaurants, point):
    lat, lon = point
    distance_fn = lambda loc: world_dist((lat, lon), (loc.lat, loc.lon))
    closest = min(restaurants, key=distance_fn)
    distance = distance_fn(closest)
    bearing = compass_bearing((lat, lon), (closest.lat, closest.lon))
    delta = (yaw - bearing) % 360
    return delta, closest, distance

