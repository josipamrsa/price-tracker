PRODUCT_URL_CSV = "product_list.csv"
SAVE_TO_CSV = True
PRICES_CSV = "products_track.csv"
PRICES_XLSX = "products_track.xlsx"
SEND_MAIL = True
OFFERS_AVAILABLE = 0

PRICE_SELECTORS = {
    'links' : ".priceDivTableDetails span.pricePart",
    'svijetmedija' : ".product-page-card-price div",
    'zutiklik' : ".product-price span",
    'aviteh' : ".side-price-original",
    'mcomp' : ".price .mainprice",
    'anigota' : ".price .mainprice"
}