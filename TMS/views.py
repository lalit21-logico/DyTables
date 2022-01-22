from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as log_out
import json
import secureCred
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from TMS.models import *
from TMS.validate import checkValidation
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(secureCred.HOST_URL)
db = client['Lalit']


def home(request):
    return render(request, 'home.html')


@login_required
def deleteRow(request):
    if request.method == 'GET':
        row_id = request.GET['row_id']
        table_name = request.GET['id']
        col = db[table_name]
        msg = ""
        if UserTables.objects.filter(
                table_name=table_name).count() == 1:
            col.delete_one({"_id": ObjectId(row_id), })
            msg1 = "deleted successfully"
            return getTable(request, table_name, msg, msg1)
        msg = "unable to access"
        return getTable(request, table_name, msg)


@login_required
def addData(request):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'POST':
        table_name = request.POST['table_name']
        data = UserTables.objects.filter(
            table_name=table_name,
            user_id=user_id
        )
        data = eval(data[0].table_schema)
        msg = checkValidation(request=request, data=data)
        if "" != msg:
            return getTable(request, table_name, msg)
        row = {}
        primary = ""
        for key, value in data.items():
            if key == "__primary":
                primary = value
                continue
            row[key] = request.POST[key]

        col = db[table_name]
        if col.find({primary: request.POST[primary]}).count() > 0:
            msg = "provide unique value to column :"+primary
            return getTable(request, table_name, msg)

        # inserting doc to  collection
        col.insert_one(row)
        msg1 = "added success"
        return getTable(request, table_name, msg, msg1)


@login_required
def getTable(request, table_name="", msg="", msg1=""):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'GET':
        table_name = request.GET['id']
    else:
        table_name = table_name
    data = UserTables.objects.filter(
        table_name=table_name, user_id=user_id)
    actual_table_name = data[0].actual_table_name
    data = eval(data[0].table_schema)
    lis = []
    col = db[table_name]
    table_data = col.find().sort("_id", -1)
    lis = []
    for x in table_data:
        lis.append(x)

    return render(request, 'tableView.html', {
        'myTables': 'active',
        'data': data,
        'table_name': table_name,
        'actual_table_name': actual_table_name,
        'msg1': msg1,
        'msg': msg,
        'table_data': lis,
    })


@login_required
def myTables(request):
    #collection_name = db["medicinedetails"]
    user_id = request.user.social_auth.get(provider='auth0').uid
    data = UserTables.objects.filter(user_id=user_id).order_by('-id')
    print(data)
    return render(request, 'myTable.html', {
        'data': data,
        'myTables': 'active'
    })


@login_required
def createTable(request):
    # user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'POST':
        columns = int(request.POST['num_column'])
        if columns == 0:
            msg = 'Add At least one column'
            return render(request, 'createTable.html', {
                'msg': msg,
                'createNew': 'active'
            })

        for i in range(1, columns+1):
            if request.POST['primary'] == request.POST['name'+str(i)]:
                break
        else:
            msg = 'primary key name should be a one column name'
            return render(request, 'createTable.html', {
                'msg': msg,
                'createNew': 'active',
            })

        schema = {}
        for i in range(1, columns+1):
            schema[request.POST['name' +
                                str(i)]] = request.POST['type'+str(i)]
        schema['__primary'] = request.POST['primary']

        user_id = request.user.social_auth.get(provider='auth0').uid
        user_email = request.user.social_auth.get(
            provider='auth0').extra_data['email']
        count = UserTables.objects.filter(user_email=user_email).count()
        ref_table_name = user_email+str(count+1)
        UserTables(
            user_id=user_id,
            user_email=user_email,
            table_name=ref_table_name,
            actual_table_name=request.POST['table_name'],
            table_schema=schema
        ).save()

        return myTables(request)
    return render(request, 'createTable.html', {
        'createNew': 'active',
    })


@login_required
def dashboard(request):
    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email'],
    }

    return render(request, 'dashboard.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })


def logout(request):
    log_out(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN,
                  settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)


def home(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'home.html')
