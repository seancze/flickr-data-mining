#!/usr/bin/env python
# coding: utf-8

# Import modules and check for access to flickrApi



import flickrapi
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import datamuse
import json
from collections import OrderedDict
import csv
import io
import os
import urllib
import pandas as pd

# Add your flickr API and secret keys here
api_key = ''
secret = ''

flickr = flickrapi.FlickrAPI(api_key, secret, format = 'parsed-json')


# # Obtain list of user_ids based around search preferences (I.e. Inputted tags)


# Auxiliary Function
def get_arr(my_str):
    '''
    Get array from string
    '''
    my_arr = my_str.split(",")
    my_arr = [x.strip() for x in my_arr]
    return my_arr



def get_top3_tags(main_tag):
    '''
    Input: A main tag with a type of String
    
    Output: Returns the top 3 tags for each cluster that is related to the main tag inputted.
    '''
    top3_tags = []
    
    cluster_list = flickr.tags.getClusters(tag = main_tag)["clusters"]["cluster"]
    tag_list = cluster_list[1]["tag"][0:3]

    for cluster in cluster_list:
        tag_list = cluster["tag"][0:3]
        top3_tags_per_cluster = []
        for tag in tag_list:
            top3_tags_per_cluster.append(tag.get("_content"))
        top3_tags.append(top3_tags_per_cluster)
    return top3_tags



# Example of some tags
# backpacker, tourist, vacation, sightseeing, scenery, holiday resort, excursion, hiking, cruise, globetrotter, adventurer, mountaineer, hotel, amusement park, ryokan, festival, carnival
# The list of tags manually determined by a person to obtain related photos
# main_tags = ['backpacker', 'tourist', 'vacation', 'sightseeing', 'scenery', 'holiday resort', 'excursion', 'hiking', 'cruise', 'globetrotter', 'adventurer', 'mountaineer', 'hotel', 'amusement park', 'ryokan', 'festival', 'carnival']
# main_tags_2 = ['backpacker', 'tourist', 'adventurer', 'globetrotter', 'mountaineer', 'traveller']

def get_related_tags(main_tags):
    '''
    Returns top 10 related words according to datamuse API
    '''
    api = datamuse.Datamuse()
    all_tags = []
    for tag in main_tags:
        words = api.words(ml = tag, max=10)
        for word in words:
            all_tags.append(word.get('word'))
            
#     Remove duplicates from list
    unique_tags = list(set(all_tags))
    print(f'Number of tags: {len(unique_tags)}')
    return unique_tags




def get_user_ids(main_tag, top3_tags):
    '''
    Returns a list of user_ids for the top 24 photos returned based on the inputted tag and cluster tags related to it
    '''
    user_id_and_tags = {}
    start_time = time.time()
    user_ids = []
#     Obtain the corresponding list of main and cluster tags used to find the user
    for tags in top3_tags:
        
        try:
            tags_to_string = '-'.join(tags)
            user_list = flickr.tags.getClusterPhotos(tag=main_tag, cluster_id=tags_to_string)["photos"]["photo"]
        except:
            pass
        for user in user_list:
            user_id_and_tags['main_tag'] = main_tag
            user_id_and_tags['cluser_tags'] = tags_to_string
            user_id_and_tags['owner'] = user['owner']
            user_ids.append(user_id_and_tags.copy())
    print(f"Number of user_ids: {len(user_ids)}")
    return user_ids




def get_ids_from_groups(group_ids):
    '''
    Input: A list of group_ids
    Output: A list of user_ids found in the group. Only works for groups with public access
    '''
    member_ids = []
    all_pages = []
#     Obtain user_ids for all members in a list of group_ids
    for group in group_ids:
        try:
            num_pages = flickr.groups.members.getList(group_id = group, per_page = 500, page = 1)["members"]["pages"]
            for page in range(num_pages):
                all_pages.append(flickr.groups.members.getList(group_id = group, page = page))
                member_list = flickr.groups.members.getList(group_id = group, per_page = 500, page = page)["members"]["member"]
                for member in member_list:
                    member_ids.append(member["nsid"])
        except:
            print("Error in getting members from Group")
            pass
    print(f'User_ids from groups: {len(member_ids)}')
    return member_ids



def filter_users(user_ids):
    '''
    Returns a list of user_ids who have been on Flickr for more than 2 years and have posted more than 1000 photos
    '''
    
    start_time = time.time()
    shortlisted_ids = []
    for user_id in user_ids:

#     Obtain the metadata related to a Flicker's user photographs
        try:
            photos_dictionary = flickr.people.getInfo(user_id=user_id["owner"])["person"]["photos"]
        except:
            pass
    
#     Retrieve number of pictures
        num_pictures = photos_dictionary["count"]["_content"]
    
#     Retrieve date of first photo as a string and convert to date object
        date_str = photos_dictionary["firstdatetaken"]["_content"]

        if date_str != None:
            if date_str.split('-')[0] != '0000':
                first_photo_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            elif date_str.split('-')[0] == '0000':
                print("Year is 0000")
        elif date_str == None:
            print("Date field is empty")
            
        
        two_years_ago = datetime.now() - relativedelta(years=2)
    #     If more than 2 years AND > 1000 photos, add user_id
        
        if two_years_ago > first_photo_date and num_pictures > 1000:
            shortlisted_ids.append(user_id)
    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Shortlisted_ids: {len(shortlisted_ids)}")
    return shortlisted_ids
    


