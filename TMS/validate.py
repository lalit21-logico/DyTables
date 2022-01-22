import datetime
from ast import Return
import re


email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

date_regex = r'^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$'


def checkDate(value):
    if(re.fullmatch(date_regex, value)):
        day, month, year = value.split('/')
        isValidDate = True
        try:
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            isValidDate = False

        if(isValidDate):
            return True
        else:
            return False
    else:
        return False


def checkString(value):
    if value.isalnum():
        return True
    else:
        return False


def checkEmail(email):
    if(re.fullmatch(email_regex, email)):
        return True

    else:
        return False


def checkBoolean(value):
    if(value == "True" or value == "False"):
        return True
    else:
        return False


def checkNumber(value):
    if value.isnumeric():
        return True
    else:
        return False


def checkValidation(request, data):
    for key, value in data.items():
        msg = ""
        if key == "__primary":
            continue
        elif value == "Number":
            if not checkNumber(request.POST[key]):
                msg = "provide correct numeral value in column "+key
        elif value == "String":
            if not checkString(request.POST[key]):
                msg = "provide correct alphaNumeric  String in column "+key
        elif value == "Boolean":
            if not checkBoolean(request.POST[key]):
                msg = "provide correct Boolean  True or False in column "+key
        elif value == "Email":
            if not checkEmail(request.POST[key]):
                msg = "provide correct Email in column "+key
        elif value == "Datetime":
            if not checkDate(request.POST[key]):
                msg = "provide correct dd/yy/mm format date in column  and should be correct"+key

        if msg != "":
            return msg
    return msg
