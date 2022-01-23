
from pymongo import MongoClient
from bson import ObjectId
import secureCred
client = MongoClient(secureCred.HOST_URL)
db = client['Lalit']


def filtering(table_name, filter_type, column, value):
    col = db[table_name]
    if filter_type in ["isEqual", "True", "False"]:
        if filter_type in ["True", "False"]:
            value = filter_type
        table_data = col.find({column: value}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "isNotEqual":
        table_data = col.find({column: {"$ne": value}}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "contains":
        table_data = col.find({column: {"$regex": ".*"+value+".*"}}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "notContain":
        table_data = col.find({column: {"$ne": {"$regex": ".*"+value+".*"}}}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "startsWith":
        table_data = col.find({column: {"$regex": "^"+value}}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "endsWith":
        table_data = col.find({column: {"$regex": value+"$"}}).collation(
            {'locale': 'en', 'strength': 1}).sort("_id", -1)
    if filter_type == "null":
        table_data = col.find({column: ""}).sort("_id", -1)
    if filter_type == "notNull":
        table_data = col.find({column: {"$ne": ""}}).sort("_id", -1)

    return table_data
