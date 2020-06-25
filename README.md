# flickr-data-mining

## How to use
1) Create a list of main_tags that you want to based your search around. For instance,  
`cuisine = ['Japanese', 'Korean', 'Chinese', Vietnamese', 'Asian']`
2) Pass the tags through get_related_tags to retrieve tags related to it. This is to broaden one's search.  
`all_tags = get_related_tags(cuisine)`
3) Retrieve a list of user_ids and their respective information via globetrotters(). Pass your file name to the 2nd argument. A .json file will be created in your current directory.
Note: user_ids have been filtered to those who have been on Flickr for *> 2 years* and who have *at least 1000* photographs.  
`finalised_user_ids, finalised_user_info = globetrotters(cuisine, "My JSON file name")`
4) Pass the outputs of globetrotters into retrieve_relevant_headers to obtain a .csv file in your current working directory. Similarly, input your file name as the 2nd argument.  
`retrieve_relevant_headers(finalised_user_ids, finalised_user_info, "My CSV file name")`
5) Optionally, you may retrieve the image location and url in a list from all user_ids collected via retrieve_images_metadata.
Note: Execution will take a significant amount of time and **even longer if the free geo-coding service is used**  
`metadata_list = retrieve_images_metadata(finalised_user_ids, isFree = False, google_api_key = <Insert API Key>)`
6) From the metadata_list retrieved, images can be downloaded into your_folder_name which will be stored in an Images folder under your current working directory.  
`download_images("My Folder Name", metadata_list)`
