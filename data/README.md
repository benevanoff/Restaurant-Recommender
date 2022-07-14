# Data files

This folder contains the raw data csv and fake generators that we used to put together the source data of our project.

As explained in the doc:
Our application needs actual restaurant, bar, and cafe information from the Chicago area. We first found a food inspection database:
https://data.cityofchicago.org/Health-Human-Services/Restaurant/5udb-dr6f. We then pulled the name of all places and split them into 3 categories and then used the google maps places API:
https://developers.google.com/maps/documentation/places/web-service/overview to scrape all the data we need for each place: name, address, longitude, and latitude for us to calculate distances, price-level, ratings and the number of ratings for recommendations.

We generated artificial data for the rest relations because we do not have a user base and the menu items were not easy to scrape. We will consider adding the actual menu info before the final demo, but artificial data so far should be adequate for the purpose of stage 3.

## bar.csv, cafe.csv, restaurant.csv
These are the actual data scraped from google maps. They were later manually cleaned to change the encoding format from utf-8 to ascii so that the sql workbench can recognize it. These took forever to scrape and the sizes are really small, so I'm simply uploading the raw datafiles here.

## fake_data.py
This was used to generat the fake user and menu data with charateristics matching our schema constraints.
  **#TODO: They are not directly runnable for now, will clean up.**

## gmap_api.py
This was used to scrape data based on a huge csv from the public database. To run it, please: 

1. download the csv file from the link above;
2. register for a gmap platform account and there is a 300 dollar free credits and use the API_KEY to scrape.

Note that the food inspection csv downloaded and the google maps scraping results will contain A LOT of duplicates. So there were also some cleaning up codes in there.
  **#TODO: They are not directly runnable for now, will clean up.**










