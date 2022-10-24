import config

import datetime
from io import StringIO

import pandas as pd
import requests

from bs4 import BeautifulSoup
from price_parser import Price
from win10toast import ToastNotifier

# PRICE CHECKER TOOL

def timestamped(msg):
    date_format = '%Y-%m-%d %H:%M:%S'
    ts = datetime.datetime.now().strftime(date_format)
    print(ts + " " + msg)


def get_urls(csv_file):
    io = ""
    with open(config.PRODUCT_URL_CSV) as csv:
        io = StringIO(csv.read().replace(';', ','))

    df = pd.read_csv(io)
    return df


def get_response(url):
    response = requests.get(url)
    return response.text


def get_price(html, company):
    soup = BeautifulSoup(html, "lxml")
    element = soup.select_one(config.PRICE_SELECTORS[company])
    price = Price.fromstring(str(element.encode_contents()))
    return price.amount_float


def process_products(df):
    updated_products = []
    for product in df.to_dict("records"):
        html = get_response(product["url"])
        product["price"] = get_price(html, product["company"])
        product["alert"] = product["price"] < product["alert_price"]
        updated_products.append(product)
    return pd.DataFrame(updated_products)


def main():
    # TODO - CHANGE TO EASYGUI OR PANDAS NATIVE DIALOG
    timestamped("PRICE TRACKER")

    timestamped("Fetching URLs for DataFrame...")
    df = get_urls(config.PRODUCT_URL_CSV)
    timestamped("Processing products and updating DataFrame...")
    df_updated = process_products(df)

    timestamped("DataFrame updated!")

    toaster = ToastNotifier()
    offers_available = sum(list(df_updated["alert"]))
    count_offers = sum([int(alert) for alert in list(df_updated["alert"])])

    if offers_available:
        toaster.show_toast("Price checker: New offers available!",
                           f'{count_offers} new offers available for selected products.')

    timestamped("Saving to CSV and XLSX formats...")
    if config.SAVE_TO_CSV:
        df_updated.to_csv(
            config.PRICES_CSV,
            index=False,
            mode="a"
        )

        df_updated.to_excel(
            config.PRICES_XLSX,
            index=False,
            header=True
        )

    timestamped("Success!")


if __name__ == '__main__':
    main()

