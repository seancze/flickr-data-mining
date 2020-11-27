#!/usr/bin/env python
# coding: utf-8


import json
import pandas as pd
import csv
import io
import os
import urllib.request as urllib

def download_images_csv():
    # Ask for location of csv file
    user_input = input("Location of csv file: ")
# To download images from csv
    df = pd.read_csv(user_input)

    user_id = df["user_id"].dropna()
    image_links = df["url_500"]

    # For each user_id
    for i, el in enumerate(user_id):
        idx = user_id.index[i]
        start = idx + 1
        if (i+1) == len(user_id):
            end = df.index[-1]
        else:
            end = user_id.index[i+1]

        image_dir = os.path.join(f"{os.getcwd()}", "images")
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        user_image_dir = os.path.join(f"{os.getcwd()}", "images", f"{el}")
        if not os.path.exists(user_image_dir):
            os.mkdir(user_image_dir)

        for num, link in enumerate(image_links[start:end]): 
            image_path = os.path.join(f"{user_image_dir}", f"{num}.jpg")
            if os.path.exists(image_path):
                continue
            
            if link != None:
    #                 Try importing urllib.request directly first
                try:
                    urllib.urlretrieve(link, f"{user_image_dir}\\{num}.jpg")
                except Exception as e:
                    print(f"Could not retrieve image, {str(e)}")
                    continue
        print(f"Status: {i+1}/{len(user_id)}")
        print(f"Total pictures downloaded for {el}: {end-start}")

def json_to_dict(file, is_json = True):
    '''
    Obtain a regular dictionary from .JSON file
    '''
    if is_json:
        with open(file, 'r') as f:
            regular_dict = json.load(f)
            return regular_dict
    regular_dict = json.loads(json.dumps(file))
    return regular_dict


def download_images_json():
    '''
    Input: metadata_list from the output of retrieve_images_metadata
    Output: Downloads images as .jpg into a folder labelled 'folder_name' which will be found within an 'images' folder
    '''
    user_input = input("Please enter the path to the .JSON file: ")
    image_metadata = json_to_dict(user_input)
    
    for user in metadata_list:
        # Download image from the url and save it to '1.jpg'
#         NOTE: RMB TO CHANGE BACK TO f"{os.getcwd()}"
        image_dir = os.path.join(f"{os.getcwd()}", "images")
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        user_image_dir = os.path.join(f"{os.getcwd()}", "images", f"{user['user_id']}")
        if not os.path.exists(user_image_dir):
            os.mkdir(user_image_dir)
        
        for i, photo in enumerate(user["images_metadata"]): 
            if photo["url_1024"] != None:
#                 Try importing urllib.request directly first
                try:
                    urllib.urlretrieve(photo["url_1024"], f"{user_image_dir}\\{i}.jpg")
                except Exception as e:
                    print(f"Could not retrieve image, {str(e)}")
                    continue


def main():
#     Check if json or csv
    is_csv = True
    while True:
        is_csv_or_json = input("Please input 'csv' or 'json' if your file is csv or json respectively: ").lower()
        if is_csv_or_json == "csv":
            is_csv = True
            break
        if is_csv_or_json == "json":
            is_csv = False
            break
        print("Did not input csv or json. Please try again.")
    
    if is_csv:
        download_images_csv()
    else:
        download_images_json()


if __name__ == "__main__":
    main()

