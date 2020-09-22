# flickr-data-mining

## Features
1. Ability to scrape users on flickr based on user tags or ids of flickr groups
Note: user_ids have been filtered to those who have been on Flickr for *> 2 years* and who have *at least 1000* photographs.  
2. Saves user ids into a .txt file, user information into a .json and .csv file
3. Ability to scrape all user's photos from a .txt file of user ids.
4. Ability to restrict photos scraped to those that are geotagged only
5. Ability to download all photos scraped into specified folder

## How to use
1. Ensure that the relevant modules have been installed via `pip install <insert_module>` Some key modules include: *flickrapi*, *datamuse*, *geopy*
Note: To import datamuse, use `pip install python-datamuse`
2. Start by adding your flickr API and secret key into the respective python files.
3. Run the respective files via `python <insert_file_name>`
- Run flickr_scrape_users to make use of Features 1 and 2
- Run flickr_retrieve_all_photos to make use of Features 3 and 4
- Run download_images to make use of Feature 5

## Other information
1. Runtime for large amounts of data (~500 to 1,000 user ids) will take a significant amount of time and **even longer if the free geo-coding service is used**
2. To use the paid geo-coding service (I.e. Google Maps), please ensure that you have a Google API key. Else, Nominatim will be used.
