import math

def calculate_angle(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = math.cos(lat2) * math.sin(delta_lon)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
    initial_angle = math.atan2(x, y)
    initial_angle = math.degrees(initial_angle)
    angle = (initial_angle + 360) % 360
    return angle

def calculate_street_position(latitude, longitude):
    CENTER_OF_TOWN_LAT, CENTER_OF_TOWN_LON = 35.220833, -97.443611
    angle = calculate_angle(CENTER_OF_TOWN_LAT, CENTER_OF_TOWN_LON, latitude, longitude)
    if angle >= 337.5 or angle < 22.5:
        return "N"
    elif 67.5 <= angle < 112.5:
        return "E"
    elif 247.5 <= angle < 292.5:
        return "W"
    elif 157.5 <= angle < 202.5:
        return "S"
    elif 22.5 <= angle < 67.5:
        return "NE"
    elif 112.5 <= angle < 157.5:
        return "SE"
    elif 202.5 <= angle < 247.5:
        return "SW"
    elif 292.5 <= angle < 337.5:
        return "NW"