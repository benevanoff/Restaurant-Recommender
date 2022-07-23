import random
import string
import sys

import numpy as np
import pandas as pd


# Generate food data
def gen_food(n=1200):
    random.seed(411)
    fd_name = []
    for _ in range(n):
        fd_name.append(''.join(random.choice(string.ascii_letters)
                               for _ in range(random.choice(np.arange(1, 35)))))

    df = pd.DataFrame(fd_name, columns=["dish_name"])
    df.drop_duplicates(inplace=True, keep="first")
    return df


# Generate User data
def gen_customer(n=200):
    random.seed(411)
    user_name = []
    real_name = []
    for _ in range(n):
        user_name.append(''.join(random.choice(string.ascii_letters)
                                 for _ in range(random.choice(np.arange(1, 35)))))
        real_name.append(''.join(random.choice(string.ascii_letters)
                                 for _ in range(random.choice(np.arange(1, 255)))))
    df = pd.DataFrame(list(zip(user_name, real_name)), columns=["user_name", "name"])
    df.drop_duplicates(subset=["user_name"], inplace=True, keep="first", ignore_index=True)
    return df


# generate favorites
def gen_favorites(cus_df, food_df, n=400):
    random.seed(411)
    customer = []
    food = []
    for _ in range(n):
        cus_idx = random.choice(np.arange(len(cus_df.index)))
        customer.append(cus_df.iloc[cus_idx]["user_name"])
        food.append(random.choice(np.arange(len(food_df.index))))
    df = pd.DataFrame(list(zip(customer, food)), columns=["user_name", "food_id"])
    df.drop_duplicates(inplace=True, keep="first")
    df.sort_values(by=["user_name"], inplace=True, ignore_index=True)
    return df


# generate serves
def gen_serve(place_df, food_df, n=2000):
    place = []
    food = []
    for _ in range(n):
        place.append(random.choice(np.arange(len(place_df.index))))
        food.append(random.choice(np.arange(len(food_df.index))))
    df = pd.DataFrame(list(zip(place, food)), columns=["place_id", "food_id"])
    df.drop_duplicates(inplace=True, keep="first")
    df.sort_values(by=["place_id"], inplace=True, ignore_index=True)
    return df


# generate orders
def gen_orders(cus_df, place_df, food_df, n=1500):
    customer = []
    place = []
    food = []
    for _ in range(n):
        cus_idx = random.choice(np.arange(len(cus_df.index)))
        customer.append(cus_df.iloc[cus_idx]["user_name"])

        place.append(random.choice(np.arange(len(place_df.index))))
        food.append(random.choice(np.arange(len(food_df.index))))
    df = pd.DataFrame(list(zip(customer, food, place)), columns=["user_name", "food_id", "place_id"])
    df.drop_duplicates(inplace=True, keep="first", ignore_index=True)
    return df


def load_place_df(type_="bar"):
    df = pd.read_csv(f"./results_{type_}.csv")
    df = df.iloc[:, 1:]
    return df


def adjust_id():
    for f in ["customers", "favorites", "food", "order_bar", "order_cafe", "order_res", "results_bar",
              "results_cafe", "results_res", "serve_bar", "serve_cafe", "serve_res"]:
        df = pd.read_csv(f"./{f}.csv")
        df = df.iloc[:, 1:]
        df.to_csv(f"upload/{f}.csv")


def split_geo():
    for type_ in ["bar", "cafe", "res"]:
        df = load_place_df(type_)
        df[["latitude", "longitude"]] = df["geometry"].str.split(',', expand=True)
        df = df.drop(columns=['geometry', 'business_status'])
        df.to_csv(f"upload/results_{type_}.csv")


def generate_fake_password(cus_df):
    random.seed(411)
    password = []
    for _ in range(len(cus_df.index)):
        password.append(''.join(random.choice(string.ascii_letters)
                               for _ in range(random.choice(np.arange(1, 14)))))

    df = pd.DataFrame(password, columns=["password"])
    df = df.join(cus_df["user_name"])
    return df

def main():
    cus_df = gen_customer()
    cus_df.to_csv("./customers.csv")
    password_df = generate_fake_password(cus_df)
    password_df.to_csv("./credential.csv")
    food_df = gen_food()
    food_df.to_csv("./food.csv")
    fav_df = gen_favorites(cus_df, food_df)
    fav_df.to_csv("./favorites.csv")

    for type_ in ["bar", "cafe", "res"]:
        place_df = load_place_df(type_)
        serve_df = gen_serve(place_df, food_df)
        serve_df.to_csv(f"./serve_{type_}.csv")
        order_df = gen_orders(cus_df, place_df, food_df)
        order_df.to_csv(f"./order_{type_}.csv")


if __name__ == "__main__":
    main()
    # adjust_id()
    # split_geo()









