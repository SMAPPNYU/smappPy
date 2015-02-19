"""
Functions relating to geo-coding in tweets and twitter (users, etc)
"""

# Geo-bounding-box coordinates in twitter style (south-west corner, north-east corner)
# of common areas. Each box is a list: [sw-long, sw-lat, ne-long, ne-lat]
# NOTE: THESE ARE BEST EFFORT. THERE ARE SIGNIFICANT OVERLAPS.
GeoBox_NorthAmerica = [-167.50, 15.99, -51.48, 70.85]
GeoBox_SouthAmerica = [-88.75, -57.69, -28.63, 14.29]
GeoBox_Europe = [-25.47, 36.05, 33.07, 71.81]
GeoBox_Asia = [72.09, -1.90, 154.71, 52.61]
GeoBox_MiddleEast = [34.47, 22.29, 74.81, 41.66]
GeoBox_Africa = [-22.22, -40.29, 49.50, 38.43]
GeoBox_SouthPacific = [91.35, -53.42, 178.67, 6.91]

GeoBox_Turkey = [25.90, 35.17, 44.70, 41.77]
#GeoBox_Russia = []
#GeoBox_Australia = []

GeoBox_SanFrancisco = [-122.758957382,36.8016310945,-121.751689668,38.0550529401] 
GeoBox_Istanbul = [28.80, 40.80, 29.30, 41.20]

# US Top 10 cities from different states (2013 census)
GeoBox_NewYork = [-74.1272539625,40.4601834953,-73.7496098766,40.9238351317]
GeoBox_LosAngeles = [-118.6938389766,33.4543809893,-117.3703715656,34.2779630492]
GeoBox_Chicago = [-87.9402669,41.5991645815,-87.4594993223,42.023131]
GeoBox_Houston = [-95.7880869,29.523624,-95.014496,30.1107319]
GeoBox_Philadelphia = [-75.280303,39.8670041,-74.9557629,40.1379919]
GeoBox_Phoenix = [-112.4449056094,33.1985349519,-111.6033226113,33.8770957331]
GeoBox_Indianapolos = [-86.3281211,39.632177,-85.9373789,39.927392]
GeoBox_Jacksonville = [-81.8929466242,30.103748,-81.3950931,30.586232]
GeoBox_Columbus = [-83.2102799,39.808631,-82.7713781,40.1572719]
GeoBox_Charlotte = [-81.0089479,35.0131739,-80.6131124229,35.393133]

USTopTen_DiftStates = [GeoBox_NewYork, GeoBox_LosAngeles, GeoBox_Chicago,
    GeoBox_Houston, GeoBox_Philadelphia, GeoBox_Phoenix, GeoBox_Indianapolos, 
    GeoBox_Jacksonville, GeoBox_Columbus, GeoBox_Charlotte]

ContinentsGeoBoxes = [GeoBox_NorthAmerica, GeoBox_SouthAmerica, GeoBox_Europe,
GeoBox_Asia, GeoBox_MiddleEast, GeoBox_Africa, GeoBox_SouthPacific]


ContinentCode = {
    -1: "Unknown",
    0: "North America",
    1: "South America",
    2: "Europe",
    3: "Asia",
    4: "Middle East",
    5: "Africa",
    6: "South Pacific (Australia)",
}


class GeoboxException(Exception):
    """Custom exception for geobox errors"""
    pass


def is_geocoded(tweet):
    """
    Returns True if tweet is geocoded. Tweet is a tweet-dict.
    """
    if "coordinates" in tweet and tweet["coordinates"]:
        return True
    elif "geo" in tweet and tweet["geo"]:
        return True
    return False


def get_coordinates(tweet):
    """
    Returns a list of floats, [longitude, lattitude], of tweet geo 
    coordinates. If tweet is not geocoded, returns empty list.
    """
    if not is_geocoded(tweet):
        return []
    if "coordinates" in tweet:
        return tweet["coordinates"]["coordinates"]
    else:
        return tweet["geo"]["coordinates"]


def get_tweet_region(tweet, regions=ContinentsGeoBoxes):
    """Takes a tweet and hierarchically tries to match it's geocode to a region.
    If tweet is not geocoded, returns -1 ("Unknown"). If is geocoded but does 
    not match any region provided, returns -1 ("Unknown").
    Returns the index of the entry in the list of GeoBoxes given that the tweet
    first matches, or -1.
    'regions' is a list of lists representing a Geobox, where each sublist is a 
    list of 4 floats, format: [sw-long, sw-lat, ne-long, ne-lat]
    By default, uses all Continents-Regions. Consult module ContinentCode dict for 
    string representing return value in this case.
    NOTE: Will return semantic errors if boxes are not range-continuous (aka, their 
        sw-long is GT their ne-long)
    """
    if not is_geocoded(tweet):
        return -1
    lon, lat = get_coordinates(tweet)
    for i in range(len(regions)):
        box = check_geobox(regions[i])
        if lon > box[0] and lon < box[2] and lat > box[1] and lat < box[3]:
            return i
    return -1

def check_geobox(box):
    """Takes a geobox (list of 4 floats representing sw-lon, sw-lat, ne-lon, ne-lat)
    and checks to make sure bounds are sound (ie, no poorly formed boxes).
    If box is ok, returns float-cast version.
    """
    if len(box) != 4:
        raise GeoboxException("Geobox does not have 4 entries")
    try:
        box = [float(c) for c in box]
    except Exception as e:
        raise GeoboxException("Cannot convert geobox entries to floats (error: {0})".format(e))
    if box[0] >= box[2]:
        raise GeoboxException("SW-long >= NE-long")
    if box[1] >= box[3]:
        raise GeoboxException("SW-lat >= NE-lat")
    return box






