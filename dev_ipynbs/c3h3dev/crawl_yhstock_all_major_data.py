
from pycrawlers.examples.yhstock.crawlers import update_all_stock_major_data

from pymongo import MongoClient
mongo_cli = MongoClient()
update_all_stock_major_data(mongo_cli.yhstock.major,
                            mongo_cli.yhstock.majorError)