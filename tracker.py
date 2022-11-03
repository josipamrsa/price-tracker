# PRICE CHECKER TOOL

import config

import os
import time
import socket
import datetime

from io import StringIO

import pandas as pd
import requests
import easygui

from bs4 import BeautifulSoup
from price_parser import Price
from win10toast import ToastNotifier


def timestamped(msg):
    date_format = '%Y-%m-%d %H:%M:%S'
    ts = datetime.datetime.now().strftime(date_format)
    print(ts + " " + msg)


def get_urls():
    # TODO - args
    # path = easygui.fileopenbox()

    path = cwd = os.getcwd() + "\\PriceCheckFiles\\" + config.PRODUCT_URL_CSV
    io = ""

    with open(path) as csv:
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


def send_notification(df):
    toaster = ToastNotifier()
    offers_available = sum(list(df["alert"]))
    count_offers = sum([int(alert) for alert in list(df["alert"])])

    if offers_available:
        toaster.show_toast("Price checker: New offers available!",
                           f'{count_offers} new offers available for selected products.')


def export_data(df):
    cwd = os.getcwd() + "\\PriceCheckFiles"
    if not os.path.exists(cwd):
        os.mkdir(cwd)

    file_csv = cwd + "\\" + "products_track.csv"
    file_xlsx = cwd + "\\" + "products_track.xlsx"

    if config.SAVE_TO_CSV:
        df.to_csv(
            file_csv,
            index=False,
            mode="a"
        )

        df.to_excel(
            file_xlsx,
            index=False,
            header=True
        )


def check_if_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


def main():
    timestamped("PRICE TRACKER")
    time.sleep(10)

    timestamped("Checking Internet connection...")
    while not check_if_connected():
        timestamped("No internet connection - retrying...")
        time.sleep(30)
    timestamped("Internet connection established - continuing...")

    timestamped("Fetching URLs for DataFrame...")
    df = get_urls()

    timestamped("Processing products and updating DataFrame...")
    df_updated = process_products(df)
    timestamped("DataFrame updated!")

    print(df_updated)

    send_notification(df_updated)

    timestamped("Saving to CSV and XLSX formats...")
    export_data(df_updated)
    timestamped("Success!")


if __name__ == '__main__':
    main()
    input("Press Enter to close...")

