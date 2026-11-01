import os

from pymongo import MongoClient


def get_db():
    client = MongoClient("mongodb://root:example@mongo:27017/")
    return client["intranet"]
