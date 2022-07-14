import sys

import requests
import json
import pandas as pd


class ScrapeGmap:
    API_KEY = "FILL THIS IN"
    ATTR_NEEDED = ["name",
                   "price_level",
                   "rating",
                   "user_ratings_total",
                   "formatted_address",
                   "business_status",
                   "geometry"]  # "opening_hours",
    NUM_ENTRY = 2500

    def __init__(self):
        self.restaurant_name = ""
        self.restaurant_address = ""

    def _generate_place_id_url(self, restaurant_name:str, address:str):
        place_id_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" \
                       + "%20".join([restaurant_name.replace(' ', "%20"), address.strip().replace(' ', "%20"), "Chicago"]) \
                       + f"&inputtype=textquery&fields=place_id&key={self.API_KEY}"
        return place_id_url

    def _generate_place_details_url(self, place_id: str):
        place_details_url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" \
                            + place_id \
                            + "&fields=" \
                            + "%2C".join(self.ATTR_NEEDED) \
                            + f"&key={self.API_KEY}"
        return place_details_url

    def _place_request(self, url):
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)

    def _get_place_id(self, restaurant_name, address):
        url = self._generate_place_id_url(restaurant_name, address)
        res_dict = self._place_request(url)

        place_id = res_dict['candidates'][0]['place_id']
        return place_id

    def scrape_place(self, restaurant_name, address):
        try:
            place_id = self._get_place_id(restaurant_name, address)
        except IndexError:
            # place not found
            return

        url = self._generate_place_details_url(place_id)
        res_dict = self._place_request(url)
        all_info = res_dict['result']

        try:
            if ("Chicago" not in all_info["formatted_address"]) or \
                    ("OPERATIONAL" not in all_info["business_status"]):
                # if the place found is weird or no longer open
                return
        except:
            return

        all_info["geometry"] = f"{all_info['geometry']['location']['lat']}, {all_info['geometry']['location']['lng']}"
        return all_info


def load_restaurant(category: str="restaurants"):
    bar_str = ["BAR", "PUB", "CLUB", "BEER", "Club", "LOUNGE", "HOUSE", "BISTRO", "BREWED", "JOINT", "GRILL", "PATIO",
               "BREWERY", "Brewery", "TAPROOM", "WINE", "BREWING", "SPORTS", "Sports", "COCKTAIL", "SIP",
               "TAP", "Tap", "Bar", "DISTILLERY", "HOLE", "Room", "DELI", "TAQUERIA", "TAVERN", "HOTEL", "DINER",
               "RESTAURANT", "SEAFOOD",
               "Tavern", "JOINT", "Joint", "BARREL", "SALOON", "INN", "KITCHEN", "EATERY", "DINER", "GRILLE"]
    cafe_str = ["CAFE", "COFFEE", "Coffee", "BISTRO", "PIZZA", "DONUTS", "DELI", "BAKE", "YOGURT", "POKE",
                "CANTEEN", "SHOP", "DINER", "TEA", "BAKERY", "SUBS", "CHICKEN", "CAKE", "COOKIES",
                "RESTAURANT", "SEAFOOD",
                "BOWL", "FOOD", "TACO", "PIZZERIA", "FISH", "MARKET", "EATERY", "SUSHI", "THAI", "PHO"]
    df = pd.read_csv("./Restaurant.csv")
    df.drop_duplicates(subset=["DBA Name"], keep="first", inplace=True)
    df = df[~df["Results"].str.contains("Out of Business|Fail")]
    df = df[["DBA Name", "Address"]]

    if category == "bar":
        bar_str = '|'.join(bar_str)
        df = df[df["DBA Name"].str.contains(fr"\b({bar_str})\b")]
    elif category == "cafe":
        cafe_str = '|'.join(cafe_str)
        df = df[df["DBA Name"].str.contains(fr"\b({cafe_str})\b")]
    else:
        full_str = '|'.join(bar_str + cafe_str)
        df = df[~df["DBA Name"].str.contains(fr"\b({full_str})\b")]

    return df.sample(n=2300)


def main():
    category = "res"
    result_df = pd.DataFrame(columns=ScrapeGmap.ATTR_NEEDED)
    data_df = load_restaurant(category)

    cnt = 0
    for index, row in data_df.iterrows():
        print(cnt, row["DBA Name"], row["Address"])
        cnt += 1
        info = ScrapeGmap().scrape_place(row["DBA Name"], row["Address"])
        if info is not None:
            result_df = pd.concat([result_df, pd.DataFrame(info, index=[0])], ignore_index=True)

    print(result_df)
    result_df.to_csv(f"./results_{category}_dup.csv")

    result_df.drop_duplicates(subset=["name"], keep="first", inplace=True)
    print(result_df)
    result_df.to_csv(f"./results_{category}.csv")


if __name__ == "__main__":
    main()


