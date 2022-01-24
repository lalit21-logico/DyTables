
from pymongo import MongoClient
from bson import ObjectId
import secureCred
from TMS.validate import checkDate
import datetime

client = MongoClient(secureCred.HOST_URL)
db = client['Lalit']


def dateFiltering(table_name, filter_type, column, value):
    col = db[table_name]
    table_data = col.find()
    lis = []

    if checkDate(value):
        day, month, year = value.split('/')
        print(table_data)
        ex_value = datetime.date(int(year), int(month), int(day))
        for x in table_data:
            day, month, year = x[column].split('/')
            temp_value = datetime.date(int(year), int(month), int(day))
            if filter_type == "on":
                if temp_value == ex_value:
                    lis.append(x)
            if filter_type == "after":
                if temp_value > ex_value:
                    lis.append(x)
            if filter_type == "before":
                if temp_value < ex_value:
                    lis.append(x)

    elif value.isnumeric():
        print("here")
        if filter_type in ["more", "exactly", "less"]:
            today = datetime.date.today()
            n_days_ago = today - datetime.timedelta(int(value))
            for x in table_data:
                day, month, year = x[column].split('/')
                temp_value = datetime.date(int(year), int(month), int(day))
                if filter_type == "exactly":
                    if temp_value == n_days_ago:
                        lis.append(x)
                if filter_type == "more":
                    if temp_value > n_days_ago:
                        lis.append(x)
                if filter_type == "less":
                    if temp_value < n_days_ago:
                        lis.append(x)
    return lis


def filtering(table_name, filter_type, column, value):
    col = db[table_name]
    table_data = ""
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

    if filter_type in ["greaterThen", "lessThen"]:
        table_data = col.find()
        lis = []
        for x in table_data:
            if int(x[column]) > int(value) and filter_type == "greaterThen":
                lis.append(x)
            elif int(x[column]) < int(value) and filter_type == "lessThen":
                lis.append(x)
        return lis

    if filter_type in ["more", "exactly", "less", "after", "on", "before"]:
        return dateFiltering(table_name, filter_type, column, value)
    else:
        lis = []
        for x in table_data:
            lis.append(x)

    return lis
