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
from TMS.customFilter import filtering
from pymongo import MongoClient
from bson import ObjectId


client = MongoClient(secureCred.HOST_URL)
db = client['Lalit']


def handler404(request, exception):
    return render(request, 'errorPage/404.html', status=404)


def handler500(request):
    return render(request, 'errorPage/404.html', status=500)


def home(request):
    return render(request, 'home.html')


@login_required
def auditHistory(request):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'GET':
        table_name = request.GET['id']
        data = AuditHistory.objects.filter(
            table_id__table_name=table_name, table_id__user_id=user_id).order_by('-id')
        if data.count() <= 0:
            return render(request, 'auditHistory.html', {
                'myTables': 'active',
                'data': data,
                'table_name': " "
            })

        return render(request, 'auditHistory.html', {
            'myTables': 'active',
            'data': data,
            'table_name': data[0].table_id.actual_table_name
        })


@login_required
def filterData(request):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'POST':
        filter_type = request.POST['filter_type']
        column = request.POST['column']
        value = request.POST['value']
        table_name = request.POST['table_name']
        actual_table_name = request.POST['actual_table_name']
    if request.method == 'GET':
        id = request.GET['filter']
        saved_filter = SavedFilter.objects.filter(id=id)
        filter_type = saved_filter[0].filter_type
        column = saved_filter[0].column
        value = saved_filter[0].value
        table_name = saved_filter[0].table_id.table_name
        actual_table_name = saved_filter[0].table_id.actual_table_name
        if user_id != saved_filter[0].table_id.user_id:
            print("invalid access")
            return ""

    data = UserTables.objects.filter(
        table_name=table_name,
        user_id=user_id
    )
    user_tab_obj = data[0]
    data = eval(data[0].table_schema)
    msg = " "+column+" "+filter_type+" "+value
    if filter_type in ["more", "exactly", "less"]:
        msg = " "+column+" "+filter_type+" then "+value+" days ago"
    lis = filtering(table_name, filter_type, column, value)
    saved_filter = SavedFilter.objects.filter(column=column, filter_type=filter_type,
                                              value=value, table_id=user_tab_obj)
    if saved_filter.count() > 0:
        saved_filter.delete()
    SavedFilter(column=column, filter_type=filter_type,
                value=value, table_id=user_tab_obj).save()
    saved_filter = SavedFilter.objects.filter(
        table_id=user_tab_obj).order_by('-id')[:10]
    return render(request, 'tableView.html', {
        'myTables': 'active',
        'data': data,
        'table_name': table_name,
        'actual_table_name': actual_table_name,
        'msg1': msg,
        'table_data': lis,
        'saved_filter': saved_filter
    })


@login_required
def updateRow(request, table_name="", row_id="", msg=""):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'GET':
        row_id = request.GET['row_id']
        table_name = request.GET['id']
    data = UserTables.objects.filter(
        table_name=table_name,
        user_id=user_id
    )
    actual_table_name = data[0].actual_table_name
    data = eval(data[0].table_schema)
    col = db[table_name]
    table_data = col.find({"_id": ObjectId(row_id)})
    lis = []
    for x in table_data:
        lis.append(x)
    return render(request, 'updateRow.html', {
        'myTables': 'active',
        'table_name': table_name,
        'table_data': lis,
        'data': data,
        'row_id': row_id,
        'actual_table_name': actual_table_name,
        'msg': msg
    })


@login_required
def deleteRow(request):
    if request.method == 'GET':
        row_id = request.GET['row_id']
        table_name = request.GET['id']
        col = db[table_name]
        msg = ""
        if UserTables.objects.filter(
                table_name=table_name).count() == 1:
            user_tab_obj = UserTables.objects.filter(
                table_name=table_name)[0]
            row = col.find_one({"_id": ObjectId(row_id), })
            col.delete_one({"_id": ObjectId(row_id), })
            msg1 = "deleted successfully"
            del row['_id']
            AuditHistory(update_type="delete",
                         row_data="Row Deleted "+str(row),
                         table_id=user_tab_obj,
                         ).save()
            return getTable(request, table_name, msg, msg1)
        msg = "unable to access"
        return getTable(request, table_name, msg)


@login_required
def addData(request):
    user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'POST':
        table_name = request.POST['table_name']
        row_id = request.POST['row_id']
        data = UserTables.objects.filter(
            table_name=table_name,
            user_id=user_id
        )
        user_tab_obj = data[0]
        data = eval(data[0].table_schema)
        msg = checkValidation(request=request, data=data)
        if "" != msg:
            if "" != row_id:
                return updateRow(request, table_name, row_id, msg)
            else:
                return getTable(request, table_name, msg)
        row = {}
        primary = ""
        for key, value in data.items():
            if key == "__primary":
                primary = value
                continue
            row[key] = request.POST[key]

        col = db[table_name]

        if "" != row_id:
            actual_row = col.find_one({"_id": ObjectId(row_id), })
            if actual_row[primary] == request.POST[primary]:
                pass
            elif col.find({primary: request.POST[primary]}).count() > 0:
                msg = "provide unique value  another column already having value " + \
                    primary+" : "+request.POST[primary]
                return updateRow(request, table_name, row_id, msg)
        elif col.find({primary: request.POST[primary]}).count() > 0:
            msg = "provide unique value to column :"+primary
            return getTable(request, table_name, msg)

        if request.POST[primary] == "":
            msg = "primary key not be null"
            if "" != row_id:
                return updateRow(request, table_name, row_id, msg)
            else:
                return getTable(request, table_name, msg)

        if "" != row_id:

            col.update_one({"_id": ObjectId(row_id), }, {"$set": row})
            del actual_row['_id']
            AuditHistory(update_type="update",
                         row_data="Row "+str(actual_row) +
                         "upadted by "+str(row),
                         table_id=user_tab_obj,
                         ).save()
            msg1 = "Update success"
        else:
            AuditHistory(update_type="insert",
                         row_data="Row Inserted "+str(row),
                         table_id=user_tab_obj,
                         ).save()
            msg1 = "added success"
            col.insert_one(row)

        # inserting doc to  collection

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
    user_tab_obj = data[0]
    actual_table_name = data[0].actual_table_name
    data = eval(data[0].table_schema)
    col = db[table_name]
    table_data = col.find().sort("_id", -1)
    lis = []
    for x in table_data:
        lis.append(x)

    saved_filter = SavedFilter.objects.filter(
        table_id=user_tab_obj).order_by('-id')[:10]
    return render(request, 'tableView.html', {
        'myTables': 'active',
        'data': data,
        'table_name': table_name,
        'actual_table_name': actual_table_name,
        'msg1': msg1,
        'msg': msg,
        'table_data': lis,
        'saved_filter': saved_filter,
    })


@login_required
def myTables(request):
    # collection_name = db["medicinedetails"]
    user_id = request.user.social_auth.get(provider='auth0').uid
    data = UserTables.objects.filter(user_id=user_id).order_by('-id')
    #print(data)
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

        user_ob = UserTables.objects.filter(
            user_id=user_id,
            user_email=user_email,
            table_name=ref_table_name,
        )
        user_tab_obj = user_ob[0]

        AuditHistory(update_type="creation",
                     row_data="Table created "+request.POST['table_name'],
                     table_id=user_tab_obj
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