def retrieve_relevant_headers(user_ids, user_info, file_name):
    '''
    Input: 
    - A list of user_ids.
    - A list of user_info.
    - Name of file. Note: MUST end in .csv as it has to be a .csv file!
    
    Output: A table with the following headers
    - main_tag
    - cluster_tags
    - user_id
    - username
    - location
    - num_photos
    - date_of_first_photo
    '''
    f = csv.writer(open(f"{file_name}.csv", "w+", encoding = "utf-8"), lineterminator = '\n')

    # Write CSV Header, If you dont need that, remove this line
    f.writerow(["main_tag", "cluser_tags", "user_id", "username", "location", "num_photos", "date_of_first_photo"])

    for i, el in enumerate(user_ids):
    #     Try retrieving location as location may be None
        try:
            location = user_info[i]["person"]["location"]["_content"]
        except:
            location = None
        f.writerow([user_ids[i]["main_tag"],
                    user_ids[i]["cluser_tags"],
                    user_ids[i]["owner"],
                    user_info[i]["person"]["username"]["_content"],
                    location,
                    user_info[i]["person"]["photos"]["count"]["_content"],
                    user_info[i]["person"]["photos"]["firstdatetaken"]["_content"]])


def main():
    '''
    Output:
    1) A list of unique user ids with more than 1,000 photos and who have been on Flickr for > 2 years in a txt file
    2) A .json file containing all the user's information according to flickr's API (flickr.people.getInfo)
    3) A .csv file containing only more crucial user's information
    '''

    finalised_user_info = []
    finalised_user_ids = []

    file_name = input("Please input the name for your output files: ")

    while True:
        try:
            searchByTag = int(input("Enter '1' to search user ids by tag or '2' to search user ids by groups: "))
            break
        except:
            print("Please input either '1' or '2'")

    if searchByTag == 1:
        tags_str = input("Please input a list of tags separated by commas: ")
        tags = get_arr(tags_str)

        for tag in tags:
            # To allow the loop to continue running in the event any tag causes any error in one of the functions
            try:

                # Obtain top 3 tags
                top_3_tags = get_top3_tags(tags)

                # Obtain all_tags
                all_tags = get_related_tags(tags)

                # Obtain user ids
                user_ids = get_user_ids(all_tags, top_3_tags)

                # Filter user ids
                shortlisted_ids = filter_users(user_ids)

                # If user_id has NOT already been appended, then append to finalised_user_ids
                for potential_user_id in shortlisted_ids:
                    if not any(user['owner'] == potential_user_id['owner'] for user in finalised_user_ids):
                        finalised_user_ids.append(potential_user_id)

                print(f'Total user_ids: {len(finalised_user_ids)}')
            except Exception as e:
                print(f"Error in obtaining users from tags: {e} \n Moving over to next loop")
                continue

    else:
        group_ids_str = input("Please input a list of group ids separated by commas: ")
        group_ids = get_arr(group_ids_str)

        # Obtain user ids
        user_ids = get_ids_from_groups(group_ids)
        
        # To allow the loop to continue running in the event flickrAPI call in filter_users fails
        try:
            # Filter user ids
            shortlisted_ids = filter_users(user_ids)

            # If user_id has NOT already been appended, then append to finalised_user_ids
            for potential_user_id in shortlisted_ids:
                if not any(user['owner'] == potential_user_id['owner'] for user in finalised_user_ids):
                    finalised_user_ids.append(potential_user_id)

            print(f'Total user_ids: {len(finalised_user_ids)}')
        except Exception as e:
            print(f"Error in obtaining users from group ids: {e} \n Moving over to next loop")
    
    
    # Get all user_info from the respective user_ids
    for user_id in finalised_user_ids:
        try:
            finalised_user_info.append(flickr.people.getInfo(user_id=user_id["owner"]))
        except Exception as e:
            print(f"Error in getting user info from user id: {e} \n Moving over to next loop")
            continue



    # NEW: Sort user_info
    # Breakdown of code
    # (a) Zip / Join the 2 lists together
    # (b) Sort according to num of pictures in user_info in descending order
    # (c) Zip the list of tuples together and unpack them using the asterisks *
        sorted_user_ids, sorted_user_info = zip(*[(x,y) for (x,y) in sorted(zip(finalised_user_ids,finalised_user_info), key=lambda pair: pair[1]["person"]["photos"]["count"]["_content"], reverse=True)])    
        
        # Save user_ids to .txt file
        with open(file_name, "w") as f:
            for i in sorted_user_ids:
                f.write(f"{i['owner']}\n")
        
        # Save all user_info to json file
        with open(f'{file_name}.json', 'w') as json_file:
            json.dump(sorted_user_info, json_file)
        
        # Save more important user info to csv file
        retrieve_relevant_headers(sorted_user_ids, sorted_user_info, file_name)        


if __name__ == "__main__":
    main()