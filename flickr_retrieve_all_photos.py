#!/usr/bin/env python
# coding: utf-8

# # Import modules and check for access to flickrApi

# In[ ]:


import flickrapi
import time
import json
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import csv

# Insert flickr API and secret keys here
api_key = ''
secret = ''

flickr = flickrapi.FlickrAPI(api_key, secret, format = 'parsed-json')


# # Scrape all user's photos from a .txt file of user ids.
# 

# In[ ]:


def retrieve_user_ids(path):
    '''
    Obtain user_ids from .txt file
    '''
    list_of_user_ids = []
    
    with open(path, "r") as f:
        for line in f:
            list_of_user_ids.append(line.strip())

    return list_of_user_ids


# In[ ]:


def retrieve_location(photo, is_free = True, google_api_key = ''):
    '''
    Retrieves location of a single photo via Nominatim (OpenStreetMaps)
    Note: Choice of geocoder (A) Nominatim & OpenStreetMaps (B) Google Maps
    If (A), it is slower.
    If (B), requires Google API Key
    '''
    lat = photo.get("latitude")
    lon = photo.get("longitude")
    coordinates = f"{lat}, {lon}"
    
#     If image is NOT geotagged, return NIL
    if lat == "0" and lon == "0":
        return "NIL"
    
#     Check if using free geocoder or not
    if is_free:
        locator = Nominatim(user_agent="myGeocoder", timeout = 10)
    else:
#         Checks for API Key
        if google_api_key != '':
            locator = GoogleV3(api_key=google_api_key)
        else:
            raise Exception("Please fill in Google API Key")
    try:
        location = locator.reverse(coordinates, exactly_one = True, timeout=60)
    except:
        print(f"Request timed out")
        return "Request timed out"
    
    if location != None:
        try:
            location = str(location)
            return location
        except:
            print(f"Cannot return location")
            return "NIL"
    else:
#         print("Location field is empty")
        return "NIL"


# In[ ]:


def retrieve_photo_data(photo, d, is_free, google_api_key, has_geo=True):
    '''
    Input: Photo retrieved from flickr.walk, Dictionary to input photo data into
    '''
    date_upload = photo.get("dateupload")
    try:
        date_upload = datetime.fromtimestamp(int(date_upload)).strftime("%Y-%m-%d, %H:%M:%S")
    except:
        pass
    d["date_upload"] = date_upload
    d["date_taken"] = photo.get("datetaken")
    d["url_500"] = photo.get("url_m")
    d["location"] = retrieve_location(photo, is_free, google_api_key)


# In[ ]:


def user_input():
    # Default settings
    has_geo = True
    is_free = True
    google_api_key = ''
    
    user_ids_file = input("Please input location of .txt file containing user ids: ")
    with open(user_ids_file, "r") as f:
        user_ids = f.read().split()
    output_file = input("Please input name of output file: ")
    while True:
        try:
            geotagged_only = input("Only return photos with location data? [Y/N]\nNote: Some location fields may still be blank. ").lower()
            if geotagged_only == "y":
                has_geo = True
                break
            if geotagged_only == "n":
                has_geo = False
                break
            print("Invalid input. Please enter either 'Y' or 'N'.")
        except Exception as e:
            print(f"Error: {e}\nPlease try again.")
                
    while True:
        try:
            use_google = input("Would you like to use google maps API (PAID)? [Y/N]\nNote: Google Maps is faster but costs money. ").lower()
            if use_google == "y":
                is_free = False
                google_api_key = input("Please enter your google API key: ")
                break
            if use_google == "n":
                is_free = True
                break
            print("Invalid input. Please enter either 'Y' or 'N'.")
                
        except Exception as e:
            print(f"Error: {e}\nPlease try again.")
        
        
    return user_ids, output_file, has_geo, is_free, google_api_key


# In[ ]:


def main():
    '''
    Input: A list of user_ids, output_file of output file
    Output: A list of photo metadata saved into output_file
    
    Note: 
    1) Choice of geocoder (A) Nominatim & OpenStreetMaps (B) Google Maps
        If (A), it is slower.
        If (B), requires Google API Key
    2) If has_geo = True, returns all photos which have been geo-tagged. Some location fields may still be blank.
    If has_geo = False, returns all photos regardless of whether it has been geo-tagged.
    '''

    # Get user input
    user_ids, output_file, has_geo, is_free, google_api_key = user_input()
    
    
    # To use flickr.walk output needs to be in 'etree', not 'parsed-json' 
    start_time = time.time()
    flickr = flickrapi.FlickrAPI(api_key, secret, format = 'etree', timeout = 20000)
    
#     Each user_id is a dictionary containing user_id and images_metadata
#     Array of user_ids. Each user_id is a dictionary?
    
#     A list of all user's dictionary
    metadata_list = []

    for user_id in user_ids:
        data = {}
#         A dictionary for 1 user containing the user's images' metadata
        metadata_per_user = {"user_id": user_id, "images_metadata": []}
        try:
            if has_geo:
                for photo in flickr.walk(user_id = user_id, has_geo = "1", extras = "geo, url_o, url_m, date_taken, date_upload", timeout = 20000):
                    retrieve_photo_data(photo, data, is_free, google_api_key, has_geo=True)
                    metadata_per_user["images_metadata"].append(data.copy())
            else:
                for photo in flickr.walk(user_id = user_id, extras = "geo, url_o, url_m, date_taken, date_upload", timeout = 20000):
                    retrieve_photo_data(photo, data, is_free, google_api_key, has_geo=False)
                    metadata_per_user["images_metadata"].append(data.copy())
        except:
            data = {}
            data["error"] = "Error retrieving data from flickr.walk"
            metadata_per_user["images_metadata"].append(data.copy())
            print(f"Could not retrieve photos for {user_id}")
        metadata_list.append(metadata_per_user)
        print(f"Total number of photos for {user_id}: {len(metadata_list[-1]['images_metadata'])}")
            
    time_taken = round(time.time() - start_time, 2)
    print(f'''
    Total number of users: {len(metadata_list)}
    Time Taken: {time_taken}s
    ''')
    
    flickr = flickrapi.FlickrAPI(api_key, secret, format = 'parsed-json')
    
    # Save to a json file
    with open(f'{output_file}.json', 'w') as json_file:
        json.dump(metadata_list, json_file)
        
    # Save to a csv file
    field_names = ['user_id', 'date_upload', 'date_taken', 'url_500', 'location', 'error'] 

    with open(f"{output_file}.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names)
        writer.writeheader() 
        for i, d in enumerate(metadata_list):
            writer.writerow({'user_id': d['user_id']})
            writer.writerows(d['images_metadata']) 


# In[ ]:


main()

